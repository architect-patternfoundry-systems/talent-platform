# Multi-Tenant OIDC Implementation Plan

**Status:** Planning Phase  
**Version:** 1.0  
**Last Updated:** 2026-07-02  
**Scope:** Ecosystem-wide reusable architecture

## Executive Summary

This document outlines a comprehensive approach to implementing OpenID Connect (OIDC) authentication that supports multiple deployment modes and identity providers across all applications in the ecosystem. The architecture is designed to be flexible, secure, and reusable without locking into specific providers or deployment patterns.

## Design Philosophy

### Core Principles

1. **Per-Tenant Configuration:** Each tenant has its own OIDC configuration stored in the database or configuration files
2. **Provider Agnostic:** Core authentication logic is generic; provider-specific quirks live in adapter modules
3. **Multi-Mode Support:** Support hosted SaaS (BYO IdP), hosted SaaS (built-in IdP), and self-hosted deployments
4. **Flexible Tenant Resolution:** Support domain-based, explicit, and hybrid tenant resolution strategies
5. **Code Path Consistency:** Same authentication code path regardless of configuration source (DB vs file)

### Key Architectural Shift

**From:** Global OIDC configuration in environment variables  
**To:** Per-tenant OIDC configuration stored in database or configuration files

## Deployment Modes

### Mode A: Hosted SaaS with Built-in IdP

**Description:** You run a central IdP (e.g., Auth0, Keycloak, or managed service). Each tenant is an "organization" in that IdP.

**Use Case:** Customers who don't want to manage their own IdP

**Tenant Resolution:**
- From a claim (e.g., `org_id`)
- From email domain
- From explicit tenant selection

**Configuration:**
- Global IdP settings in environment variables
- Tenant-specific settings in `tenant_oidc_configs` table
- Provider type: `built-in`

### Mode B: Hosted SaaS with Customer's IdP (BYO IdP)

**Description:** Each tenant connects their own OIDC provider (Okta, Azure AD, Google, etc.)

**Use Case:** Enterprise customers who require SSO with their corporate IdP

**Tenant Resolution:**
- Often via domain or explicit tenant selection
- Token may not always carry internal `tenant_id`

**Configuration:**
- Per-tenant OIDC settings in `tenant_oidc_configs` table
- Provider type: `okta`, `azuread`, `google`, `keycloak`, `generic`

### Mode C: Self-Hosted

**Description:** Customer deploys the application in their environment

**Use Case:** Regulated organizations, air-gapped environments, or those requiring full control

**Sub-modes:**
- **C1:** Use their own IdP (Mode B pattern, customer controls infra)
- **C2:** Run bundled/local IdP (e.g., Keycloak) with your configuration
- **C3:** Disable OIDC and use local users only (small/internal deployments)

**Configuration:**
- Single-tenant configuration file (e.g., `config/tenant.yaml`)
- Optional database-backed multi-tenant for larger self-hosted deployments

## Data Model

### Core Tables

```sql
-- Tenants table
CREATE TABLE tenants (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL, -- for subdomain or URL routing
    domain TEXT, -- optional for domain-based resolution
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tenant OIDC configurations
CREATE TABLE tenant_oidc_configs (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    provider_type TEXT NOT NULL, -- 'generic', 'okta', 'azuread', 'keycloak', 'auth0', 'built-in'
    issuer_url TEXT NOT NULL,
    client_id TEXT NOT NULL,
    client_secret_enc TEXT NOT NULL, -- encrypted at rest
    redirect_uri TEXT NOT NULL,
    audience TEXT,
    scopes TEXT[], -- e.g., ['openid', 'profile', 'email']
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id)
);

-- Attribute mappings (optional, for claim mapping)
CREATE TABLE tenant_oidc_attribute_mappings (
    id TEXT PRIMARY KEY,
    tenant_oidc_config_id TEXT NOT NULL REFERENCES tenant_oidc_configs(id) ON DELETE CASCADE,
    claim_name TEXT NOT NULL, -- e.g., 'email', 'name', 'sub'
    target_field TEXT NOT NULL, -- e.g., 'email', 'name', 'external_id'
    is_required BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Users table
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    external_id TEXT NOT NULL, -- OIDC sub claim
    email TEXT NOT NULL,
    name TEXT,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    idp TEXT NOT NULL DEFAULT 'oidc', -- 'oidc', 'local', 'saml'
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, external_id),
    UNIQUE (tenant_id, email)
);

-- User sessions (optional, for session management)
CREATE TABLE user_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    session_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT
);
```

### Self-Hosted Configuration File

```yaml
# config/tenant.yaml
tenant:
  id: "default"
  name: "Default Organization"
  slug: "default"
  domain: "example.com"

oidc:
  enabled: true
  provider_type: "generic"  # or 'okta', 'azuread', 'keycloak', 'disabled'
  issuer_url: "https://your-idp.example.com"
  client_id: "your-client-id"
  client_secret: "your-client-secret"
  redirect_uri: "https://app.example.com/auth/callback"
  audience: "your-audience"
  scopes:
    - "openid"
    - "profile"
    - "email"
  
  attribute_mappings:
    email: "email"
    name: "name"
    external_id: "sub"

auth:
  tenant_resolution_strategy: "domain"  # 'domain', 'explicit', 'hybrid'
  session_storage: "database"  # 'redis', 'database'
  token_strategy: "jwt"  # 'jwt', 'provider'
```

## Tenant Resolution Strategies

### Strategy 1: Domain-Based Routing

**Flow:**
1. User enters email on login page
2. Extract domain (`@acme.com`)
3. Look up tenant by domain in `tenants` table
4. Load tenant's OIDC configuration
5. Redirect to tenant's configured IdP

**Pros:**
- Simple for users
- Works well when each tenant has distinct email domains

**Cons:**
- Breaks if tenants share domains or have multiple domains
- Requires email input before redirect

**Implementation:**
```python
async def resolve_tenant_by_domain(email: str) -> Optional[Tenant]:
    domain = email.split('@')[1]
    return await get_tenant_by_domain(domain)
```

### Strategy 2: Explicit Tenant Selection

**Flow:**
1. User selects tenant via:
   - Subdomain (`acme.app.example.com`)
   - Path (`/t/acme/...`)
   - Query parameter (`?tenant=acme`)
   - Header (`X-Tenant-Id`)
2. Load tenant's OIDC configuration
3. Redirect to tenant's configured IdP

**Pros:**
- Works even if domains are shared or complex
- Works well for self-hosted single-tenant deployments
- No email input required

**Cons:**
- Slightly more friction for users
- Requires tenant awareness

**Implementation:**
```python
async def resolve_tenant_from_request(request: Request) -> Optional[Tenant]:
    # Try subdomain
    host = request.headers.get('host', '')
    subdomain = host.split('.')[0]
    if subdomain != 'www' and subdomain != 'app':
        return await get_tenant_by_slug(subdomain)
    
    # Try query parameter
    tenant_slug = request.query_params.get('tenant')
    if tenant_slug:
        return await get_tenant_by_slug(tenant_slug)
    
    # Try header
    tenant_id = request.headers.get('X-Tenant-Id')
    if tenant_id:
        return await get_tenant_by_id(tenant_id)
    
    return None
```

### Strategy 3: Hybrid (Recommended)

**Flow:**
1. Primary: Domain-based routing
2. Fallback: Explicit tenant parameter override
3. Default: System default tenant

**Implementation:**
```python
async def resolve_tenant(request: Request, email: Optional[str] = None) -> Tenant:
    # Try explicit first
    tenant = await resolve_tenant_from_request(request)
    if tenant:
        return tenant
    
    # Try domain-based if email provided
    if email:
        tenant = await resolve_tenant_by_domain(email)
        if tenant:
            return tenant
    
    # Return default tenant
    return await get_default_tenant()
```

## Implementation Components

### 1. Tenant Configuration Service

**File:** `src/services/tenant_oidc_config.py`

```python
from typing import Optional
from src.models.tenant import Tenant, TenantOidcConfig

class TenantOidcConfigService:
    async def get_tenant_oidc_config(self, tenant_id: str) -> Optional[TenantOidcConfig]:
        """Load OIDC config from DB or config file"""
        if self.is_self_hosted():
            return self.load_from_config_file()
        return await self.load_from_database(tenant_id)
    
    async def upsert_tenant_oidc_config(
        self, 
        tenant_id: str, 
        config: TenantOidcConfig
    ) -> TenantOidcConfig:
        """Create or update tenant OIDC configuration"""
        # Implementation depends on mode
        pass
    
    async def list_tenant_oidc_configs(self, tenant_id: str) -> list[TenantOidcConfig]:
        """List all OIDC configs for a tenant"""
        pass
```

### 2. Tenant Resolution Middleware

**File:** `src/middleware/tenant_resolution.py`

```python
from fastapi import Request, HTTPException
from src.services.tenant_oidc_config import TenantOidcConfigService

async def tenant_resolution_middleware(request: Request, call_next):
    """Middleware to resolve tenant from request"""
    
    # Resolve tenant using hybrid strategy
    tenant = await resolve_tenant(request)
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Store tenant in request state
    request.state.tenant = tenant
    
    # Load tenant's OIDC config
    oidc_config = await tenant_oidc_config_service.get_tenant_oidc_config(tenant.id)
    request.state.oidc_config = oidc_config
    
    response = await call_next(request)
    return response
```

### 3. OIDC Authentication Flow

**File:** `src/api/oidc.py`

```python
from fastapi import APIRouter, Request, HTTPException
from src.services.oidc_flow import OidcFlowService

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.get("/login")
async def login(request: Request):
    """Initiate OIDC login flow"""
    tenant = request.state.tenant
    oidc_config = request.state.oidc_config
    
    if not oidc_config or not oidc_config.is_active:
        raise HTTPException(status_code=400, detail="OIDC not configured for tenant")
    
    # Build authorization URL using tenant's config
    auth_url = await oidc_flow_service.build_authorization_url(
        tenant_id=tenant.id,
        oidc_config=oidc_config
    )
    
    return {"authorization_url": auth_url}

@router.get("/callback")
async def callback(request: Request):
    """Handle OIDC callback"""
    tenant = request.state.tenant
    oidc_config = request.state.oidc_config
    
    # Exchange code for tokens using tenant's config
    tokens = await oidc_flow_service.exchange_code_for_tokens(
        code=request.query_params.get("code"),
        state=request.query_params.get("state"),
        oidc_config=oidc_config
    )
    
    # Validate tokens against tenant's issuer
    user_info = await oidc_flow_service.validate_and_extract_user_info(
        tokens,
        oidc_config
    )
    
    # Create or update user
    user = await user_service.get_or_create_user(
        tenant_id=tenant.id,
        user_info=user_info
    )
    
    # Generate application JWT
    app_token = await create_application_token(user, tenant)
    
    return {"access_token": app_token, "token_type": "bearer"}
```

### 4. Provider Adapters

**File:** `src/services/oidc/adapters/`

```python
# src/services/oidc/adapters/base.py
class OidcProviderAdapter(ABC):
    @abstractmethod
    async def get_discovery_document(self, issuer_url: str) -> dict:
        pass
    
    @abstractmethod
    async def get_jwks(self, issuer_url: str) -> dict:
        pass
    
    @abstractmethod
    def map_claims_to_user(self, claims: dict, mappings: dict) -> dict:
        pass

# src/services/oidc/adapters/generic.py
class GenericOidcAdapter(OidcProviderAdapter):
    """Standard OIDC provider"""
    pass

# src/services/oidc/adapters/okta.py
class OktaAdapter(OidcProviderAdapter):
    """Okta-specific quirks"""
    pass

# src/services/oidc/adapters/azuread.py
class AzureADAdapter(OidcProviderAdapter):
    """Azure AD-specific quirks"""
    pass
```

### 5. Token Validation Service

**File:** `src/services/token_validation.py`

```python
class TokenValidationService:
    async def validate_id_token(
        self, 
        token: str, 
        oidc_config: TenantOidcConfig
    ) -> dict:
        """Validate ID token against tenant's issuer and JWKS"""
        
        # Fetch JWKS from tenant's issuer
        jwks = await self.fetch_jwks(oidc_config.issuer_url)
        
        # Verify signature
        payload = jwt.decode(
            token,
            key=self.get_jwks_key(jwks, token),
            algorithms=["RS256"],
            audience=oidc_config.audience,
            issuer=oidc_config.issuer_url
        )
        
        return payload
    
    async def fetch_jwks(self, issuer_url: str) -> dict:
        """Fetch JWKS from provider's .well-known endpoint"""
        discovery_url = f"{issuer_url}/.well-known/openid-configuration"
        discovery = await httpx.get(discovery_url)
        jwks_url = discovery.json()["jwks_uri"]
        jwks = await httpx.get(jwks_url)
        return jwks.json()
```

## Configuration Decisions (Per-Tenant)

### 1. Provider Type Selection

**Options:**
- `generic` - Standard OIDC provider
- `okta` - Okta-specific adapter
- `azuread` - Azure AD-specific adapter
- `keycloak` - Keycloak-specific adapter
- `auth0` - Auth0-specific adapter
- `built-in` - Built-in IdP (Mode A)
- `disabled` - No OIDC (local auth only)

**Decision:** Per-tenant configuration in `tenant_oidc_configs.provider_type`

### 2. Attribute Mapping

**Default Mappings:**
```python
DEFAULT_ATTRIBUTE_MAPPINGS = {
    "email": "email",
    "name": "name",
    "external_id": "sub",
    "tenant_id": None  # Set from tenant context
}
```

**Override:** Per-tenant in `tenant_oidc_attribute_mappings` table

### 3. Tenant Resolution Strategy

**Options:**
- `domain` - Email domain-based
- `explicit` - Subdomain/path/header-based
- `hybrid` - Domain with explicit fallback

**Decision:** Per-tenant in `tenants.resolution_strategy` or global default

### 4. Session Storage

**Options:**
- `redis` - Fast, distributed, requires Redis infrastructure
- `database` - Slower, no additional infrastructure
- `memory` - Fastest, not scalable (single-instance only)

**Decision:** Per-tenant or global default in configuration

### 5. Token Strategy

**Options:**
- `jwt` - Generate own JWTs after OIDC (recommended)
- `provider` - Use provider tokens directly
- `hybrid` - Use provider tokens with refresh

**Decision:** Global default with per-tenant override capability

## Security Considerations

### 1. Secret Management

**Requirements:**
- Encrypt `client_secret` at rest in database
- Use Kubernetes secrets for self-hosted config files
- Rotate secrets regularly
- Audit secret access

**Implementation:**
```python
from cryptography.fernet import Fernet

class SecretEncryption:
    def __init__(self, encryption_key: str):
        self.cipher = Fernet(encryption_key)
    
    def encrypt(self, plaintext: str) -> str:
        return self.cipher.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        return self.cipher.decrypt(ciphertext.encode()).decode()
```

### 2. Token Validation

**Requirements:**
- Validate issuer against tenant's configured issuer
- Validate audience against tenant's configured audience
- Verify signature using provider's JWKS
- Check token expiration
- Validate nonce (if used)

### 3. CSRF Protection

**Requirements:**
- Use state parameter with nonce
- Validate state on callback
- Bind state to session/tenant
- Short state expiration (5-10 minutes)

### 4. Rate Limiting

**Requirements:**
- Rate limit `/auth/login` endpoint
- Rate limit `/auth/callback` endpoint
- Implement exponential backoff
- Log suspicious activity

## Implementation Phases

### Phase 1: Foundation (Week 1)

**Goal:** Establish tenant configuration and resolution infrastructure

**Tasks:**
1. Create tenant and user data models
2. Implement tenant OIDC config service
3. Create tenant resolution middleware
4. Add database migrations
5. Implement self-hosted config file loader
6. Add basic tenant management API endpoints

**Deliverables:**
- Tenant data models and migrations
- Tenant resolution middleware
- Tenant OIDC config service
- Self-hosted config file support
- Basic tenant management API

### Phase 2: OIDC Flow (Week 2)

**Goal:** Implement generic OIDC authentication flow

**Tasks:**
1. Implement OIDC discovery document fetching
2. Implement JWKS fetching and caching
3. Build authorization URL generation
4. Implement token exchange
5. Add ID token validation
6. Create user provisioning logic
7. Implement session management
8. Add application JWT generation

**Deliverables:**
- OIDC flow service
- Token validation service
- User provisioning service
- Session management
- `/auth/login` and `/auth/callback` endpoints

### Phase 3: Provider Adapters (Week 3)

**Goal:** Add provider-specific adapters

**Tasks:**
1. Create base adapter interface
2. Implement generic OIDC adapter
3. Implement Okta adapter (if needed)
4. Implement Azure AD adapter (if needed)
5. Implement Keycloak adapter (if needed)
6. Add adapter selection logic
7. Test with multiple providers

**Deliverables:**
- Provider adapter framework
- Generic OIDC adapter
- Specific provider adapters (as needed)
- Adapter selection logic

### Phase 4: Security & Polish (Week 4)

**Goal:** Add security features and polish

**Tasks:**
1. Implement secret encryption
2. Add CSRF protection
3. Implement rate limiting
4. Add comprehensive error handling
5. Implement logging and monitoring
6. Add token refresh flow
7. Implement logout functionality
8. Add security headers

**Deliverables:**
- Secret encryption
- CSRF protection
- Rate limiting
- Comprehensive error handling
- Logging and monitoring
- Token refresh
- Logout functionality

### Phase 5: Testing & Documentation (Week 5)

**Goal:** Comprehensive testing and documentation

**Tasks:**
1. Write unit tests for all components
2. Write integration tests for OIDC flow
3. Test with multiple providers
4. Test tenant resolution strategies
5. Test self-hosted mode
6. Write setup documentation
7. Write provider configuration guides
8. Create troubleshooting guide

**Deliverables:**
- Comprehensive test suite
- Setup documentation
- Provider configuration guides
- Troubleshooting guide

## Configuration Examples

### Example 1: Hosted Multi-Tenant (Mode B)

```sql
-- Tenant: Acme Corp
INSERT INTO tenants (id, name, slug, domain) VALUES
('acme-corp', 'Acme Corporation', 'acme', 'acme.com');

-- OIDC Config: Okta
INSERT INTO tenant_oidc_configs (
    id, tenant_id, provider_type, issuer_url, client_id, 
    client_secret_enc, redirect_uri, audience, is_active
) VALUES (
    'acme-oidc-1', 'acme-corp', 'okta',
    'https://acme.okta.com',
    '0oaxxxxxxxxxxxxx',
    'encrypted_secret_here',
    'https://app.example.com/auth/callback',
    'api://acme-app',
    true
);
```

### Example 2: Self-Hosted Single-Tenant (Mode C1)

```yaml
# config/tenant.yaml
tenant:
  id: "default"
  name: "My Organization"
  slug: "default"
  domain: "myorg.com"

oidc:
  enabled: true
  provider_type: "azuread"
  issuer_url: "https://login.microsoftonline.com/tenant-id/v2.0"
  client_id: "your-client-id"
  client_secret: "your-client-secret"
  redirect_uri: "https://app.myorg.com/auth/callback"
  audience: "api://myorg-app"
  scopes:
    - "openid"
    - "profile"
    - "email"
  
  attribute_mappings:
    email: "email"
    name: "name"
    external_id: "oid"

auth:
  tenant_resolution_strategy: "domain"
  session_storage: "database"
  token_strategy: "jwt"
```

### Example 3: Self-Hosted Local Auth (Mode C3)

```yaml
# config/tenant.yaml
tenant:
  id: "default"
  name: "My Organization"
  slug: "default"

oidc:
  enabled: false
  provider_type: "disabled"

auth:
  tenant_resolution_strategy: "explicit"
  session_storage: "database"
  token_strategy: "jwt"
  local_users_enabled: true
```

## Migration Strategy

### For Existing Applications

1. **Add tenant table** (if not exists)
2. **Migrate existing users** to tenant-based model
3. **Add OIDC config table**
4. **Implement tenant resolution middleware**
5. **Gradually migrate auth endpoints** to new OIDC flow
6. **Maintain backward compatibility** during transition

### For New Applications

1. **Start with tenant-based model** from day one
2. **Implement OIDC from the beginning**
3. **Use self-hosted config file** for initial development
4. **Add database-backed config** when needed for multi-tenant

## Monitoring and Observability

### Key Metrics

1. **Authentication Metrics**
   - Login success rate per tenant
   - Login failure rate per tenant
   - Token validation failures
   - Provider response times

2. **Tenant Metrics**
   - Active tenants
   - Tenant OIDC configuration changes
   - Tenant resolution failures

3. **Security Metrics**
   - Failed authentication attempts
   - Rate limit violations
   - Suspicious activity patterns

### Logging

**Critical Events:**
- Tenant resolution failures
- OIDC configuration changes
- Authentication failures
- Token validation failures
- Provider connectivity issues

**Log Format:**
```json
{
  "timestamp": "2026-07-02T00:00:00Z",
  "level": "INFO",
  "tenant_id": "acme-corp",
  "event": "oidc_login_success",
  "provider_type": "okta",
  "user_id": "user-123",
  "ip_address": "10.0.0.1"
}
```

## Troubleshooting Guide

### Common Issues

#### 1. Tenant Resolution Fails

**Symptoms:** 404 errors on login, "Tenant not found"

**Solutions:**
- Check tenant slug/domain configuration
- Verify tenant resolution strategy
- Check request headers/subdomain
- Review tenant resolution middleware logs

#### 2. OIDC Configuration Invalid

**Symptoms:** 400 errors on login, "OIDC not configured"

**Solutions:**
- Verify OIDC config exists for tenant
- Check `is_active` flag
- Validate issuer URL format
- Check client ID/secret encryption

#### 3. Token Validation Fails

**Symptoms:** 401 errors after callback, "Invalid token"

**Solutions:**
- Verify issuer URL matches token issuer
- Check audience validation
- Validate JWKS fetching
- Check token expiration
- Review clock synchronization

#### 4. Provider Connectivity Issues

**Symptoms:** Timeouts, connection errors

**Solutions:**
- Check network connectivity to provider
- Verify provider URL accessibility
- Check firewall rules
- Review DNS resolution
- Test with curl/wget

## Appendix

### A. OIDC Specification References

- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- [OpenID Connect Discovery 1.0](https://openid.net/specs/openid-connect-discovery-1_0.html)
- [OAuth 2.0 for Browser-Based Apps](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps)

### B. Provider-Specific Documentation

- [Okta OIDC Guide](https://developer.okta.com/docs/guides/implement-oauth-for-okta/)
- [Azure AD OIDC Guide](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-protocols-oidc)
- [Keycloak OIDC Guide](https://www.keycloak.org/documentation.html)
- [Auth0 OIDC Guide](https://auth0.com/docs/authenticate/protocols/oidc)

### C. Security Best Practices

- Use PKCE (Proof Key for Code Exchange)
- Implement state parameter with nonce
- Validate redirect URIs
- Use HTTPS only
- Implement proper session management
- Regular security audits
- Keep dependencies updated

### D. Testing Checklist

- [ ] Test with generic OIDC provider
- [ ] Test with Okta (if applicable)
- [ ] Test with Azure AD (if applicable)
- [ ] Test with Keycloak (if applicable)
- [ ] Test domain-based tenant resolution
- [ ] Test explicit tenant resolution
- [ ] Test hybrid tenant resolution
- [ ] Test self-hosted mode
- [ ] Test database-backed mode
- [ ] Test token validation
- [ ] Test token refresh
- [ ] Test logout functionality
- [ ] Test error handling
- [ ] Test rate limiting
- [ ] Test CSRF protection
- [ ] Test secret encryption

---

**Document Owners:** Architecture Team  
**Review Cycle:** Quarterly  
**Next Review:** 2026-10-01

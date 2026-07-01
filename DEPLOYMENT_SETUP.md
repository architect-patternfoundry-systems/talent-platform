# Talent Platform Deployment Setup

## Overview

This document describes the setup for establishing a permanent development URL for the Talent Platform using the Tailscale pattern, following the same model as other apps in the storyloom ecosystem.

## Development URL

**Permanent Development URL:** `http://talent-platform-dev.tailc2cafc.ts.net`

This URL is accessible via Tailscale and follows the naming convention: `{app-name}-dev.{tailscale-namespace}.ts.net`

## Files Created

### 1. k8s/deploy-infra.yaml
Infrastructure configuration for the talent platform:

- **Namespace:** `talent-platform-dev`
- **Network Policies:**
  - DNS egress
  - HTTPS egress
  - Ingress from Tailscale
  - Intra-namespace traffic
  - Database access (pgbouncer in infra-data namespace)
  - Redis access (if needed)

### 2. k8s/deploy-apps.yaml
Application fleet configuration:

- **Deployment:** `talent-platform-api`
  - Image: `registry-bridge.tailc2cafc.ts.net/talent-platform:latest`
  - Port: 8000
  - Node selector: cortex
  - Init container: wait for database
  - Readiness/liveness probes
  - Environment variables for database, OIDC, etc.

- **Service:** `talent-platform-api`
  - Port: 8000

- **Ingress:** `talent-platform-dev`
  - Host: `talent-platform-dev.tailc2cafc.ts.net`
  - Ingress class: tailscale
  - Routes: /v1, /health, /docs, /redoc, /auth, /

- **PodDisruptionBudget:** `talent-platform-api-pdb`

### 3. Tiltfile
Tilt configuration for local development:

- **Sovereign Mode:** Uses in-cluster pods and Tailscale identities
- **Registry:** `registry-bridge.tailc2cafc.ts.net`
- **Live Updates:** Syncs src/, migrations/, alembic.ini
- **Flux Coma:** Suspends GitOps (optional, not configured yet)
- **UI Buttons:** Run/rollback database migrations

## What Else Needs to Occur

### 1. Create Database

The talent platform needs a PostgreSQL database. Options:

**Option A: Use existing pgbouncer in infra-data**
- Database name: `talent_platform`
- Connection string: `postgresql://cortex_db_admin:XwYcij2BguKzVlEdlsKJu1@pgbouncer.infra-data.svc.cluster.local:5432/talent_platform`
- Create database manually:
  ```bash
  kubectl exec -n infra-data deployment/postgres -- psql -U cortex_db_admin -c "CREATE DATABASE talent_platform;"
  ```

**Option B: Create dedicated PostgreSQL instance**
- Create a new PostgreSQL deployment in talent-platform-dev namespace
- Update deploy-apps.yaml to use the new database

### 2. Configure OIDC Provider

The talent platform uses OIDC for authentication. You need to:

1. **Create an application in your OIDC provider** (Auth0, Keycloak, etc.)
2. **Update environment variables in deploy-apps.yaml:**
   - `OIDC_ISSUER_URL`: Your OIDC provider URL
   - `OIDC_CLIENT_ID`: Your client ID
   - `OIDC_CLIENT_SECRET`: Your client secret
   - `OIDC_AUDIENCE`: Your audience

3. **Alternatively, use the test endpoint** (already implemented in src/api/main.py):
   - `GET /auth/token?tenant_id=test_tenant` - Get test token
   - `GET /auth/tenant` - Verify tenant context

### 3. Run Database Migrations

Apply the database schema:

```bash
# Via Tilt button: "Run Database Migration"
# Or manually:
kubectl exec -n talent-platform-dev deployment/talent-platform-api -- alembic upgrade head
```

### 4. Update Environment Variables

Review and update environment variables in deploy-apps.yaml:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key (change from default)
- `OIDC_*`: OIDC provider configuration
- Other environment variables as needed

### 5. Create Database (if not using existing)

If not using the existing pgbouncer, create a dedicated database:

```bash
# Create namespace (already in deploy-infra.yaml)
kubectl apply -f k8s/deploy-infra.yaml

# Create PostgreSQL deployment (add to deploy-apps.yaml or separate file)
# Then create database:
kubectl exec -n talent-platform-dev deployment/postgres -- psql -U postgres -c "CREATE DATABASE talent_platform;"
```

### 6. Apply Kubernetes Manifests

Apply the infrastructure and application manifests:

```bash
# Apply infrastructure
kubectl apply -f k8s/deploy-infra.yaml

# Apply applications
kubectl apply -f k8s/deploy-apps.yaml
```

### 7. Start Tilt

Start Tilt for local development:

```bash
cd /home/cortex/workspace/storyloom/talent-platform
tilt up
```

### 8. Access the Platform

Once deployed, access the platform at:

- **API:** http://talent-platform-dev.tailc2cafc.ts.net
- **API Documentation:** http://talent-platform-dev.tailc2cafc.ts.net/docs
- **ReDoc:** http://talent-platform-dev.tailc2cafc.ts.net/redoc

### 9. Test Authentication

Test the authentication endpoints:

```bash
# Get test token
curl "http://talent-platform-dev.tailc2cafc.ts.net/auth/token?tenant_id=test_tenant"

# Verify tenant context
curl -H "Authorization: Bearer <token>" http://talent-platform-dev.tailc2cafc.ts.net/auth/tenant
```

### 10. Configure Flux (Optional)

If you want to use Flux for GitOps:

1. **Create Flux configuration** in infrastructure repository
2. **Add talent-platform to Flux kustomization**
3. **Remove Flux Coma from Tiltfile** (or keep it for local development)

## Differences from Storyloom Pattern

The talent platform follows the storyloom pattern with these differences:

1. **Simpler Architecture:** No GPU workers, no synthesis workers, no media storage
2. **Single Service:** Only API service (no web frontend)
3. **Database:** Uses PostgreSQL (same as storyloom)
4. **Authentication:** Uses OIDC (similar to storyloom)
5. **Network Policies:** Simplified (no GPU access, no media storage access)

## Port Registry

The talent platform uses the sovereign port registry:

```python
TILT_PORT = get_sovereign_port('talent-platform')
```

This reserves a unique port for the talent platform in the port registry.

## Sovereign Mode

The talent platform uses Sovereign Mode (ADR-012):

- **In-cluster pods** for development
- **Tailscale identities** for access
- **Registry bridge** for image building
- **Flux coma** for GitOps suspension (optional)

## Next Steps

1. Create database (or use existing pgbouncer)
2. Configure OIDC provider (or use test endpoints)
3. Apply Kubernetes manifests
4. Run database migrations
5. Start Tilt
6. Access platform at http://talent-platform-dev.tailc2cafc.ts.net
7. Test authentication and API endpoints

## Troubleshooting

### Database Connection Failed

- Check pgbouncer is running: `kubectl get pods -n infra-data`
- Check network policy allows database access
- Check connection string in deploy-apps.yaml

### OIDC Authentication Failed

- Check OIDC provider configuration
- Check environment variables in deploy-apps.yaml
- Use test endpoint for development

### Ingress Not Working

- Check Tailscale ingress class is installed
- Check ingress resource is created: `kubectl get ingress -n talent-platform-dev`
- Check network policy allows ingress from Tailscale

### Tilt Not Building

- Check registry bridge is accessible
- Check Dockerfile exists
- Check network='host' is working

## References

- **Storyloom Tiltfile:** /home/cortex/workspace/storyloom/Tiltfile
- **Storyloom deploy-infra.yaml:** /home/cortex/workspace/storyloom/deploy-infra.yaml
- **Storyloom deploy-apps.yaml:** /home/cortex/workspace/storyloom/deploy-apps.yaml
- **ADR-012:** Sovereign Mode documentation
- **Port Registry:** /home/cortex/workspace/infrastructure/globals/tilt/port_registry.tilt

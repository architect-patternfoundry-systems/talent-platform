# Tiltfile for Talent Platform Local Development Ecosystem

# Load environment variables from .env file if present
load('ext://dotenv', 'dotenv')
dotenv()

# Sovereign Port Management
load('../infrastructure/globals/tilt/port_registry.tilt', 'get_sovereign_port')
TILT_PORT = get_sovereign_port('talent-platform')
print("[SOVEREIGN] Reserved Port: " + str(TILT_PORT))

# --- Context Guard (ADR-012) ---
allowed_contexts = ["k3d-local", "rancher-desktop", "docker-desktop", "default"]
allow_k8s_contexts(allowed_contexts)

current = str(local("kubectl config current-context", quiet=True)).strip()
if current not in allowed_contexts:
    fail("\n[CRITICAL] Refusing to run Tilt against context '{}'.\nAllowed contexts: {}\n".format(
        current, allowed_contexts))

# --- Platform Sovereignty Settings (ADR-012) ---
# Sovereign Mode: Uses in-cluster pods and Tailscale identities
SOVEREIGN_MODE = os.environ.get('SOVEREIGN_MODE', 'True').lower() == 'true'

# Canonical Sovereign Host
SOVEREIGN_HOST = 'cortex.tailc2cafc.ts.net'

# Native Cluster Ports
NATIVE_PORTS = {
    'postgres': 5432,
    'api': 8000
}

load('ext://uibutton', 'cmd_button')
load('ext://restart_process', 'docker_build_with_restart')

if SOVEREIGN_MODE:
    print("\n[ADR-012] Substrate Locus Check: SOVEREIGN Mode Active.")
    print("[ADR-012] Targeting In-Cluster Dev Pods via registry-bridge.\n")
    
    # 1. Build and deploy dev substrate
    # Infrastructure (PVC/Namespace) is applied first and remains stable
    k8s_yaml('k8s/deploy-infra.yaml')
    
    # Application fleet is managed by Tilt for iterative development
    k8s_yaml('k8s/deploy-apps.yaml')
    
    # 2. Build and deploy talent-platform-api
    docker_build_with_restart('registry-bridge.tailc2cafc.ts.net/talent-platform', '.', 
                 dockerfile='Dockerfile',
                 entrypoint=['/bin/sh', '-c', 'exec "$@"', '--'],
                 network='host',
                 live_update=[
                     sync('./src', '/app/src'),
                     sync('./migrations', '/app/migrations'),
                     sync('./alembic.ini', '/app/alembic.ini')
                 ])
    
    # --- Flux Coma (Hard Anchor Suspension) ---
    # Suspends the entire GitOps hierarchy to prevent declarative sprawl and whack-a-mole reversion
    # Note: Flux may not be configured for talent-platform yet, so this is optional
    local_resource(
        "flux-coma",
        cmd='''
            echo "🔒 Flux Coma not configured for talent-platform yet"
            echo "✅ Skipping Flux suspension"
        ''',
        serve_cmd='''
            while true; do
                sleep 3600
            done
        ''',
        auto_init=True,
        labels=["Talent-Platform-Watchdog"]
    )

    k8s_resource('talent-platform-api', labels=['Talent-Platform'])

else:
    # Legacy Local Dev Mode
    print("\n[ADR-012] Substrate Locus Check: LOCAL Mode Active.")
    print("[ADR-012] Using docker-compose for local development")
    
    # Use docker-compose for local development
    local_resource(
        'docker-compose-up',
        cmd='docker-compose up -d',
        serve_cmd='docker-compose logs -f',
        auto_init=True,
        labels=['Talent-Platform']
    )

print("\n[ADR-012] Substrate Locus: " + ("SOVEREIGN" if SOVEREIGN_MODE else "LOCAL"))

# UI Buttons
cmd_button('Run Database Migration',
           argv=['kubectl', 'exec', '-n', 'talent-platform-dev', 'deployment/talent-platform-api', '--', 'alembic', 'upgrade', 'head'],
           resource='talent-platform-api',
           icon_name='upgrade',
           text='Run DB Migration')

cmd_button('Rollback Database Migration',
           argv=['kubectl', 'exec', '-n', 'talent-platform-dev', 'deployment/talent-platform-api', '--', 'alembic', 'downgrade', '-1'],
           resource='talent-platform-api',
           icon_name='restore',
           text='Rollback DB Migration')

print("\n[Talent Platform] Development URL: http://talent-platform-dev.tailc2cafc.ts.net")
print("[Talent Platform] API Documentation: http://talent-platform-dev.tailc2cafc.ts.net/docs")

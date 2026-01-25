import os
import sys
import yaml
import traceback
from pathlib import Path
from datetime import datetime

print("=" * 90)
print("🚀 deploy_agent.py starting")
print(f"🕒 Timestamp (UTC): {datetime.utcnow().isoformat()}")
print("=" * 90)

# ------------------------------------------------------------------------------
# Load environment configuration
# ------------------------------------------------------------------------------

ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
REPO_ROOT = Path(__file__).parent
CONFIG_FILE = REPO_ROOT / "config" / f"{ENVIRONMENT}.yaml"

print(f"\n🔧 Loading configuration for environment: {ENVIRONMENT}")
print(f"📄 Config file: {CONFIG_FILE}")

if not CONFIG_FILE.exists():
    raise FileNotFoundError(f"Configuration file not found: {CONFIG_FILE}")

with open(CONFIG_FILE, 'r') as f:
    config = yaml.safe_load(f)

# Extract configuration
PROJECT_ID = config['gcp']['project_id']
LOCATION = config['gcp']['location']
STAGING_BUCKET = config['gcp']['staging_bucket']

AGENT_DISPLAY_NAME = config['agent']['display_name']
AGENT_DESCRIPTION = config['agent']['description']
MIN_INSTANCES = config['agent']['min_instances']
MAX_INSTANCES = config['agent']['max_instances']
CONTAINER_CONCURRENCY = config['agent']['container_concurrency']

# Path configuration
AGENT_SRC_PATH = REPO_ROOT / os.getenv("AGENT_SOURCE_DIR", "agent")
REQUIREMENTS_FILE = os.getenv("REQUIREMENTS_FILE", "agent/requirements.txt")
EXTRA_PACKAGES = os.getenv("EXTRA_PACKAGES", "agent,installation_scripts/install_package.sh").split(",")

print("\n⚙️ Configuration Loaded")
print(f"   - ENVIRONMENT            = {ENVIRONMENT}")
print(f"   - PROJECT_ID             = {PROJECT_ID}")
print(f"   - LOCATION               = {LOCATION}")
print(f"   - STAGING_BUCKET         = {STAGING_BUCKET}")
print(f"   - AGENT_DISPLAY_NAME     = {AGENT_DISPLAY_NAME}")
print(f"   - MIN_INSTANCES          = {MIN_INSTANCES}")
print(f"   - MAX_INSTANCES          = {MAX_INSTANCES}")
print(f"   - CONTAINER_CONCURRENCY  = {CONTAINER_CONCURRENCY}")

# ------------------------------------------------------------------------------
# Path setup
# ------------------------------------------------------------------------------

sys.path.append(str(AGENT_SRC_PATH))

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

try:
    import vertexai
    from vertexai.agent_engines import AgentEngine
    from agent.agent import root_agent
    print("✅ All imports successful")
except Exception as e:
    print("❌ Import failure")
    traceback.print_exc()
    raise

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

def main():
    try:
        print("\n" + "=" * 90)
        print(f"🧩 Deploying to {ENVIRONMENT.upper()} environment")
        print("=" * 90)

        vertexai.init(
            project=PROJECT_ID,
            location=LOCATION,
            staging_bucket=STAGING_BUCKET,
        )
        print("✅ Vertex AI initialized")

        # Validate paths
        requirements_path = REPO_ROOT / REQUIREMENTS_FILE
        if not requirements_path.exists():
            raise FileNotFoundError(f"Requirements not found: {requirements_path}")

        for pkg in EXTRA_PACKAGES:
            pkg_path = REPO_ROOT / pkg.strip()
            if not pkg_path.exists():
                raise FileNotFoundError(f"Extra package not found: {pkg_path}")

        # Deploy agent
        print(f"\n⏳ Creating Agent Engine in {ENVIRONMENT}...")
        
        remote_agent = AgentEngine.create(
            agent_engine=root_agent,
            display_name=AGENT_DISPLAY_NAME,
            description=AGENT_DESCRIPTION,
            requirements=REQUIREMENTS_FILE,
            extra_packages=[pkg.strip() for pkg in EXTRA_PACKAGES],
            build_options={
                "installation_scripts": ["installation_scripts/install_package.sh"],
            },
            min_instances=MIN_INSTANCES,
            max_instances=MAX_INSTANCES,
            container_concurrency=CONTAINER_CONCURRENCY,
        )

        print("\n" + "=" * 90)
        print(f"🎉 Deployment to {ENVIRONMENT.upper()} successful!")
        print("=" * 90)
        print(f"🔖 Resource Name: {remote_agent.resource_name}")

    except Exception as e:
        print("\n" + "=" * 90)
        print(f"🔥 DEPLOYMENT TO {ENVIRONMENT.upper()} FAILED")
        print("=" * 90)
        print(f"❌ Exception: {e}")
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()

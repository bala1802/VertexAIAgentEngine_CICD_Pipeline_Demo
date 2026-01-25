import os
import sys
import traceback
from pathlib import Path
from datetime import datetime

print("=" * 90)
print("🚀 deploy_agent.py starting")
print(f"🕒 Timestamp (UTC): {datetime.utcnow().isoformat()}")
print("=" * 90)

# ------------------------------------------------------------------------------
# Configuration from environment variables
# ------------------------------------------------------------------------------

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "agentops-end-to-end")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")
STAGING_BUCKET = os.getenv("GCP_STAGING_BUCKET", "gs://agentops-end-to-end-agent-staging")

# Agent configuration
AGENT_DISPLAY_NAME = os.getenv("AGENT_DISPLAY_NAME", "content-creation-agent-engine-demo")
AGENT_DESCRIPTION = os.getenv("AGENT_DESCRIPTION", "Simple Content Creation agent using AgentEngine and Queryable.")
MIN_INSTANCES = int(os.getenv("AGENT_MIN_INSTANCES", "0"))
MAX_INSTANCES = int(os.getenv("AGENT_MAX_INSTANCES", "1"))
CONTAINER_CONCURRENCY = int(os.getenv("AGENT_CONTAINER_CONCURRENCY", "1"))

# Path configuration
REPO_ROOT = Path(__file__).parent
AGENT_SRC_PATH = REPO_ROOT / os.getenv("AGENT_SOURCE_DIR", "agent")
REQUIREMENTS_FILE = os.getenv("REQUIREMENTS_FILE", "agent/requirements.txt")
EXTRA_PACKAGES = os.getenv("EXTRA_PACKAGES", "agent,installation_scripts/install_package.sh").split(",")

print("\n⚙️ Configuration")
print(f"   - PROJECT_ID              = {PROJECT_ID}")
print(f"   - LOCATION                = {LOCATION}")
print(f"   - STAGING_BUCKET          = {STAGING_BUCKET}")
print(f"   - AGENT_DISPLAY_NAME      = {AGENT_DISPLAY_NAME}")
print(f"   - MIN_INSTANCES           = {MIN_INSTANCES}")
print(f"   - MAX_INSTANCES           = {MAX_INSTANCES}")
print(f"   - CONTAINER_CONCURRENCY   = {CONTAINER_CONCURRENCY}")
print(f"   - AGENT_SRC_PATH          = {AGENT_SRC_PATH}")
print(f"   - REQUIREMENTS_FILE       = {REQUIREMENTS_FILE}")
print(f"   - EXTRA_PACKAGES          = {EXTRA_PACKAGES}")

# ------------------------------------------------------------------------------
# Path setup
# ------------------------------------------------------------------------------

sys.path.append(str(AGENT_SRC_PATH))
print(f"\n✅ Added to sys.path: {AGENT_SRC_PATH}")

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

try:
    print("\n📦 Importing vertexai...")
    import vertexai
    from vertexai.agent_engines import AgentEngine
    print("✅ vertexai imports successful")

    print("\n📦 Importing agent...")
    from agent.agent import root_agent
    print("✅ agent import successful")

except Exception as e:
    print("❌ Import failure detected")
    traceback.print_exc()
    raise

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

def main():
    try:
        print("\n" + "=" * 90)
        print("🧩 Step 1: Initializing Vertex AI")
        print("=" * 90)

        vertexai.init(
            project=PROJECT_ID,
            location=LOCATION,
            staging_bucket=STAGING_BUCKET,
        )
        print("✅ Vertex AI initialized successfully")

        # ----------------------------------------------------------------------
        print("\n" + "=" * 90)
        print("📦 Step 2: Resolving requirements")
        print("=" * 90)

        requirements_path = REPO_ROOT / REQUIREMENTS_FILE
        print(f"📄 requirements: {requirements_path}")
        print(f"📄 Exists?     : {requirements_path.exists()}")

        if not requirements_path.exists():
            raise FileNotFoundError(f"requirements.txt not found: {requirements_path}")

        # ----------------------------------------------------------------------
        print("\n" + "=" * 90)
        print("📦 Step 3: Validating extra_packages")
        print("=" * 90)

        for pkg in EXTRA_PACKAGES:
            pkg_path = REPO_ROOT / pkg.strip()
            print(f"📁 Extra package: {pkg.strip()}")
            print(f"   - Path  : {pkg_path}")
            print(f"   - Exists: {pkg_path.exists()}")

            if not pkg_path.exists():
                raise FileNotFoundError(f"Extra package not found: {pkg_path}")

        # ----------------------------------------------------------------------
        print("\n" + "=" * 90)
        print("🛠 Step 4: Build options")
        print("=" * 90)

        build_options = {
            "installation_scripts": [
                "installation_scripts/install_package.sh",
            ],
        }

        print("🔧 build_options:")
        for k, v in build_options.items():
            print(f"   - {k}: {v}")

        # ----------------------------------------------------------------------
        print("\n" + "=" * 90)
        print("🤖 Step 5: Creating Agent Engine")
        print("=" * 90)

        print("⏳ Submitting AgentEngine.create(...)")

        remote_agent = AgentEngine.create(
            agent_engine=root_agent,
            display_name=AGENT_DISPLAY_NAME,
            description=AGENT_DESCRIPTION,
            requirements=REQUIREMENTS_FILE,
            extra_packages=EXTRA_PACKAGES,
            build_options=build_options,
            min_instances=MIN_INSTANCES,
            max_instances=MAX_INSTANCES,
            container_concurrency=CONTAINER_CONCURRENCY,
        )

        print("✅ AgentEngine.create() completed successfully")

        # ----------------------------------------------------------------------
        print("\n" + "=" * 90)
        print("📊 Step 6: Agent Output")
        print("=" * 90)

        print("🔖 Resource Name:")
        print(remote_agent.resource_name)

        print("\n🎉 Deployment finished successfully!")

    except Exception as e:
        print("\n" + "=" * 90)
        print("🔥 DEPLOYMENT FAILED")
        print("=" * 90)
        print(f"❌ Exception: {e}")
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()

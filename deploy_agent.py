import sys
import traceback
from pathlib import Path
from datetime import datetime

print("=" * 90)
print("🚀 deploy_agent.py starting")
print(f"🕒 Timestamp (UTC): {datetime.utcnow().isoformat()}")
print("=" * 90)

# ------------------------------------------------------------------------------
# Path setup
# ------------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent
print(f"📁 REPO_ROOT resolved to: {REPO_ROOT}")

USER_SRC_PATH = REPO_ROOT / "agent"
print(f"📁 USER_SRC_PATH resolved to: {USER_SRC_PATH}")

sys.path.append(str(USER_SRC_PATH))
print(f"✅ Added to sys.path: {USER_SRC_PATH}")

print("🔎 Current sys.path:")
for idx, p in enumerate(sys.path):
    print(f"   [{idx}] {p}")

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
# Configuration
# ------------------------------------------------------------------------------

PROJECT_ID = "agentops-end-to-end"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://agentops-end-to-end-agent-staging"

print("\n⚙️ Configuration")
print(f"   - PROJECT_ID     = {PROJECT_ID}")
print(f"   - LOCATION       = {LOCATION}")
print(f"   - STAGING_BUCKET = {STAGING_BUCKET}")

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

def main():
    try:
        print("\n" + "=" * 90)
        print("🧩 Step 1: Initializing Vertex AI")
        print("=" * 90)

        print("➡️ Calling vertexai.init(...)")
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

        requirements = "agent/requirements.txt"
        requirements_path = REPO_ROOT / requirements

        print(f"📄 requirements (string)     : {requirements}")
        print(f"📄 requirements (full path)  : {requirements_path}")
        print(f"📄 Exists?                   : {requirements_path.exists()}")

        if not requirements_path.exists():
            raise FileNotFoundError(f"requirements.txt not found: {requirements_path}")

        # ----------------------------------------------------------------------
        print("\n" + "=" * 90)
        print("📦 Step 3: Validating extra_packages")
        print("=" * 90)

        extra_packages = [
            "agent",                           # your source dir
            "installation_scripts/install_package.sh"
        ]

        for pkg in extra_packages:
            pkg_path = REPO_ROOT / pkg
            print(f"📁 Extra package entry : {pkg}")
            print(f"   - Resolved path     : {pkg_path}")
            print(f"   - Exists?           : {pkg_path.exists()}")

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
        print("   - display_name          : echo-agent-engine-demo")
        print("   - min_instances         : 0")
        print("   - max_instances         : 1")
        print("   - container_concurrency : 1")

        remote_agent = AgentEngine.create(
            agent_engine=root_agent,
            display_name="content-creation-agent-engine-demo",
            description="Simple Content Creation agent using AgentEngine and Queryable.",
            requirements=requirements,
            extra_packages=extra_packages,
            build_options=build_options,
            min_instances=0,
            max_instances=1,
            container_concurrency=1,
        )

        print("✅ AgentEngine.create() completed successfully")

        # ----------------------------------------------------------------------
        print("\n" + "=" * 90)
        print("📊 Step 6: Agent Output")
        print("=" * 90)

        print("🔖 Resource Name:")
        print(remote_agent.resource_name)

        print("\n📋 Full Agent Metadata:")
        print(remote_agent.to_dict())

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
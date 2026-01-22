"""Deployment script for ADK agent to Vertex AI Agent Engine."""

import argparse
import sys
import os
from pathlib import Path

import vertexai
from vertexai import agent_engines


def deploy_agent(
    project_id: str,
    location: str,
    agent_name: str,
    staging_bucket: str | None = None,
) -> agent_engines.AgentEngine:
    """Deploy ADK agent to Vertex AI Agent Engine."""

    print("🚀 Deploying ADK Agent")
    print(f"   Project: {project_id}")
    print(f"   Location: {location}")
    print(f"   Agent Name: {agent_name}")

    # Initialize Vertex AI (staging_bucket is required for AgentEngine.create) [page:1]
    init_kwargs: dict[str, str] = {"project": project_id, "location": location}
    if staging_bucket:
        init_kwargs["staging_bucket"] = staging_bucket
    vertexai.init(**init_kwargs)

    # Add repository root to Python path
    repo_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(repo_root))

    print("\n📥 Importing agent...")
    print(f"   Repo root: {repo_root}")

    # Import root agent from agent module
    from agent.agent import root_agent

    print(f"   ✅ Agent imported: {root_agent}")

    # Prepare requirements for AgentEngine.create:
    # Per docs, this can be a path to requirements.txt OR a list of lines. [page:1]
    requirements_file = repo_root / "requirements.txt"
    requirements: str | list[str] | None = None

    if requirements_file.exists():
        print(f"\n📦 Using requirements from: {requirements_file}")
        # Pass the file path directly so the library reads it remotely if desired. [page:1]
        requirements = str(requirements_file)
    else:
        print(f"   ⚠️  No requirements.txt found at {requirements_file}")

    # Optionally set a GCS subdir name for staging artifacts. [page:1]
    gcs_dir_name = f"agent-engines/{agent_name}"

    print("\n📦 Creating Agent Engine instance...")
    try:
        agent_engine = agent_engines.AgentEngine.create(
            agent_engine=root_agent,
            display_name=agent_name,
            description=f"ADK Agent deployed via CI/CD ({agent_name})",
            requirements=requirements,
            gcs_dir_name=gcs_dir_name,
            # extra_packages, env_vars, build_options, etc. can be added as needed. [page:1]
        )

        print("\n✅ Deployment successful!")
        print(f"   Resource: {agent_engine.resource_name}")
        print(f"   Display Name: {agent_engine.display_name}")

        return agent_engine
    except Exception as e:
        print(f"\n❌ Agent Engine creation failed: {str(e)}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Deploy ADK agent to Vertex AI Agent Engine"
    )
    parser.add_argument("--project-id", required=True, help="GCP Project ID")
    parser.add_argument("--location", default="us-central1", help="Agent location")
    parser.add_argument("--agent-name", required=True, help="Agent display name")
    parser.add_argument(
        "--staging-bucket",
        help="GCS staging bucket (must start with gs:// for Agent Engine)",
    )

    args = parser.parse_args()

    try:
        deploy_agent(
            project_id=args.project_id,
            location=args.location,
            agent_name=args.agent_name,
            staging_bucket=args.staging_bucket,
        )
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
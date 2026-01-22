"""Deployment script for ADK agent to Vertex AI Agent Engine."""

import argparse
import sys
import os
from pathlib import Path
import vertexai
from vertexai import agent_engines

def deploy_agent(project_id: str, location: str, agent_name: str,
                 staging_bucket: str = None):
    """Deploy ADK agent to Vertex AI Agent Engine."""
    
    print(f"🚀 Deploying ADK Agent")
    print(f"   Project: {project_id}")
    print(f"   Location: {location}")
    print(f"   Agent Name: {agent_name}")
    
    # Initialize Vertex AI
    vertexai.init(project=project_id, location=location)
    
    # Add repository root to Python path
    repo_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(repo_root))
    
    print(f"\n📥 Importing agent...")
    print(f"   Repo root: {repo_root}")
    
    # Import root agent from agent module
    from agent.agent import root_agent
    
    print(f"   ✅ Agent imported: {root_agent}")
    
    # Read requirements from repo root
    requirements_file = repo_root / "requirements.txt"
    requirements = None
    if requirements_file.exists():
        print(f"\n📦 Loading requirements from: {requirements_file}")
        with open(requirements_file) as f:
            requirements = [line.strip() for line in f if line.strip()
                          and not line.startswith("#")]
        print(f"   Found {len(requirements)} requirements")
    else:
        print(f"   ⚠️  No requirements.txt found at {requirements_file}")
    
    # Create agent engine instance
    print(f"\n📦 Creating Agent Engine instance...")
    try:
        agent_engine = agent_engines.AgentEngine.create(
            source_code=root_agent,
            display_name=agent_name,
            description=f"ADK Agent deployed via CI/CD ({agent_name})",
            requirements=requirements,
            agent_framework="google-adk",
            location=location
        )
        
        print(f"\n✅ Deployment successful!")
        print(f"   Resource: {agent_engine.resource_name}")
        print(f"   Display Name: {agent_engine.display_name}")
        
        return agent_engine
    except Exception as e:
        print(f"\n❌ Agent Engine creation failed: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy ADK agent to Agent Engine")
    parser.add_argument("--project-id", required=True, help="GCP Project ID")
    parser.add_argument("--location", default="us-central1", help="Agent location")
    parser.add_argument("--agent-name", required=True, help="Agent display name")
    parser.add_argument("--staging-bucket", help="GCS staging bucket")
    
    args = parser.parse_args()
    
    try:
        deploy_agent(
            project_id=args.project_id,
            location=args.location,
            agent_name=args.agent_name,
            staging_bucket=args.staging_bucket
        )
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

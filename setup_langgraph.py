#!/usr/bin/env python3
"""
Setup script for LangGraph PropertyTek implementation
"""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def main():
    """Main setup function"""
    print("🚀 Setting up LangGraph PropertyTek Implementation")
    print("=" * 60)
    
    # Check if we're in a conda environment
    if 'CONDA_DEFAULT_ENV' in os.environ:
        print(f"📦 Using conda environment: {os.environ['CONDA_DEFAULT_ENV']}")
    else:
        print("⚠️  No conda environment detected. Consider activating your chatbot environment.")
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    # Test the workflow
    if not run_command("python test_langgraph_workflow.py", "Testing LangGraph workflow"):
        print("⚠️  Workflow test failed, but continuing with setup...")
    
    print("\n" + "=" * 60)
    print("🎉 Setup completed!")
    print("\nTo run the server:")
    print("  python run_server.py")
    print("\nOr:")
    print("  python src/main.py")
    print("\nAPI will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")


if __name__ == "__main__":
    main()
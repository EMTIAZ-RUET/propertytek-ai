#!/usr/bin/env python3
"""
Install dependencies for LangGraph PropertyTek implementation
"""

import subprocess
import sys
import os


def run_pip_install(packages, description):
    """Install packages with pip"""
    print(f"🔄 {description}...")
    try:
        cmd = [sys.executable, "-m", "pip", "install"] + packages
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def main():
    """Install dependencies in the correct order"""
    print("🚀 Installing LangGraph PropertyTek Dependencies")
    print("=" * 60)
    
    # Check if we're in a conda environment
    if 'CONDA_DEFAULT_ENV' in os.environ:
        print(f"📦 Using conda environment: {os.environ['CONDA_DEFAULT_ENV']}")
    else:
        print("⚠️  No conda environment detected. Consider activating your chatbot environment.")
    
    # Install core dependencies first
    core_packages = [
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "pydantic==2.5.0",
        "python-dotenv==1.0.0",
        "aiofiles==23.2.1",
        "python-multipart==0.0.6",
        "requests==2.31.0",
        "python-dateutil==2.8.2"
    ]
    
    if not run_pip_install(core_packages, "Installing core dependencies"):
        return False
    
    # Install OpenAI
    if not run_pip_install(["openai==1.3.0"], "Installing OpenAI"):
        return False
    
    # Install external service dependencies
    external_packages = [
        "twilio==8.10.0",
        "google-api-python-client==2.149.0",
        "google-auth-httplib2==0.2.0",
        "google-auth-oauthlib==1.2.1"
    ]
    
    if not run_pip_install(external_packages, "Installing external service dependencies"):
        return False
    
    # Install LangGraph and LangChain (latest compatible versions)
    langchain_packages = [
        "langchain-core",
        "langchain-openai", 
        "langgraph"
    ]
    
    if not run_pip_install(langchain_packages, "Installing LangGraph and LangChain"):
        print("⚠️  LangGraph installation failed. Continuing without it...")
        print("📝 You can install manually later with: pip install langgraph langchain-core langchain-openai")
    
    print("\n" + "=" * 60)
    print("🎉 Dependency installation completed!")
    print("\n📝 Next steps:")
    print("1. Configure your .env file with API keys")
    print("2. Test the basic structure: python test_basic_structure.py")
    print("3. Run the server: python run_server.py")
    print("\n🔧 If LangGraph installation failed, you can:")
    print("- Try: pip install --upgrade pip")
    print("- Then: pip install langgraph langchain-core langchain-openai")


if __name__ == "__main__":
    main()
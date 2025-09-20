#!/usr/bin/env python3
"""
Install LangGraph dependencies with proper conflict resolution
"""

import subprocess
import sys
import os


def run_pip_command(command, description):
    """Run pip command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        if e.stderr:
            print(f"   Error: {e.stderr.strip()}")
        return False


def main():
    """Install dependencies with conflict resolution"""
    print("🚀 Installing LangGraph PropertyTek Dependencies")
    print("=" * 60)
    
    # Check if we're in a conda environment
    if 'CONDA_DEFAULT_ENV' in os.environ:
        print(f"📦 Using conda environment: {os.environ['CONDA_DEFAULT_ENV']}")
    else:
        print("⚠️  No conda environment detected. Consider activating your chatbot environment.")
    
    print("\n🔧 Resolving dependency conflicts...")
    
    # Step 1: Upgrade pip first
    if not run_pip_command("python -m pip install --upgrade pip", "Upgrading pip"):
        print("⚠️  Pip upgrade failed, continuing anyway...")
    
    # Step 2: Install core dependencies without version conflicts
    core_deps = [
        "python-dotenv",
        "requests", 
        "python-dateutil",
        "twilio"
    ]
    
    for dep in core_deps:
        if not run_pip_command(f"pip install {dep}", f"Installing {dep}"):
            print(f"⚠️  {dep} installation failed, continuing...")
    
    # Step 3: Install compatible pydantic version first
    if not run_pip_command("pip install 'pydantic>=2.7.4'", "Installing compatible Pydantic"):
        print("❌ Pydantic installation failed")
        return False
    
    # Step 4: Install FastAPI with compatible pydantic
    if not run_pip_command("pip install 'fastapi>=0.104.1'", "Installing FastAPI"):
        print("❌ FastAPI installation failed")
        return False
    
    # Step 5: Install uvicorn
    if not run_pip_command("pip install 'uvicorn>=0.24.0'", "Installing Uvicorn"):
        print("❌ Uvicorn installation failed")
        return False
    
    # Step 6: Install OpenAI
    if not run_pip_command("pip install 'openai>=1.3.0'", "Installing OpenAI"):
        print("❌ OpenAI installation failed")
        return False
    
    # Step 7: Install Google dependencies
    google_deps = [
        "google-api-python-client",
        "google-auth-httplib2", 
        "google-auth-oauthlib"
    ]
    
    for dep in google_deps:
        if not run_pip_command(f"pip install {dep}", f"Installing {dep}"):
            print(f"⚠️  {dep} installation failed, continuing...")
    
    # Step 8: Install LangGraph and LangChain (most likely to have conflicts)
    print("\n🧠 Installing LangGraph and LangChain...")
    langchain_success = True
    
    if not run_pip_command("pip install langchain-core", "Installing LangChain Core"):
        print("⚠️  LangChain Core installation failed")
        langchain_success = False
    
    if not run_pip_command("pip install langchain-openai", "Installing LangChain OpenAI"):
        print("⚠️  LangChain OpenAI installation failed")
        langchain_success = False
    
    if not run_pip_command("pip install langgraph", "Installing LangGraph"):
        print("⚠️  LangGraph installation failed")
        langchain_success = False
    
    # Step 9: Verify installations
    print("\n🔍 Verifying installations...")
    
    test_imports = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("openai", "OpenAI"),
        ("twilio.rest", "Twilio"),
        ("googleapiclient.discovery", "Google API Client")
    ]
    
    if langchain_success:
        test_imports.extend([
            ("langchain_core", "LangChain Core"),
            ("langchain_openai", "LangChain OpenAI"),
            ("langgraph", "LangGraph")
        ])
    
    import_results = {}
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"✅ {name} imported successfully")
            import_results[name] = True
        except ImportError as e:
            print(f"❌ {name} import failed: {e}")
            import_results[name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Installation Summary:")
    print("-" * 30)
    
    successful = sum(import_results.values())
    total = len(import_results)
    
    for name, success in import_results.items():
        status = "✅ OK" if success else "❌ FAIL"
        print(f"{name:<20} {status}")
    
    print("-" * 30)
    print(f"Total: {successful}/{total} packages working")
    
    if successful == total:
        print("\n🎉 All dependencies installed successfully!")
        print("🚀 You can now run: python run_server.py")
    elif successful >= total - 3:  # Allow up to 3 failures (likely LangGraph related)
        print(f"\n✅ Core dependencies installed ({successful}/{total})")
        if not langchain_success:
            print("⚠️  LangGraph installation had issues, but core functionality should work")
            print("💡 You can try installing LangGraph manually later:")
            print("   pip install --upgrade pip")
            print("   pip install langgraph langchain-core langchain-openai")
        print("🚀 You can try running: python run_server.py")
    else:
        print(f"\n❌ Too many installation failures ({total - successful}/{total})")
        print("💡 Try these troubleshooting steps:")
        print("1. Update pip: python -m pip install --upgrade pip")
        print("2. Clear pip cache: pip cache purge")
        print("3. Install packages one by one manually")
        print("4. Check your Python version (requires 3.8+)")


if __name__ == "__main__":
    main()
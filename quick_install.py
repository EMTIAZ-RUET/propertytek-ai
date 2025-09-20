#!/usr/bin/env python3
"""
Quick installation script for PropertyTek dependencies
"""

import subprocess
import sys

def install_package(package):
    """Install a single package"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Quick install essential packages"""
    print("🚀 Quick Install for PropertyTek")
    print("=" * 40)
    
    # Essential packages in order
    packages = [
        "python-dotenv",
        "requests", 
        "fastapi",
        "uvicorn",
        "openai",
        "twilio",
        "google-api-python-client"
    ]
    
    print("📦 Installing essential packages...")
    for package in packages:
        print(f"Installing {package}...")
        if install_package(package):
            print(f"✅ {package} installed")
        else:
            print(f"❌ {package} failed")
    
    print("\n🧪 Testing imports...")
    test_results = {}
    
    imports_to_test = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"), 
        ("openai", "OpenAI"),
        ("twilio.rest", "Twilio"),
        ("googleapiclient.discovery", "Google API")
    ]
    
    for module, name in imports_to_test:
        try:
            __import__(module)
            print(f"✅ {name}")
            test_results[name] = True
        except ImportError:
            print(f"❌ {name}")
            test_results[name] = False
    
    successful = sum(test_results.values())
    total = len(test_results)
    
    print(f"\n📊 Result: {successful}/{total} packages working")
    
    if successful >= 4:  # At least core packages work
        print("✅ Core functionality should work!")
        print("🚀 Try running: python run_server.py")
    else:
        print("❌ Too many failures. Check your Python environment.")

if __name__ == "__main__":
    main()
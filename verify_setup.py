#!/usr/bin/env python3
"""
Deadlift AI Backend - Setup Verification Script
Tests that all components are properly installed and configured
"""

import sys
import importlib
from pathlib import Path


def check_python_version():
    """Check Python version is 3.8+"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor} (need 3.8+)")
        return False


def check_dependencies():
    """Check all required packages are installed"""
    print("\n🔍 Checking dependencies...")
    
    required_packages = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'mediapipe': 'MediaPipe',
        'cv2': 'OpenCV',
        'PIL': 'Pillow',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'sklearn': 'scikit-learn',
        'requests': 'Requests'
    }
    
    all_installed = True
    for package, name in required_packages.items():
        try:
            importlib.import_module(package)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name} (not installed)")
            all_installed = False
    
    return all_installed


def check_files():
    """Check all required files exist"""
    print("\n🔍 Checking required files...")
    
    required_files = {
        'api.py': 'Flask API server',
        'client.py': 'Python client library',
        'landmarks.py': 'Landmark definitions',
        'deadlift.pkl': 'ML model',
        'index.html': 'Web dashboard',
        'requirements.txt': 'Dependencies file'
    }
    
    project_dir = Path(__file__).parent
    all_exist = True
    
    for filename, description in required_files.items():
        filepath = project_dir / filename
        if filepath.exists():
            print(f"   ✅ {filename}")
        else:
            print(f"   ❌ {filename} - {description} (missing)")
            all_exist = False
    
    return all_exist


def check_model():
    """Check if model file is valid"""
    print("\n🔍 Checking ML model...")
    
    import pickle
    
    model_path = Path(__file__).parent / 'deadlift.pkl'
    
    if not model_path.exists():
        print(f"   ❌ Model file not found at {model_path}")
        return False
    
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        print(f"   ✅ Model loaded successfully")
        print(f"   ℹ️  Model type: {type(model).__name__}")
        return True
    except Exception as e:
        print(f"   ❌ Error loading model: {e}")
        return False


def check_api_structure():
    """Check if API file has correct structure"""
    print("\n🔍 Checking API structure...")
    
    api_file = Path(__file__).parent / 'api.py'
    
    required_endpoints = [
        '/health',
        '/detect',
        '/stream',
        '/status',
        '/reset'
    ]
    
    try:
        with open(api_file, 'r') as f:
            content = f.read()
        
        all_found = True
        for endpoint in required_endpoints:
            if endpoint in content:
                print(f"   ✅ Endpoint {endpoint}")
            else:
                print(f"   ❌ Endpoint {endpoint} (not found)")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"   ❌ Error reading API file: {e}")
        return False


def check_ports():
    """Check if port 5000 is available"""
    print("\n🔍 Checking port availability...")
    
    import socket
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 5000))
        sock.close()
        
        if result == 0:
            print("   ⚠️  Port 5000 is in use (API already running?)")
            return True  # Not necessarily a problem
        else:
            print("   ✅ Port 5000 is available")
            return True
    except Exception as e:
        print(f"   ⚠️  Could not check port: {e}")
        return True


def print_summary(results):
    """Print summary of checks"""
    print("\n" + "="*50)
    print("📊 VERIFICATION SUMMARY")
    print("="*50)
    
    all_passed = all(results.values())
    
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check_name}")
    
    print("="*50)
    
    if all_passed:
        print("🎉 All checks passed! Your setup is ready.")
        print("\n🚀 To start the API:")
        print("   python api.py")
        print("\n📊 Then open your browser:")
        print("   http://localhost:5000")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\n💡 Tips:")
        print("   - Install missing packages: pip install -r requirements.txt")
        print("   - Ensure deadlift.pkl is in the project directory")
        print("   - Check that all files are present")
        return 1


def main():
    """Run all verification checks"""
    print("="*50)
    print("🔧 DEADLIFT AI - SETUP VERIFICATION")
    print("="*50)
    
    checks = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies(),
        'Required Files': check_files(),
        'ML Model': check_model(),
        'API Structure': check_api_structure(),
        'Port Availability': check_ports()
    }
    
    exit_code = print_summary(checks)
    
    print("\n📖 For more information:")
    print("   - Quick Start: QUICKSTART.md")
    print("   - Full Docs: BACKEND_README.md")
    print("   - Setup Summary: SETUP_SUMMARY.md")
    
    return exit_code


if __name__ == '__main__':
    sys.exit(main())

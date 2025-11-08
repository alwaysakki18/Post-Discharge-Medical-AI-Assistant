"""
Verification script to check if the system is properly set up.
Run this before starting the application.
"""

import sys
from pathlib import Path
import json

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def check_file(file_path, description):
    """Check if a file exists."""
    if Path(file_path).exists():
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - NOT FOUND")
        return False

def check_directory(dir_path, description):
    """Check if a directory exists."""
    if Path(dir_path).exists():
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - NOT FOUND")
        return False

def check_env_file():
    """Check if .env file exists and has required keys."""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        print("   → Copy .env.example to .env and add your API keys")
        return False
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    has_openai = "OPENAI_API_KEY" in content and "sk-" in content
    
    if has_openai:
        print("✅ .env file exists with OpenAI API key")
        return True
    else:
        print("⚠️  .env file exists but OpenAI API key not configured")
        print("   → Add your OpenAI API key to .env file")
        return False

def check_patient_data():
    """Check patient data file."""
    patient_file = Path("data/patient_reports.json")
    if not patient_file.exists():
        print("❌ Patient data file not found")
        return False
    
    try:
        with open(patient_file, 'r') as f:
            data = json.load(f)
        
        if len(data) >= 25:
            print(f"✅ Patient data file exists with {len(data)} patients")
            return True
        else:
            print(f"⚠️  Patient data file has only {len(data)} patients (need 25+)")
            return False
    except Exception as e:
        print(f"❌ Error reading patient data: {e}")
        return False

def check_reference_material():
    """Check nephrology reference material."""
    ref_file = Path("data/nephrology_reference.txt")
    if not ref_file.exists():
        print("❌ Nephrology reference file not found")
        return False
    
    try:
        with open(ref_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if len(content) > 10000:  # Should be substantial
            print(f"✅ Nephrology reference file exists ({len(content)} characters)")
            return True
        else:
            print("⚠️  Nephrology reference file seems too small")
            return False
    except Exception as e:
        print(f"❌ Error reading reference file: {e}")
        return False

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"✅ Python version {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python version {version.major}.{version.minor}.{version.micro} (need 3.9+)")
        return False

def check_dependencies():
    """Check if key dependencies are installed."""
    dependencies = [
        ("fastapi", "FastAPI"),
        ("streamlit", "Streamlit"),
        ("langchain", "LangChain"),
        ("langgraph", "LangGraph"),
        ("chromadb", "ChromaDB"),
        ("openai", "OpenAI"),
        ("sqlalchemy", "SQLAlchemy"),
    ]
    
    all_installed = True
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✅ {name} installed")
        except ImportError:
            print(f"❌ {name} NOT installed")
            all_installed = False
    
    return all_installed

def main():
    """Run all verification checks."""
    print_header("Post Discharge Medical AI Assistant")
    print_header("System Verification")
    
    all_checks = []
    
    # Check Python version
    print_header("Python Environment")
    all_checks.append(check_python_version())
    
    # Check dependencies
    print_header("Dependencies")
    all_checks.append(check_dependencies())
    
    # Check project structure
    print_header("Project Structure")
    all_checks.append(check_directory("backend", "Backend directory"))
    all_checks.append(check_directory("frontend", "Frontend directory"))
    all_checks.append(check_directory("data", "Data directory"))
    all_checks.append(check_directory("scripts", "Scripts directory"))
    all_checks.append(check_directory("docs", "Documentation directory"))
    
    # Check key files
    print_header("Key Files")
    all_checks.append(check_file("requirements.txt", "Requirements file"))
    all_checks.append(check_file("README.md", "README file"))
    all_checks.append(check_file("backend/main.py", "Backend main file"))
    all_checks.append(check_file("frontend/app.py", "Frontend app file"))
    
    # Check configuration
    print_header("Configuration")
    all_checks.append(check_env_file())
    
    # Check data files
    print_header("Data Files")
    all_checks.append(check_patient_data())
    all_checks.append(check_reference_material())
    
    # Check setup scripts
    print_header("Setup Scripts")
    all_checks.append(check_file("scripts/setup_database.py", "Database setup script"))
    all_checks.append(check_file("scripts/setup_vector_db.py", "Vector DB setup script"))
    
    # Summary
    print_header("Verification Summary")
    passed = sum(all_checks)
    total = len(all_checks)
    
    print(f"\nPassed: {passed}/{total} checks")
    
    if passed == total:
        print("\n🎉 All checks passed! Your system is ready.")
        print("\nNext steps:")
        print("1. Run: python scripts/setup_database.py")
        print("2. Run: python scripts/setup_vector_db.py")
        print("3. Start backend: cd backend && uvicorn main:app --reload")
        print("4. Start frontend: cd frontend && streamlit run app.py")
    else:
        print(f"\n⚠️  {total - passed} check(s) failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Create .env file: copy .env.example .env")
        print("- Add OpenAI API key to .env file")
    
    print("\n" + "=" * 60 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

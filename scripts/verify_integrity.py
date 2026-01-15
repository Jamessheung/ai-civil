import os
import sys
import importlib.util

def check_file(path):
    if os.path.exists(path):
        print(f"✅ Found: {path}")
        return True
    else:
        print(f"❌ Missing: {path}")
        return False

def check_python_syntax(path):
    try:
        with open(path, 'r') as f:
            compile(f.read(), path, 'exec')
        print(f"✅ Syntax OK: {path}")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax Error in {path}: {e}")
        return False

REQUIRED_FILES = [
    "docker-compose.yml",
    "database/schema.sql",
    "database/patch_v1_1_1.sql",
    "backend/main.py",
    "backend/database.py",
    "backend/models/__init__.py",
    "backend/services/ingestor.py",
    "backend/services/evidence_extractor.py",
    "backend/services/clusterer.py",
    "backend/services/scorer.py",
    "backend/services/heartbeat.py",
    "backend/routes/clusters.py",
    "frontend/package.json",
    "frontend/app/page.tsx"
]

def main():
    print("=== AI Civilization Project Integrity Check ===")
    base_dir = os.getcwd()
    if 'ai文明' not in base_dir:
        # Adjustment for absolute path if needed, or assume running from project root
        project_root = "/Users/james/Desktop/ai文明"
        if os.path.exists(project_root):
             os.chdir(project_root)
        else:
             print("Warning: Could not find project root, checking relative...")

    all_ok = True
    for f in REQUIRED_FILES:
        if not check_file(f):
            all_ok = False
        elif f.endswith(".py"):
            if not check_python_syntax(f):
                all_ok = False
    
    if all_ok:
        print("\n🎉 Integrity Check Passed! Project structure is valid.")
        print("Next Step: Run 'docker-compose up -d' to start the database.")
    else:
        print("\n⚠️ Integrity Check Failed. See errors above.")

if __name__ == "__main__":
    main()

import os
import sys
from sqlalchemy import text

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.database import SessionLocal

def apply_patch():
    print("🛠 Applying Database Patch (Add Summary)...")
    try:
        db = SessionLocal()
        with open("../database/patch_add_summary.sql", "r") as f:
            sql = f.read()
            db.execute(text(sql))
            db.commit()
            print("   ✅ Patch executed successfully.")
    except Exception as e:
        print(f"   ❌ Patch failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    apply_patch()

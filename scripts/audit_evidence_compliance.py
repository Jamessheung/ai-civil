
import os
import sys
import json
from collections import Counter
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.supa_client import get_supabase

def audit_compliance():
    print("🛡️  Starting Evidence Compliance Audit (P0 Check)...")
    supa = get_supabase()
    res = supa.table("evidence").select("evidence_id, level, pointer, extract").execute()
    
    total = 0
    compliant = 0
    non_compliant = 0
    
    issues = Counter()
    
    for item in res.data:
        level = item['level']
        pointer = item['pointer'] or {}
        
        # Only audit L4 and L5 according to user spec
        if level >= 4:
            total += 1
            is_valid = True
            
            # Rule 1: Locator
            has_locator = 'selector' in pointer or 'match_text' in pointer or 'page' in pointer
            if not has_locator:
                issues['Missing Locator (P0.2)'] += 1
                is_valid = False
                
            # Rule 2: Anti-Drift
            if 'captured_at' not in pointer:
                issues['Missing Captured At (P0.3)'] += 1
                is_valid = False
            if 'source_hash' not in pointer:
                issues['Missing Source Hash (P0.3)'] += 1
                is_valid = False
                
            # Rule 3: URL
            if 'url' not in pointer or not pointer['url'].startswith('http'):
                 issues['Invalid URL (P0.1)'] += 1
                 is_valid = False
            
            if is_valid:
                compliant += 1
            else:
                non_compliant += 1
                # Print sample failure
                if non_compliant <= 3:
                     print(f"   [FAIL L{level}] ID {item['evidence_id']}: {json.dumps(pointer)}")

    print("\n📊 Compliance Report")
    print(f"   Total High-Level Evidence (L4/L5): {total}")
    print(f"   ✅ Compliant: {compliant} ({compliant/total*100:.1f}%)" if total else "   ✅ Compliant: 0")
    print(f"   ❌ Non-Compliant: {non_compliant}")
    
    if issues:
        print("\n   ⚠️  Violation Breakdown:")
        for rule, count in issues.items():
            print(f"      - {rule}: {count}")

if __name__ == "__main__":
    audit_compliance()

import json
import os

def load_json(filename):
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return []
    try:
        with open(filename, 'r') as f:
            content = f.read()
            if not content: return []
            return json.loads(content)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return []

leaves = load_json('leaves_dump.json')
students = load_json('students_dump.json')
advisors = load_json('advisors_dump.json')

print(f"Loaded {len(leaves)} leaves, {len(students)} students, {len(advisors)} advisors.")

print("\n--- Unique Department Codes ---")
sf_depts = set(s.get('dept') for s in students)
lf_depts = set(l.get('dept') for l in leaves)
af_depts = set(a.get('dept') for a in advisors)

print(f"Student Depts: {sf_depts}")
print(f"Leave Depts:   {lf_depts}")
print(f"Advisor Depts: {af_depts}")

print("\n--- Mismatch Analysis ---")
# Check if Leaves match Advisors
for dept in lf_depts:
    if dept not in af_depts:
        print(f"CRITICAL: Leaves exist for Dept '{dept}' but NO Advisor exists for that Dept.")
    else:
        print(f"OK: Leaves for '{dept}' have a matching Advisor.")

# Check for specific "Pending" leaves
pending = [l for l in leaves if l.get('status') == 'Pending']
print(f"\nTotal Pending Leaves: {len(pending)}")
for l in pending:
    print(f"  - Pending: {l.get('regNo')} ({l.get('dept')}) -> Advisor Match? {l.get('dept') in af_depts}")

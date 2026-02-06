import json
import os

def load(f):
    if os.path.exists(f): 
        return json.load(open(f))
    return []

students = load('students_dump.json')
leaves = load('leaves_v2.json')

print(f"Students: {len(students)}")
print(f"Leaves: {len(leaves)}")

s_depts = set(x.get('dept') for x in students)
l_depts = set(x.get('dept') for x in leaves)

print(f"Student Depts: {s_depts}")
print(f"Leave Depts: {l_depts}")

print("--- Pending Leaves ---")
for l in leaves:
    if l.get('status') == 'Pending':
        print(f"Pending: Reg={l.get('regNo')} Dept='{l.get('dept')}'")

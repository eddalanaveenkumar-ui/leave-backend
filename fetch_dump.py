import requests
import json

BASE_URL = 'https://leave-backend-24w1.onrender.com/api'

def fetch_and_save(endpoint, filename):
    try:
        print(f"Fetching {endpoint}...")
        resp = requests.get(f"{BASE_URL}/{endpoint}")
        if resp.status_code == 200:
            with open(filename, 'w') as f:
                json.dump(resp.json(), f, indent=2)
            print(f"Saved {filename}")
        else:
            print(f"Failed {endpoint}: {resp.status_code}")
    except Exception as e:
        print(f"Error {endpoint}: {e}")

fetch_and_save('leaves', 'leaves_dump.json')
fetch_and_save('students', 'students_dump.json')
fetch_and_save('advisors', 'advisors_dump.json')

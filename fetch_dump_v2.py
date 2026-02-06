import requests
import json

BASE_URL = 'https://leave-backend-24w1.onrender.com/api'

def fetch(endpoint, filename):
    print(f"Fetching {endpoint}...")
    try:
        r = requests.get(f"{BASE_URL}/{endpoint}")
        if r.status_code == 200:
            with open(filename, 'w') as f:
                json.dump(r.json(), f, indent=2)
            print(f"Saved {filename}")
        else:
            print(f"Error {endpoint}: {r.status_code}")
    except Exception as e:
        print(f"Ex: {e}")

fetch('leaves', 'leaves_v2.json')
# We know /students works
# /advisors likely doesn't exist.

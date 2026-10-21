import os
import json
import hashlib
from datetime import datetime

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def hash_string(s):
    return hashlib.sha256(s.encode()).hexdigest()

def today():
    return datetime.now().strftime("%Y-%m-%d")
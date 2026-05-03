import json
import os
import hashlib
from datetime import datetime

FILE_PATH = "error_memory.json"


def load_memory():
    if not os.path.exists(FILE_PATH):
        return {}
    try:
        with open(FILE_PATH, "r") as f:
            return json.load(f)
    except:
        return {}


def save_memory(data):
    with open(FILE_PATH, "w") as f:
        json.dump(data, f, indent=2)


# 🔥 ONLY USE ERROR TYPE FOR STABLE GROUPING
def generate_key(error_type):
    base = error_type.lower().strip()
    return hashlib.md5(base.encode()).hexdigest()[:10]


def update_error_group(error_type, root_cause):
    data = load_memory()

    key = generate_key(error_type)

    if key not in data:
        data[key] = {
            "error_type": error_type,
            "root_cause": root_cause,
            "count": 1,
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "issue_url": None
        }
    else:
        data[key]["count"] += 1
        data[key]["last_seen"] = datetime.now().isoformat()

    save_memory(data)
    return key, data[key]


def attach_issue(key, issue_url):
    data = load_memory()
    if key in data:
        data[key]["issue_url"] = issue_url
        save_memory(data)


def get_error_group(key):
    return load_memory().get(key, {})


def get_top_errors(limit=10):
    data = load_memory()
    return sorted(data.items(), key=lambda x: x[1]["count"], reverse=True)[:limit]
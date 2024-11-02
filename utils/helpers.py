import requests
import os

def check_server_status(url):
    try:
        response = requests.get(url, timeout=10)
        return (True, "Server is up and running") if response.status_code == 200 else (False, "Server is down")
    except requests.RequestException:
        return False, "Server is not reachable"

def load_last_guid():
    if os.path.exists("data/last_guid.txt"):
        with open("data/last_guid.txt") as f:
            return f.read().strip()
    return None

def save_last_guid(guid):
    with open("data/last_guid.txt", "w") as f:
        f.write(guid)

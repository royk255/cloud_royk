import json
import os

DB_FILE = "users.json"

def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f)

def user_exists(username):
    users = load_users()
    return username in users

def add_user(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = {"password": password}
    save_users(users)
    return True

def check_login(username, password):
    users = load_users()
    return users.get(username, {}).get("password") == password

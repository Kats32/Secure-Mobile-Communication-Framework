import json
from crypto_utils import hash_password


USER_FILE = "users.json"


def load_users():

    with open(USER_FILE, "r") as file:
        return json.load(file)


def save_users(users):

    with open(USER_FILE, "w") as file:
        json.dump(users, file, indent=4)


def register(username, password):

    users = load_users()

    if username in users:
        return False

    users[username] = hash_password(password)

    save_users(users)

    return True


def authenticate(username, password):

    users = load_users()

    if username not in users:
        return False

    return users[username] == hash_password(password)
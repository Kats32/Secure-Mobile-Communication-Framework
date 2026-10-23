import binascii
import hashlib
import hmac
import json
import os


USER_FILE = "users.json"


def load_users():

    try:
        with open(USER_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_users(users):

    with open(USER_FILE, "w") as file:
        json.dump(users, file, indent=4)


def register(username, password):

    users = load_users()

    if username in users:
        return False

    salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        100000,
    )
    users[username] = {
        "salt": binascii.hexlify(salt).decode(),
        "password_hash": binascii.hexlify(password_hash).decode(),
    }

    save_users(users)

    return True


def authenticate(username, password):

    users = load_users()

    user_data = users.get(username)
    if not isinstance(user_data, dict):
        return False

    try:
        salt = binascii.unhexlify(user_data["salt"])
        expected_hash = binascii.unhexlify(user_data["password_hash"])
    except (KeyError, TypeError, binascii.Error):
        return False

    candidate_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        100000,
    )
    return hmac.compare_digest(candidate_hash, expected_hash)

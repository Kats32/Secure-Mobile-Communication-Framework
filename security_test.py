"""Run focused, isolated checks for the project's auth and crypto helpers."""

from pathlib import Path
import sys
import tempfile

import auth
from crypto_utils import (
    decrypt_message,
    derive_shared_key,
    encrypt_message,
    generate_ec_keypair,
    generate_rsa_keypair,
    sign_message,
    verify_signature,
)
from replay_protection import is_replay


def check(name, operation, results):
    try:
        passed = bool(operation())
    except Exception as error:
        passed = False
        print(f"[ERROR] {name}: {type(error).__name__}: {error}")
    results.append(passed)
    print(f"[{'PASS' if passed else 'FAIL'}] {name}")


def check_authentication():
    original_user_file = auth.USER_FILE
    try:
        with tempfile.TemporaryDirectory(prefix="smcf-auth-test-") as temp_dir:
            auth.USER_FILE = str(Path(temp_dir) / "users.json")
            username = "test-user"
            password = "temporary-test-password"
            registered = auth.register(username, password)
            valid_login = auth.authenticate(username, password)
            invalid_login = auth.authenticate(username, "wrong-password")
            return registered and valid_login and not invalid_login
    finally:
        auth.USER_FILE = original_user_file


def main():
    results = []
    print("=" * 52)
    print(" SECURE COMMUNICATION CHECKS")
    print("=" * 52)

    check("PBKDF2 registration, valid login, and wrong-password rejection",
          check_authentication, results)

    keys = {}

    def ecdh_agreement():
        client_private, client_public = generate_ec_keypair()
        server_private, server_public = generate_ec_keypair()
        keys["client"] = derive_shared_key(client_private, server_public)
        keys["server"] = derive_shared_key(server_private, client_public)
        return keys["client"] == keys["server"]

    check("ECDH shared-key agreement", ecdh_agreement, results)

    message_state = {}

    def aes_round_trip():
        message_state["message"] = "Secure Mobile Communication"
        message_state["nonce"], message_state["ciphertext"] = encrypt_message(
            keys["client"], message_state["message"]
        )
        plaintext = decrypt_message(
            keys["server"], message_state["nonce"], message_state["ciphertext"]
        )
        return plaintext == message_state["message"]

    check("AES-GCM encrypt/decrypt round trip", aes_round_trip, results)

    def reject_tampered_ciphertext():
        changed = bytearray(message_state["ciphertext"])
        changed[0] ^= 1
        try:
            decrypt_message(keys["server"], message_state["nonce"], bytes(changed))
        except Exception:
            return True
        return False

    check("AES-GCM rejects modified ciphertext", reject_tampered_ciphertext, results)
    check("Replay counter rejects duplicate and older values",
          lambda: is_replay(5, 5) and is_replay(4, 5), results)
    check("Replay counter accepts a newer value",
          lambda: not is_replay(6, 5), results)

    rsa_state = {}

    def verify_valid_signature():
        rsa_state["private"], rsa_state["public"] = generate_rsa_keypair()
        rsa_state["message"] = b"Secure Mobile Communication"
        rsa_state["signature"] = sign_message(
            rsa_state["private"], rsa_state["message"]
        )
        return verify_signature(
            rsa_state["public"], rsa_state["message"], rsa_state["signature"]
        )

    check("RSA-PSS accepts a valid signature", verify_valid_signature, results)
    check("RSA-PSS rejects a modified message",
          lambda: not verify_signature(
              rsa_state["public"], b"Modified message", rsa_state["signature"]
          ), results)

    passed = sum(results)
    print("=" * 52)
    print(f"RESULT: {passed}/{len(results)} checks passed")
    print("=" * 52)
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())

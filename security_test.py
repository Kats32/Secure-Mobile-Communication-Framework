from auth import authenticate
from crypto_utils import (
    generate_ec_keypair,
    derive_shared_key,
    encrypt_message,
    decrypt_message,
    generate_rsa_keypair,
    sign_message,
    verify_signature
)


def print_result(test_name, passed):
    if passed:
        print(f"[PASS] {test_name}")
    else:
        print(f"[FAIL] {test_name}")


print("=" * 50)
print("     SECURE COMMUNICATION SECURITY TEST")
print("=" * 50)


# 1. Authentication Test

print("\n1. Authentication Test")

username = "Kavya Amrutha"
password = "munni#123"

try:
    result = authenticate(username, password)

    print_result(
        "User Authentication",
        result
    )

except Exception as e:
    print_result(
        "User Authentication",
        False
    )
    print("Error:", e)


# 2. ECDH Key Exchange Test

print("\n2. ECDH Key Exchange Test")

try:
    client_private, client_public = generate_ec_keypair()
    server_private, server_public = generate_ec_keypair()

    client_shared_key = derive_shared_key(
        client_private,
        server_public
    )

    server_shared_key = derive_shared_key(
        server_private,
        client_public
    )

    result = client_shared_key == server_shared_key

    print_result(
        "ECDH Shared Key Agreement",
        result
    )

except Exception as e:
    print_result(
        "ECDH Shared Key Agreement",
        False
    )
    print("Error:", e)


# 3. AES-GCM Encryption Test

print("\n3. AES-GCM Encryption Test")

try:
    message = "Secure Mobile Communication"

    nonce, ciphertext = encrypt_message(
        client_shared_key,
        message
    )

    decrypted_message = decrypt_message(
        server_shared_key,
        nonce,
        ciphertext
    )

    result = decrypted_message == message

    print_result(
        "AES-GCM Encryption and Decryption",
        result
    )

except Exception as e:
    print_result(
        "AES-GCM Encryption and Decryption",
        False
    )
    print("Error:", e)


# 4. Tampering Detection Test

print("\n4. Tampering Detection Test")

try:
    tampered_data = bytearray(ciphertext)

    tampered_data[0] ^= 1

    tampered_ciphertext = bytes(tampered_data)

    try:
        decrypt_message(
            server_shared_key,
            nonce,
            tampered_ciphertext
        )

        tampering_detected = False

    except Exception:
        tampering_detected = True

    print_result(
        "Modified Ciphertext Rejected",
        tampering_detected
    )

except Exception as e:
    print_result(
        "Modified Ciphertext Rejected",
        False
    )
    print("Error:", e)


# 5. Replay Attack Detection Test

print("\n5. Replay Attack Detection Test")

try:
    last_counter = 1
    received_counter = 2

    replay_detected = received_counter <= last_counter

    print_result(
        "Repeated Counter Detected",
        replay_detected
    )

except Exception as e:
    print_result(
        "Repeated Counter Detected",
        False
    )
    print("Error:", e)


# 6. RSA Digital Signature Test

print("\n6. RSA Digital Signature Test")

try:
    rsa_private_key, rsa_public_key = generate_rsa_keypair()

    message = b"Secure Mobile Communication"

    signature = sign_message(
        rsa_private_key,
        message
    )

    valid_signature = verify_signature(
        rsa_public_key,
        message,
        signature
    )

    print_result(
        "RSA Signature Verification",
        valid_signature
    )

except Exception as e:
    print_result(
        "RSA Signature Verification",
        False
    )
    print("Error:", e)


# 7. Modified Message Signature Test

print("\n7. Modified Message Signature Test")

try:
    modified_message = b"Modified Communication"

    invalid_signature = verify_signature(
        rsa_public_key,
        modified_message,
        signature
    )

    print_result(
        "Modified Message Rejected",
        not invalid_signature
    )

except Exception as e:
    print_result(
        "Modified Message Rejected",
        False
    )
    print("Error:", e)


# Final Summary

print("\n" + "=" * 50)
print("          SECURITY EVALUATION COMPLETE")
print("=" * 50)

print("\nSecurity mechanisms tested:")
print("1. User Authentication")
print("2. ECDH Key Exchange")
print("3. AES-GCM Encryption")
print("4. Tampering Detection")
print("5. Replay Detection")
print("6. RSA Digital Signature")
print("7. Modified Message Detection")

print("\n" + "=" * 50)
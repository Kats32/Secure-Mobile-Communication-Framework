import socket
import json

from auth import authenticate
from crypto_utils import (
    generate_ec_keypair,
    serialize_ec_public_key,
    load_ec_public_key,
    derive_shared_key,
    decrypt_message,
    verify_signature
)

from cryptography.hazmat.primitives import serialization

HOST = "127.0.0.1"
PORT = 5000

last_counter = 0

server_ec_private, server_ec_public = generate_ec_keypair()


def receive_json(connection):
    data = b""

    while b"\n" not in data:
        chunk = connection.recv(4096)

        if not chunk:
            break

        data += chunk

    message = data.split(b"\n", 1)[0]

    return json.loads(message.decode())


def send_json(connection, data):
    connection.send(
        (json.dumps(data) + "\n").encode()
    )


def start_server():

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server.bind((HOST, PORT))
    server.listen(5)

    print("Secure Mobile Communication Server")
    print("Listening on port", PORT)

    while True:

        connection, address = server.accept()

        print("\nConnection from:", address)

        handle_client(connection)


def handle_client(connection):

    global last_counter

    try:

        
        # 1. Authentication

        request = receive_json(connection)

        username = request["username"]
        password = request["password"]

        if not authenticate(username, password):

            send_json(
                connection,
                {
                    "status": "AUTH_FAILED"
                }
            )

            connection.close()

            return

        print("User authenticated:", username)

        
        # 2. Send ECDH public key

        server_public_key = serialize_ec_public_key(
            server_ec_public
        ).decode()

        send_json(
            connection,
            {
                "status": "AUTH_SUCCESS",
                "server_public_key": server_public_key
            }
        )

        
        # 3. Receive client keys

        request = receive_json(connection)

        client_public_key = load_ec_public_key(
            request["client_public_key"].encode()
        )

        client_rsa_public_key = serialization.load_pem_public_key(
            request["client_rsa_public_key"].encode()
        )

        
        # 4. ECDH

        session_key = derive_shared_key(
            server_ec_private,
            client_public_key
        )

        print("ECDH key exchange completed")
        print("Session key established")

        print("Client RSA public key received")

       
        # 5. Receive encrypted message

        message = receive_json(connection)

        counter = message["counter"]

        nonce_hex = message["nonce"]
        ciphertext_hex = message["ciphertext"]
        signature_hex = message["signature"]

       
        # 6. RSA Signature Verification

        signed_data = (
            f"{counter}|{nonce_hex}|{ciphertext_hex}"
        ).encode()

        signature = bytes.fromhex(signature_hex)

        signature_valid = verify_signature(
            client_rsa_public_key,
            signed_data,
            signature
        )

        if not signature_valid:

            print("RSA signature verification failed")

            send_json(
                connection,
                {
                    "status": "SIGNATURE_INVALID"
                }
            )

            return

        print("RSA digital signature verified")

        
        # 7. Replay Detection

        print("Received counter:", counter)

        if counter <= last_counter:

            print("REPLAY ATTACK DETECTED")
            print("Message rejected")

            send_json(
                connection,
                {
                    "status": "REPLAY_ATTACK_DETECTED"
                }
            )

            return

        last_counter = counter


        # 8. AES-GCM Decryption

        nonce = bytes.fromhex(nonce_hex)

        ciphertext = bytes.fromhex(ciphertext_hex)

        plaintext = decrypt_message(
            session_key,
            nonce,
            ciphertext
        )

        print("Decrypted message:", plaintext)


        # 9. Success

        send_json(
            connection,
            {
                "status": "MESSAGE_ACCEPTED",
                "message": plaintext
            }
        )

    except Exception as e:

        print("Security error:", type(e).__name__)

        try:

            send_json(
                connection,
                {
                    "status": "MESSAGE_REJECTED",
                    "error": type(e).__name__
                }
            )

        except:

            pass

    finally:

        connection.close()


if __name__ == "__main__":

    start_server()
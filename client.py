import socket
import json

from cryptography.hazmat.primitives import serialization

from crypto_utils import (
    generate_ec_keypair,
    load_ec_public_key,
    derive_shared_key,
    encrypt_message,
    generate_rsa_keypair,
    sign_message
)

from attacks import (
    eavesdropping_demo,
    tampering_demo,
    replay_demo
)

HOST = "127.0.0.1"
PORT = 5000
last_packet = None


def receive_json(client):

    data = b""

    while b"\n" not in data:

        chunk = client.recv(4096)

        if not chunk:
            break

        data += chunk

    message = data.split(b"\n", 1)[0]

    return json.loads(message.decode())


def send_message(counter, tamper=False, username=None, password=None, message=None):

    if username is None:
        username = input("Username: ")

    if password is None:
        password = input("Password: ")

    if message is None:
        message = input("Enter message: ")

    
    # Generate ECDH key pair

    client_ec_private, client_ec_public = generate_ec_keypair()

    
    # Generate RSA key pair

    client_rsa_private, client_rsa_public = generate_rsa_keypair()

    client = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    client.connect((HOST, PORT))


    # Authentication

    login_request = {
        "username": username,
        "password": password
    }

    client.send(
        (json.dumps(login_request) + "\n").encode()
    )

    response = receive_json(client)

    if response["status"] != "AUTH_SUCCESS":

        print("Authentication failed")

        client.close()

        return

    print("Authentication successful")


    # Receive server ECDH key

    server_public_key = load_ec_public_key(
        response["server_public_key"].encode()
    )

    shared_key = derive_shared_key(
        client_ec_private,
        server_public_key
    )

    print("ECDH key exchange completed")


    # Serialize client ECDH key

    client_public_key = client_ec_public.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    
    # Serialize client RSA key

    client_rsa_public_key = client_rsa_public.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    
    # Send public keys

    key_request = {

        "client_public_key":
            client_public_key.decode(),

        "client_rsa_public_key":
            client_rsa_public_key.decode()
    }

    client.send(
        (json.dumps(key_request) + "\n").encode()
    )

    
    # AES-GCM Encryption

    nonce, ciphertext = encrypt_message(
        shared_key,
        message
    )

    encrypted_message = {
        "counter": counter,
        "nonce": nonce.hex(),
        "ciphertext": ciphertext.hex()
    }

    global last_packet
    last_packet = encrypted_message.copy()

    print("\nOriginal message:")
    print(message)

    print("\nOriginal ciphertext:")
    print(encrypted_message["ciphertext"])

    
    # Tampering simulation

    if tamper:

        ciphertext_data = bytearray.fromhex(
            encrypted_message["ciphertext"]
        )

        ciphertext_data[0] ^= 1

        encrypted_message["ciphertext"] = (
            bytes(ciphertext_data).hex()
        )

        print("\nTampering attack performed!")

        print("\nCiphertext before tampering:")
        print(ciphertext.hex())

        print("\nCiphertext after tampering:")
        print(encrypted_message["ciphertext"])

    
    # RSA Digital Signature

    signed_data = (

        f"{encrypted_message['counter']}|"
        f"{encrypted_message['nonce']}|"
        f"{encrypted_message['ciphertext']}"

    ).encode()

    signature = sign_message(
        client_rsa_private,
        signed_data
    )

    encrypted_message["signature"] = signature.hex()
    last_packet = encrypted_message.copy()  

    print("\nRSA digital signature generated")

    
    # Send encrypted message

    client.send(
        (json.dumps(encrypted_message) + "\n").encode()
    )

    response = receive_json(client)

    print("\nServer response:")
    print(response)
    
    client.close()

    return encrypted_message


def replay_attack():

    username = input("Username: ")
    password = input("Password: ")

    message = input("Enter message: ")

    
    # Generate keys

    client_ec_private, client_ec_public = generate_ec_keypair()

    client_rsa_private, client_rsa_public = generate_rsa_keypair()

    client = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    client.connect((HOST, PORT))

    
    # Authentication

    login_request = {

        "username": username,
        "password": password
    }

    client.send(
        (json.dumps(login_request) + "\n").encode()
    )

    response = receive_json(client)

    if response["status"] != "AUTH_SUCCESS":

        print("Authentication failed")

        client.close()

        return

    print("Authentication successful")

    
    # ECDH

    server_public_key = load_ec_public_key(
        response["server_public_key"].encode()
    )

    shared_key = derive_shared_key(
        client_ec_private,
        server_public_key
    )

    print("ECDH key exchange completed")

    
    # Public keys

    client_public_key = client_ec_public.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    client_rsa_public_key = client_rsa_public.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    key_request = {

        "client_public_key":
            client_public_key.decode(),

        "client_rsa_public_key":
            client_rsa_public_key.decode()
    }

    client.send(
        (json.dumps(key_request) + "\n").encode()
    )


    # Encrypt message

    nonce, ciphertext = encrypt_message(
        shared_key,
        message
    )

    counter = 1

    signed_data = (

        f"{counter}|"
        f"{nonce.hex()}|"
        f"{ciphertext.hex()}"

    ).encode()

    signature = sign_message(
        client_rsa_private,
        signed_data
    )

    encrypted_message = {

        "counter": counter,

        "nonce": nonce.hex(),

        "ciphertext": ciphertext.hex(),

        "signature": signature.hex()
    }

    print("\nReplay attack message prepared.")
    print("Counter:", counter)

    client.send(
        (json.dumps(encrypted_message) + "\n").encode()
    )

    response = receive_json(client)

    print("\nServer response:")
    print(response)

    client.close()

def run_eavesdropping():
    if last_packet is None:
        return {
            "status": "ERROR",
            "details": "No encrypted packet available."
        }

    return eavesdropping_demo(last_packet)


def run_tampering():
    if last_packet is None:
        return {
            "status": "ERROR",
            "details": "No encrypted packet available."
        }

    return tampering_demo(last_packet)


def run_replay():
    if last_packet is None:
        return {
            "status": "ERROR",
            "details": "No encrypted packet available."
        }

    return replay_demo(last_packet)

def create_secure_packet(username, password, message):

    return send_message(
        counter=1,
        username=username,
        password=password,
        message=message
    )

if __name__ == "__main__":

    print("\n1. Normal Communication")
    print("2. Eavesdropping Demo")
    print("3. Tampering Attack")
    print("4. Replay Attack")

    choice = input("\nSelect option: ")

    if choice == "1":

        send_message(
            counter=1
        )

    elif choice == "2":

        send_message(
            counter=1
        )

    elif choice == "3":

        send_message(
            counter=2,
            tamper=True
        )

    elif choice == "4":

        replay_attack()

    else:

        print("Invalid choice")
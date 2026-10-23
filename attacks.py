"""Attack demonstrations that use the normal authenticated TCP handshake."""

import json
import socket

from cryptography.hazmat.primitives import serialization

from crypto_utils import derive_shared_key, generate_ec_keypair, serialize_ec_public_key


HOST = "127.0.0.1"
PORT = 5000
PACKET_FIELDS = ("counter", "nonce", "ciphertext", "signature")


def _wire_packet(packet):
    return {field: packet[field] for field in PACKET_FIELDS if field in packet}


def send_packet(packet, username, password):
    """Authenticate, complete key setup, and submit a previously captured packet."""
    client_private, client_public = generate_ec_keypair()
    client_rsa_public = packet.get("_client_rsa_public_key")
    if not client_rsa_public:
        return {"status": "SIMULATION_FAILED", "reason": "Missing signing key context"}

    try:
        with socket.create_connection((HOST, PORT), timeout=10) as client:
            client.settimeout(10)
            client.sendall((json.dumps({
                "username": username,
                "password": password,
            }) + "\n").encode())
            response = _receive_json(client)
            if response.get("status") != "AUTH_SUCCESS":
                return response

            # Complete the protocol setup. The captured packet's RSA key is
            # reused so its original signature can be checked by the server.
            server_public_key = serialization.load_pem_public_key(
                response["server_public_key"].encode()
            )
            derive_shared_key(client_private, server_public_key)
            public_bytes = serialize_ec_public_key(client_public).decode()
            client.sendall((json.dumps({
                "client_public_key": public_bytes,
                "client_rsa_public_key": client_rsa_public,
            }) + "\n").encode())
            client.sendall((json.dumps(_wire_packet(packet)) + "\n").encode())
            return _receive_json(client)
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as error:
        return {"status": "SIMULATION_FAILED", "reason": str(error)}


def _receive_json(client):
    data = bytearray()
    while b"\n" not in data:
        chunk = client.recv(4096)
        if not chunk:
            break
        data.extend(chunk)
        if len(data) > 1_048_576:
            raise ValueError("Response exceeds maximum size")
    line = bytes(data).split(b"\n", 1)[0]
    if not line:
        raise ValueError("Server closed before returning a response")
    return json.loads(line.decode())


def eavesdropping_demo(packet):
    visible_packet = _wire_packet(packet)
    return {
        "type": "Eavesdropping Attack",
        "original": packet.get("ciphertext", ""),
        "modified": None,
        "result": "Encrypted packet captured",
        "details": "The captured packet contains ciphertext, not the original plaintext.",
        "status": "PROTECTED",
        "captured_packet": json.dumps(visible_packet, indent=4),
    }


def tampering_demo(packet, username, password):
    tampered_packet = dict(packet)
    ciphertext = bytearray.fromhex(tampered_packet["ciphertext"])
    if not ciphertext:
        return {
            "type": "Tampering Attack",
            "status": "FAILED",
            "details": "The packet has no ciphertext to modify.",
        }
    ciphertext[0] ^= 1
    tampered_packet["ciphertext"] = bytes(ciphertext).hex()

    response = send_packet(tampered_packet, username, password)
    blocked = response.get("status") == "SIGNATURE_INVALID"
    return {
        "type": "Tampering Attack",
        "original": packet["ciphertext"],
        "modified": tampered_packet["ciphertext"],
        "result": response,
        "status": "BLOCKED" if blocked else "FAILED",
        "details": (
            "The server rejected the modified packet because its signature no longer matches."
            if blocked else "The server did not report the expected signature rejection."
        ),
    }


def replay_demo(packet, username, password):
    response = send_packet(packet, username, password)
    blocked = response.get("status") == "REPLAY_ATTACK_DETECTED"
    return {
        "type": "Replay Attack",
        "original": packet.get("ciphertext", ""),
        "modified": None,
        "result": response,
        "status": "BLOCKED" if blocked else "FAILED",
        "details": (
            "The server rejected the repeated counter before decrypting the packet."
            if blocked else "The server did not report the expected replay rejection."
        ),
    }

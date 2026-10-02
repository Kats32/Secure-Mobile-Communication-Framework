import socket
import json


HOST = "127.0.0.1"
PORT = 5000


def send_packet(packet):
    client = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    client.connect((HOST, PORT))

    client.send(
        (json.dumps(packet) + "\n").encode()
    )

    data = b""

    while b"\n" not in data:
        chunk = client.recv(4096)

        if not chunk:
            break

        data += chunk

    response = json.loads(
        data.split(b"\n", 1)[0].decode()
    )

    client.close()

    return response


def eavesdropping_demo(packet):

    captured_packet = json.dumps(
        packet,
        indent=4
    )

    return {
        "type": "Eavesdropping Attack",
        "original": packet.get("ciphertext", ""),
        "modified": None,
        "result": "Encrypted packet captured",
        "details": "Attacker can see ciphertext but cannot see the original plaintext.",
        "status": "PROTECTED",
        "captured_packet": captured_packet
    }


def tampering_demo(packet):

    tampered_packet = packet.copy()

    ciphertext = bytearray.fromhex(
        tampered_packet["ciphertext"]
    )

    ciphertext[0] ^= 1

    tampered_packet["ciphertext"] = ciphertext.hex()

    response = send_packet(
        tampered_packet
    )

    return {
        "type": "Tampering Attack",
        "original": packet["ciphertext"],
        "modified": tampered_packet["ciphertext"],
        "result": response,
        "status": "DETECTED"
    }


def replay_demo(packet):

    response = send_packet(packet)

    return {
        "type": "Replay Attack",
        "original": packet.get("ciphertext", ""),
        "modified": None,
        "result": response,
        "status": "DETECTED"
    }
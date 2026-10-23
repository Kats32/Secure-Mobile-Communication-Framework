# Secure Mobile Communication Framework

A Python-based desktop demonstration of a secure messaging flow using several cryptographic techniques. It is an educational prototype; its raw TCP transport and unauthenticated peer keys do not provide production-grade communication security.

## Features

* **AES-256-GCM** for secure message encryption
* **ECDH (SECP256R1)** for secure key exchange
* **RSA-2048** for digital signatures
* **Replay attack protection**
* **Tampering detection**
* **Eavesdropping simulation**
* **PySide6 security dashboard**
* **Activity logs and attack simulator**

## Technologies

* Python 3
* PySide6
* Cryptography library
* TCP Socket Communication
* AES-256-GCM
* ECDH
* RSA

## Project Structure

```text
Secure-Mobile-Network/
│
├── dashboard.py
├── client.py
├── server.py
├── crypto_utils.py
├── register.py
├── security_test.py
├── auth.py
├── attacks.py
├── replay_protection.py
├── pages.py
├── assets/
└── README.md
```

## Installation

Install [uv](https://docs.astral.sh/uv/), then create the environment and install the locked dependencies:

```bash
uv sync
```

Run commands inside the project environment with `uv run`, for example:

```bash
uv run python server.py
uv run python login.py
```

## Running the Project

Start the server first:

```bash
python server.py
```

Then, in another terminal, run the dashboard:

```bash
python dashboard.py
```

The dashboard provides access to:

* Security status
* Secure communication
* Cryptographic key information
* Attack simulation
* Activity logs

## Attack Simulation

The framework demonstrates three common attacks:

**Eavesdropping** — displays the client's encrypted packet; it does not capture live network traffic.

**Tampering** — changes ciphertext while retaining its signature, then submits it through the normal handshake. The server should reject the invalid signature.

**Replay Attack** — resends an accepted packet through the normal handshake. The server should reject its already-used per-user counter.

The console checks can be run with `uv run python security_test.py`. They use a temporary account record and check authentication, cryptographic helpers, and counter ordering.

## Security Flow

```text
Authentication
      ↓
ECDH Key Exchange
      ↓
Session Key
      ↓
AES-256-GCM Encryption
      ↓
Secure Communication
      ↓
Integrity + Signature + Replay Checks
```

## Purpose

This project was developed as an educational demonstration of how **hybrid cryptographic techniques** can be combined to secure communication and detect common attacks.

## Author

**M. Kavya Amrutha**

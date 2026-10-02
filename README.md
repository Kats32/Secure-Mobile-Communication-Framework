# Secure Mobile Communication Framework

A Python-based secure communication framework that combines multiple cryptographic techniques to provide **confidentiality, integrity, authentication, and secure key exchange**.

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
├── attacks.py
├── pages.py
├── assets/
└── README.md
```

## Installation

Make sure **Python 3** is installed.

It is recommended to use a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:

```powershell
venv\Scripts\activate
```

Install the required libraries:

```bash
pip install cryptography PySide6
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

**Eavesdropping** — demonstrates interception of encrypted communication.

**Tampering** — modifies an encrypted message and checks whether the modification is detected.

**Replay Attack** — attempts to resend a previously captured packet.

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

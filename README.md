# Secure Mobile Communication Framework Using Hybrid Cryptographic Techniques

A secure mobile communication framework designed to demonstrate how multiple cryptographic techniques can be combined to provide **confidentiality, integrity, authentication, and secure key exchange** during communication.

The project also includes an **attack simulation module** that demonstrates how common communication attacks can be detected or prevented.

## Features

* 🔐 **AES-256-GCM Encryption**

  * Encrypts messages to provide confidentiality.
  * GCM also provides integrity protection.

* 🔑 **ECDH Key Exchange**

  * Establishes a shared secret key between communicating parties.
  * Uses the SECP256R1 elliptic curve.

* ✍️ **RSA Digital Signatures**

  * Provides message authentication and integrity verification.
  * Uses RSA-2048.

* 🛡️ **Replay Attack Protection**

  * Detects previously captured packets being resent.

* ⚠️ **Tampering Detection**

  * Demonstrates detection of modified encrypted messages.

* 👁️ **Eavesdropping Simulation**

  * Demonstrates what an attacker can observe when communication is intercepted.

* 📊 **Security Dashboard**

  * Displays the current security status of the communication system.
  * Shows encryption, key exchange, authentication, replay protection, and tamper detection status.

* 📝 **Activity Logs**

  * Records important security events and communication activities.

* 🎯 **Attack Simulator**

  * Provides a graphical interface for simulating eavesdropping, tampering, and replay attacks.

## Cryptographic Techniques Used

| Technique         | Purpose                               |
| ----------------- | ------------------------------------- |
| AES-256-GCM       | Message encryption and integrity      |
| ECDH              | Secure shared-key establishment       |
| RSA-2048          | Digital signatures and authentication |
| Replay Protection | Prevents reuse of captured packets    |

The framework uses a **hybrid cryptographic approach**, where different cryptographic mechanisms are used for different security requirements.

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
│
├── assets/
│   └── background image
│
├── README.md
└── .gitignore
```

### Main Files

**`dashboard.py`**

Contains the PySide6 graphical dashboard, navigation, security cards, activity logs, and attack simulator interface.

**`client.py`**

Handles client-side communication and creation of secure communication packets.

**`server.py`**

Runs the secure communication server and handles authentication, key exchange, and packet processing.

**`crypto_utils.py`**

Contains the cryptographic functions used by the framework, including:

* ECDH key generation
* Shared-key derivation
* AES encryption
* Public-key handling

**`attacks.py`**

Contains the attack simulation functions:

* Eavesdropping
* Tampering
* Replay attacks

**`pages.py`**

Contains the additional dashboard pages:

* Secure Chat
* Cryptographic Keys
* Activity Logs

## Requirements

The project requires **Python 3** and the following Python libraries:

* `cryptography`
* `PySide6`

You can install them using:

```bash
pip install cryptography PySide6
```

### Recommended: Virtual Environment

It is recommended to use a Python virtual environment.

Create one:

```bash
python3 -m venv venv
```

Activate it on Linux/WSL:

```bash
source venv/bin/activate
```

On Windows:

```powershell
venv\Scripts\activate
```

Then install the required libraries:

```bash
pip install cryptography PySide6
```

## Running the Project

### 1. Activate the virtual environment

Linux/WSL:

```bash
source venv/bin/activate
```

Windows:

```powershell
venv\Scripts\activate
```

### 2. Start the server

Open a terminal and run:

```bash
python server.py
```

The server should start listening for secure communication connections.

### 3. Start the dashboard

Open another terminal in the project directory and run:

```bash
python dashboard.py
```

The graphical security dashboard will open.

## Dashboard

The dashboard provides access to:

### Dashboard

Displays the overall security status of the communication framework.

It includes:

* AES encryption status
* ECDH key exchange status
* RSA signature status
* Authentication status
* Replay protection
* Tamper detection
* Recent activity

### Secure Chat

Provides the interface for secure message communication.

### Cryptographic Keys

Displays information about the cryptographic mechanisms used by the framework.

### Attack Simulator

Allows security attacks to be simulated against the communication system.

Available simulations:

1. Eavesdropping
2. Tampering
3. Replay Attack

### Activity Logs

Displays previously recorded security and communication events.

## Attack Simulation

The project demonstrates three common attack scenarios.

### Eavesdropping

An attacker attempts to observe intercepted communication.

The simulation demonstrates that intercepted encrypted communication does not directly reveal the original plaintext message.

### Tampering

An attacker modifies the encrypted message before it reaches the receiver.

The integrity mechanisms used by the framework allow the modification to be detected.

### Replay Attack

An attacker captures a previously valid communication packet and attempts to send it again.

Replay protection prevents an already-used packet from being accepted again.

## Security Flow

The basic secure communication process is:

```text
        CLIENT
          │
          │ Authentication
          ▼
       SERVER
          │
          │ ECDH Key Exchange
          ▼
   Shared Session Key
          │
          │
          ▼
   AES-256-GCM Encryption
          │
          ▼
     Secure Packet
          │
          ▼
        SERVER
          │
          ├── Integrity Check
          ├── Signature Verification
          └── Replay Detection
          │
          ▼
     Decrypted Message
```

## Hybrid Cryptography

The framework combines asymmetric and symmetric cryptography.

### ECDH

ECDH is used to establish a shared secret between the communicating parties.

```text
Client Private Key + Server Public Key
                  ↓
            Shared Secret
                  ↓
             Session Key
```

### AES

The derived session key is then used with AES-256-GCM to encrypt messages.

```text
Plaintext
    ↓
AES-256-GCM
    ↓
Encrypted Message
```

### RSA

RSA digital signatures are used to authenticate communication and verify message integrity.

```text
Message
   ↓
RSA Signature
   ↓
Signature Verification
```

## Technologies Used

* Python
* PySide6
* Cryptography library
* AES-256-GCM
* ECDH
* RSA
* TCP Socket Communication

## Installation Summary

For a fresh setup:

```bash
git clone <repository-url>
cd "Secure-Mobile-Network"

python3 -m venv venv
source venv/bin/activate

pip install cryptography PySide6
```

Then run:

```bash
python server.py
```

and in another terminal:

```bash
python dashboard.py
```

## Disclaimer

This project is developed for **educational and demonstration purposes** to study secure communication and common network attack scenarios.

It is not intended to replace a production-grade secure messaging system.

## Author

**M. Kavya Amrutha**

Secure Mobile Communication Framework Using Hybrid Cryptographic Techniques

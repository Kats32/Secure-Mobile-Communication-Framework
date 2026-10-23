# Project Overview

This repository contains a PySide6 desktop demo of a secure-messaging flow. See [`presentation/PROJECT_EXPLANATION.md`](presentation/PROJECT_EXPLANATION.md) for the full architecture, cryptography, setup, and implementation notes.

## Run it

From the project root, install dependencies with `uv sync`. Start the server and login UI in separate terminals:

```bash
uv run python server.py
uv run python login.py
```

Create an account through the registration screen. The app is configured for localhost port `5000`.

## Message and attack flows

- **Normal message:** PBKDF2 account check → P-256 ECDH/HKDF key derivation → AES-GCM encryption → RSA-PSS signature → per-user counter check → decrypt and accept.
- **Tampering:** changes ciphertext but retains the original signature; the authenticated request is rejected by signature verification.
- **Replay:** resubmits an accepted signed packet through the normal handshake; the repeated counter is rejected.
- **Eavesdropping:** displays the client packet locally. It is not a live network capture.

`security_test.py` runs eight focused checks, including temporary-file authentication tests and replay-counter ordering. The server's counters are held in memory and reset on restart. Credentials still travel over plaintext TCP, and neither endpoint authenticates the peer's public key, so this remains a course demonstration rather than a production secure channel.

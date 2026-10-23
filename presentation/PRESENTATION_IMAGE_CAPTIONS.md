# Presentation Image Captions

Captions below follow the current 27-slide presentation. Each short caption can sit directly under an image; the notes explain what the image shows and how to interpret it accurately.

## Architecture and cryptography diagrams

### Slide 7 — System architecture

**Caption:** The PySide6 interface coordinates local account and dashboard functions with a TCP client/server path; the protected-message path combines ECDH/HKDF, AES-GCM, RSA-PSS, and a replay counter.

**Explanation:** The diagram separates the user interface, client, server, local account record, and cryptographic operations. It describes the intended component flow. It should not be read as evidence that the peer identities or network transport are authenticated: the implementation sends credentials over plaintext TCP and accepts peer public keys without a trusted binding.

### Slide 8 — Registration and login flow

**Caption:** Registration stores a random salt and PBKDF2-HMAC-SHA256 verifier; login derives the verifier again from the entered password and saved salt.

**Explanation:** The GUI uses a 16-byte random salt and 100,000 PBKDF2 iterations. The account record stores the salt and derived verifier rather than the original password. The current `auth.py` record format is aligned with the GUI implementation; the supplied report describes an earlier mismatch.

### Slide 9 — Cryptographic building blocks

**Caption:** The prototype combines P-256 ECDH and HKDF for a shared AES key, AES-256-GCM for message confidentiality and integrity, RSA-PSS for signatures, and PBKDF2 for local password verification.

**Explanation:** These mechanisms serve different purposes and depend on the surrounding protocol for safe use. The project does not authenticate the exchanged ECDH key or bind the supplied RSA key to a verified user identity.

### Slide 10 — ECDH and HKDF key agreement

**Caption:** Each endpoint derives the same 32-byte AES key from an ECDH shared secret using HKDF-SHA256.

**Explanation:** Private keys remain local while public keys are exchanged. This implementation uses P-256, HKDF-SHA256, a fixed info label (`secure-mobile-communication`), and no HKDF salt. The client creates an EC key pair for a send while the server EC key is process-scoped. Because the public keys are exchanged without authentication, ECDH alone does not prevent a man-in-the-middle key substitution.

### Slide 11 — AES-256-GCM encryption

**Caption:** AES-GCM encrypts each message with the derived 32-byte key and a fresh 12-byte nonce; the ciphertext includes an authentication tag checked before plaintext is returned.

**Explanation:** The packet carries the nonce and ciphertext bytes (including the tag). Changing the ciphertext, nonce, or tag should make decryption fail. The implementation supplies no additional authenticated data (AAD); counter and other packet metadata are instead covered by the RSA signature.

### Slide 12 — RSA-PSS signatures and replay checks

**Caption:** The client signs the counter, nonce, and ciphertext fields with RSA-PSS; the server verifies the signature and then checks the counter before decrypting.

**Explanation:** The code uses RSA-2048, PSS with MGF1-SHA256, SHA-256, and maximum-length PSS salt. A valid signature proves that the packet matches the private key corresponding to the public key used for verification. In this project, the client supplies that public key on the same connection, so it does not establish a trusted sender identity. Replay state is a per-user in-memory counter; the client reads the latest accepted value during authentication and sends the next one. The state resets at server restart.

### Slide 13 — PBKDF2 password verification

**Caption:** PBKDF2-HMAC-SHA256 derives a salted password verifier at registration and recomputes it at login for comparison.

**Explanation:** The GUI creates a random 16-byte salt and uses 100,000 iterations. This makes offline password guessing more expensive if the local account file is exposed; it does not encrypt a password sent over the TCP connection.

### Slide 14 — Secure message workflow

**Caption:** The client authenticates, establishes a session key, encrypts and signs a packet; the server verifies the signature, checks freshness, and decrypts.

**Explanation:** This is the intended high-level sequence. The server checks the RSA signature before the replay counter and AES-GCM decryption. The diagram does not imply that the key exchange authenticates either endpoint.

### Slide 15 — Attack simulation overview

**Caption:** The interface presents eavesdropping, tampering, and replay as demonstrations of ciphertext visibility, packet modification, and repeated-message handling.

**Explanation:** These labels describe the simulator’s scenarios. See the three result screenshots below for the actual captured outputs and their limitations.

## Interface screenshots

### Slide 17 — Login, registration, and dashboard

**Caption:** The screenshots show the account entry screens and the dashboard layout, including its security-status cards and recent-activity panel.

**Explanation:** Dashboard badges and initial activity entries are static interface content; they are not proof that a secure session or verification event occurred.

### Slide 18 — Secure chat and cryptographic keys

**Caption:** The chat page accepts a message for sending, while the cryptographic-keys page summarizes the mechanisms shown by the prototype.

**Explanation:** These are interface captures. A success dialog or a displayed “active” status should be interpreted alongside the server and protocol behavior, not as independent security evidence.

### Slide 19 — Attack simulator and activity logs

**Caption:** The simulator exposes three attack-demo actions; the activity page lists events recorded or displayed by the interface.

**Explanation:** The log is useful as a UI history view, but its entries do not independently validate that an attack was exercised against an authenticated, established session.

## Attack result screenshots

### Slide 20 — Eavesdropping result

**Caption:** The simulator displays the captured ciphertext and labels the result “PROTECTED,” indicating that the shown encrypted bytes do not reveal the original plaintext.

**Explanation:** In the current `attacks.py`, this demo displays the packet produced by the client; it does not capture live network traffic. The screenshot illustrates ciphertext-versus-plaintext visibility in the UI, not a measured network interception test. It does not prove that credentials or other protocol data are protected in transit—the client sends username and password as plaintext JSON over TCP.

### Slide 20 — Tampering result

**Caption:** The simulator changes one ciphertext bit but retains the original signature; the authenticated server rejects it with `SIGNATURE_INVALID`.

**Explanation:** `attacks.py` changes the first ciphertext byte and resubmits the packet after authentication and key setup. It keeps the original signature, so the server rejects the packet during RSA-PSS verification before decryption. This confirms that the modified packet is not accepted; the displayed result comes from the actual server response.

### Slide 20 — Replay result

**Caption:** The simulator resends an accepted signed packet through the normal handshake; the server rejects its duplicate counter with `REPLAY_ATTACK_DETECTED`.

**Explanation:** The helper authenticates and completes key setup, then resubmits the original counter, ciphertext, and signature. Since that packet was already accepted, the server rejects it using the per-user replay counter before decryption. The displayed status is based on the server's response.

### Reading the attack screenshots together

The screenshots show current application dialogs from a local end-to-end run. Tampering was rejected by signature verification, replay was rejected by the per-user counter check, and eavesdropping displays the client's ciphertext packet without plaintext. The eavesdropping display is still a local simulation rather than a live network capture.

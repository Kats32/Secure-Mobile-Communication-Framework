# Architecture Diagram Captions

These captions describe the diagrams in `assets/architecture_diagrams`. Detailed captions for every image in the PowerPoint, including the individual attack-result screenshots, are in [PRESENTATION_IMAGE_CAPTIONS.md](../../presentation/PRESENTATION_IMAGE_CAPTIONS.md).

1. **System Architecture** — The PySide6 dashboard connects the user to the client and TCP server, while the protected-message path combines ECDH/HKDF, AES-256-GCM, and RSA-PSS. GUI registration uses salted PBKDF2-HMAC-SHA256; the current `auth.py` reads the same PBKDF2 record format as the GUI.

2. **Registration & Login** — Registration generates a random salt and derives a password verifier with PBKDF2-HMAC-SHA256; login derives the value again from the entered password and stored salt, then compares it with the saved verifier.

3. **Secure Message Workflow** — The client authenticates, establishes a session key through ECDH/HKDF, encrypts a message with AES-GCM, and signs packet fields; the server verifies the signature, checks the counter, then decrypts. The public keys are not authenticated by a trusted identity mechanism.

4. **Attack Simulation** — The diagram summarizes the eavesdropping, tampering, and replay scenarios presented by the interface. The current tampering helper retains the original signature so the authenticated server rejects the changed packet; replay resubmits an accepted packet through the normal handshake so its counter is rejected. Eavesdropping remains a local packet display, not a live network capture. Detailed result captions are in the presentation caption file.

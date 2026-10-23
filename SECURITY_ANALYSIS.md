# Security Analysis

## Scope

This review covers the current Python/PySide6 client/server demonstration: account storage, TCP framing, ECDH/HKDF, AES-GCM, RSA-PSS, replay handling, attack simulations, and the console checks. It distinguishes behavior observed in the current code from protections that would require a stronger protocol design.

## Current message path

1. `register.py` creates a random 16-byte salt and a PBKDF2-HMAC-SHA256 verifier. `login.py` verifies that local record.
2. `client.py` sends credentials as newline-delimited JSON over TCP. `auth.py` validates the same PBKDF2 record format.
3. The server returns its P-256 public key and the authenticated user's latest accepted counter.
4. The client sends its P-256 public key and RSA-2048 public key. Both sides derive a 32-byte key with ECDH and HKDF-SHA256.
5. The client encrypts the message with AES-256-GCM and signs the counter, nonce, and ciphertext representation with RSA-PSS/SHA-256.
6. The server verifies the signature, checks the per-user counter, decrypts, updates the counter only after successful authenticated decryption, and responds.

## Findings

### High: credentials and peer keys are not protected/authenticated

The client sends username and password over raw TCP without TLS. The server's ECDH public key is accepted without certificate, signature, or pinning validation. The client RSA public key is supplied by the same connection and is not bound to the authenticated username or ECDH transcript. A valid signature therefore proves consistency with the supplied key, not a trusted user identity. Active network attacks and credential exposure remain possible.

### Medium: replay state is not persistent

The server tracks the highest accepted counter per username in process memory. The client reads that value during authentication and sends the next counter, so repeated ordinary messages work while the server remains running. The server commits the counter only after AES-GCM decryption succeeds, and duplicate or older counters are rejected. Restarting the server clears its replay history; persistent replay protection remains future work.

### Medium: eavesdropping is a local display, not wire capture

`eavesdropping_demo` formats the packet created by the client and shows ciphertext. It does not sniff a live network connection. Tampering and replay helpers now complete authentication and key setup before sending their packet: tampering retains the original signature and is rejected with `SIGNATURE_INVALID`; replay resubmits an accepted packet and is rejected with `REPLAY_ATTACK_DETECTED`.

### Medium: server request handling is sequential

The server now limits newline-delimited JSON requests to 1 MiB and applies a 10-second per-connection timeout. It still processes one connection at a time, so concurrency is limited. `sendall` is used for JSON responses.

### Low: some dashboard indicators are static

The dashboard's initial status cards and activity items are presentation content, not proof that a real session or cryptographic event occurred. Runtime events should be distinguished from those initial labels.

## Verification performed

- `security_test.py`: **8/8 checks passed** for temporary-file PBKDF2 authentication, ECDH agreement, AES-GCM round trip and tampering, replay counter ordering, and RSA-PSS valid/modified signatures.
- Local client/server smoke flow with a temporary account: two successive messages were accepted; a ciphertext change with the original signature was rejected as `SIGNATURE_INVALID`; replay of the accepted packet was rejected as `REPLAY_ATTACK_DETECTED`.
- The login UI remained active under Qt's offscreen platform. A visible desktop display was unavailable in the execution environment, so visual interaction was not verified in this run.

These checks validate the exercised local paths. They do not address TLS, peer identity, server restart replay behavior, concurrency, or resistance to active network attackers.

## Remaining work

1. Protect credentials with TLS and authenticate the server's key.
2. Bind client signing keys to authenticated account identities and the key-exchange transcript.
3. Persist replay state safely or use a protocol with well-defined session/replay windows.
4. Add concurrent connection handling and automated integration tests.
5. Replace static dashboard status indicators with state derived from actual protocol events.

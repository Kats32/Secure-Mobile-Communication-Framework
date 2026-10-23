"""Build a report-grounded, expanded presentation from the BTP template."""
from copy import deepcopy
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile
from xml.etree import ElementTree as ET
import re
import subprocess
from html import escape

PRESENTATION_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PRESENTATION_DIR.parent
TEMPLATE = PROJECT_ROOT / "BTP Presentation Template-3.pptx"
REPORT = PROJECT_ROOT / "crypto_report_iter_3.pdf"
OUTPUT = PRESENTATION_DIR / "Secure_Mobile_Communication_Framework_BTP.pptx"
NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
    "ep": "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties",
    "vt": "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes",
}
for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)
EMU = 914400


def parse_xml(data):
    for _, (prefix, uri) in ET.iterparse(BytesIO(data), events=("start-ns",)):
        ET.register_namespace(prefix or "", uri)
    return ET.fromstring(data)


def xml_bytes(root):
    return ET.tostring(root, encoding="UTF-8", xml_declaration=True)


def slide_shape(slide, name, ph_type=None, no_placeholder=False):
    for item in slide.findall(".//p:sp", NS):
        nv = item.find("p:nvSpPr/p:cNvPr", NS)
        ph = item.find("p:nvSpPr/p:nvPr/p:ph", NS)
        if nv is None or nv.get("name") != name:
            continue
        if ph_type and (ph is None or ph.get("type") != ph_type):
            continue
        if no_placeholder and ph is not None:
            continue
        return item
    raise ValueError(f"Slide shape not found: {name}")


def set_text(shape, text, size=None):
    body = shape.find("p:txBody", NS)
    ps = body.findall("a:p", NS)
    p = ps[0] if ps else ET.SubElement(body, f"{{{NS['a']}}}p")
    for extra in ps[1:]:
        body.remove(extra)
    runs = p.findall("a:r", NS)
    run = runs[0] if runs else ET.SubElement(p, f"{{{NS['a']}}}r")
    for extra in runs[1:]:
        p.remove(extra)
    for old in run.findall("a:t", NS):
        run.remove(old)
    if run.find("a:rPr", NS) is None:
        ET.SubElement(run, f"{{{NS['a']}}}rPr", {"lang": "en-US"})
    node = ET.SubElement(run, f"{{{NS['a']}}}t")
    node.text = text
    rpr = run.find("a:rPr", NS)
    if size:
        rpr.set("sz", str(size))


def set_bullets(shape, lines, size=1900):
    body = shape.find("p:txBody", NS)
    for p in body.findall("a:p", NS):
        body.remove(p)
    for line in lines:
        p = ET.SubElement(body, f"{{{NS['a']}}}p")
        ET.SubElement(p, f"{{{NS['a']}}}pPr", {"lvl": "0"})
        run = ET.SubElement(p, f"{{{NS['a']}}}r")
        ET.SubElement(run, f"{{{NS['a']}}}rPr", {"lang": "en-US", "sz": str(size)})
        ET.SubElement(run, f"{{{NS['a']}}}t").text = line


def set_cover_lines(shape, lines, size):
    body = shape.find("p:txBody", NS)
    for p in body.findall("a:p", NS):
        body.remove(p)
    for line in lines:
        p = ET.SubElement(body, f"{{{NS['a']}}}p")
        pp = ET.SubElement(p, f"{{{NS['a']}}}pPr", {"algn": "ctr"})
        ET.SubElement(pp, f"{{{NS['a']}}}buNone")
        r = ET.SubElement(p, f"{{{NS['a']}}}r")
        ET.SubElement(r, f"{{{NS['a']}}}rPr", {"lang": "en-US", "sz": str(size)})
        ET.SubElement(r, f"{{{NS['a']}}}t").text = line


def set_box(shape, box):
    x, y, w, h = (int(v * EMU) for v in box)
    xfrm = shape.find("p:spPr/a:xfrm", NS)
    if xfrm is None:
        xfrm = ET.SubElement(shape.find("p:spPr", NS), f"{{{NS['a']}}}xfrm")
        ET.SubElement(xfrm, f"{{{NS['a']}}}off")
        ET.SubElement(xfrm, f"{{{NS['a']}}}ext")
    xfrm.find("a:off", NS).attrib.update(x=str(x), y=str(y))
    xfrm.find("a:ext", NS).attrib.update(cx=str(w), cy=str(h))


def remove_content_placeholder(slide):
    placeholder = slide_shape(slide, "Content Placeholder 2")
    parent = next(parent for parent in slide.iter() if placeholder in list(parent))
    parent.remove(placeholder)


def set_slide_number(slide, number):
    shp = slide_shape(slide, "Slide Number Placeholder 9")
    text_nodes = shp.findall(".//a:t", NS)
    if text_nodes:
        text_nodes[-1].text = str(number)


def add_picture(slide, rid, name, alt, box):
    x, y, w, h = (int(v * EMU) for v in box)
    pic = ET.Element(f"{{{NS['p']}}}pic")
    nv = ET.SubElement(pic, f"{{{NS['p']}}}nvPicPr")
    ids = [int(e.get("id", 0)) for e in slide.findall(".//p:cNvPr", NS)]
    ET.SubElement(nv, f"{{{NS['p']}}}cNvPr", {
        "id": str(max(ids, default=1) + 1), "name": name, "descr": alt,
    })
    locks = ET.SubElement(nv, f"{{{NS['p']}}}cNvPicPr")
    ET.SubElement(locks, f"{{{NS['a']}}}picLocks", {"noChangeAspect": "1"})
    ET.SubElement(nv, f"{{{NS['p']}}}nvPr")
    fill = ET.SubElement(pic, f"{{{NS['p']}}}blipFill")
    ET.SubElement(fill, f"{{{NS['a']}}}blip", {f"{{{NS['r']}}}embed": rid})
    stretch = ET.SubElement(fill, f"{{{NS['a']}}}stretch")
    ET.SubElement(stretch, f"{{{NS['a']}}}fillRect")
    sppr = ET.SubElement(pic, f"{{{NS['p']}}}spPr")
    xf = ET.SubElement(sppr, f"{{{NS['a']}}}xfrm")
    ET.SubElement(xf, f"{{{NS['a']}}}off", {"x": str(x), "y": str(y)})
    ET.SubElement(xf, f"{{{NS['a']}}}ext", {"cx": str(w), "cy": str(h)})
    geom = ET.SubElement(sppr, f"{{{NS['a']}}}prstGeom", {"prst": "rect"})
    ET.SubElement(geom, f"{{{NS['a']}}}avLst")
    tree = slide.find(".//p:spTree", NS)
    ext = tree.find("p:extLst", NS)
    tree.insert(list(tree).index(ext) if ext is not None else len(tree), pic)


def add_caption(slide, text, box, name, size=1050, align="l"):
    """Add a compact, visible figure caption to a slide."""
    x, y, w, h = (int(v * EMU) for v in box)
    shape = ET.Element(f"{{{NS['p']}}}sp")
    nv = ET.SubElement(shape, f"{{{NS['p']}}}nvSpPr")
    ids = [int(e.get("id", 0)) for e in slide.findall(".//p:cNvPr", NS)]
    ET.SubElement(nv, f"{{{NS['p']}}}cNvPr", {
        "id": str(max(ids, default=1) + 1), "name": name, "descr": text,
    })
    ET.SubElement(nv, f"{{{NS['p']}}}cNvSpPr")
    ET.SubElement(nv, f"{{{NS['p']}}}nvPr")
    sppr = ET.SubElement(shape, f"{{{NS['p']}}}spPr")
    xfrm = ET.SubElement(sppr, f"{{{NS['a']}}}xfrm")
    ET.SubElement(xfrm, f"{{{NS['a']}}}off", {"x": str(x), "y": str(y)})
    ET.SubElement(xfrm, f"{{{NS['a']}}}ext", {"cx": str(w), "cy": str(h)})
    geom = ET.SubElement(sppr, f"{{{NS['a']}}}prstGeom", {"prst": "rect"})
    ET.SubElement(geom, f"{{{NS['a']}}}avLst")
    ET.SubElement(sppr, f"{{{NS['a']}}}noFill")
    txbody = ET.SubElement(shape, f"{{{NS['p']}}}txBody")
    ET.SubElement(txbody, f"{{{NS['a']}}}bodyPr", {
        "wrap": "square", "anchor": "t", "lIns": "25000", "rIns": "25000",
        "tIns": "12000", "bIns": "0",
    })
    ET.SubElement(txbody, f"{{{NS['a']}}}lstStyle")
    para = ET.SubElement(txbody, f"{{{NS['a']}}}p")
    ET.SubElement(para, f"{{{NS['a']}}}pPr", {"algn": align})
    run = ET.SubElement(para, f"{{{NS['a']}}}r")
    rpr = ET.SubElement(run, f"{{{NS['a']}}}rPr", {"lang": "en-US", "sz": str(size)})
    solid = ET.SubElement(rpr, f"{{{NS['a']}}}solidFill")
    ET.SubElement(solid, f"{{{NS['a']}}}srgbClr", {"val": "54213F"})
    ET.SubElement(run, f"{{{NS['a']}}}t").text = text
    ET.SubElement(para, f"{{{NS['a']}}}endParaRPr", {"lang": "en-US", "sz": str(size)})
    tree = slide.find(".//p:spTree", NS)
    ext = tree.find("p:extLst", NS)
    tree.insert(list(tree).index(ext) if ext is not None else len(tree), shape)


def attach_image(files, slide_no, image_name, image_bytes, alt, box):
    slide_path = f"ppt/slides/slide{slide_no}.xml"
    rel_path = f"ppt/slides/_rels/slide{slide_no}.xml.rels"
    slide, rels = parse_xml(files[slide_path]), parse_xml(files[rel_path])
    ids = [int(m.group(1)) for rel in rels
           if (m := re.fullmatch(r"rId(\d+)", rel.get("Id", "")))]
    rid = f"rId{max(ids, default=0) + 1}"
    ET.SubElement(rels, f"{{{NS['rel']}}}Relationship", {
        "Id": rid,
        "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
        "Target": f"../media/{image_name}",
    })
    add_picture(slide, rid, image_name, alt, box)
    files[slide_path], files[rel_path] = xml_bytes(slide), xml_bytes(rels)
    files[f"ppt/media/{image_name}"] = image_bytes


def crop_image(source, output, geometry):
    subprocess.run(["convert", str(source), "-crop", geometry, "+repage", str(output)], check=True)
    return output.read_bytes()


def make_flow_diagram(tempdir, stem, title, steps):
    """Render a compact, readable vertical flow diagram for a crypto slide."""
    width, height = 820, 590
    pieces = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" rx="28" fill="#fff8fb"/>',
        '<text x="410" y="48" text-anchor="middle" font-family="Arial" font-size="25" font-weight="700" fill="#54213f">' + escape(title) + '</text>',
    ]
    y0, card_h, gap = 78, 92, 34
    colors = ["#f5e5ee", "#e8eafb", "#fff0d8", "#e5f3ed"]
    for index, (heading, detail) in enumerate(steps):
        y = y0 + index * (card_h + gap)
        if index:
            pieces.append(f'<path d="M410 {y-gap+2} L410 {y-8}" stroke="#d73d7f" stroke-width="4"/>')
            pieces.append(f'<path d="M401 {y-18} L410 {y-7} L419 {y-18}" fill="none" stroke="#d73d7f" stroke-width="4"/>')
        pieces.append(f'<rect x="60" y="{y}" width="700" height="{card_h}" rx="18" fill="{colors[index % len(colors)]}" stroke="#e4c5d5" stroke-width="2"/>')
        pieces.append(f'<rect x="76" y="{y+15}" width="8" height="62" rx="4" fill="#d73d7f"/>')
        pieces.append(f'<text x="102" y="{y+38}" font-family="Arial" font-size="21" font-weight="700" fill="#54213f">{escape(heading)}</text>')
        pieces.append(f'<text x="102" y="{y+67}" font-family="Arial" font-size="16" fill="#68435a">{escape(detail)}</text>')
    pieces.append('</svg>')
    svg_path = Path(tempdir) / f"{stem}.svg"
    png_path = Path(tempdir) / f"{stem}.png"
    svg_path.write_text("\n".join(pieces), encoding="utf-8")
    subprocess.run(["convert", str(svg_path), str(png_path)], check=True)
    return png_path.read_bytes()


def extract_report_images(tempdir):
    prefix = Path(tempdir) / "report-image"
    subprocess.run(["pdfimages", "-png", "-f", "13", "-l", "22", str(REPORT), str(prefix)], check=True)
    return {i: Path(f"{prefix}-{i:03d}.png").read_bytes()
            for i in (0, 2, 4, 6, 8, 10, 18, 20, 22, 24)}


SLIDES = [
    ("Presentation Roadmap", [
        "Project context, objectives, and proposed approach",
        "System architecture and cryptographic workflow",
        "Implementation, interface, and attack demonstrations",
        "Security findings, evidence quality, and next steps",
    ], 2050),
    ("Background & Objectives", [
        "Communication channels may expose data to interception, modification, impersonation, or replay.",
        "Protect message confidentiality and integrity with AES-256-GCM.",
        "Establish a shared secret with ECDH; derive a session key with HKDF-SHA256.",
        "Support signatures, password protection, freshness checks, and practical demonstrations through a desktop dashboard.",
        "Project scope: Python/PySide6 prototype for a mobile-communication use case; native mobile deployment is future work.",
    ], 1800),
    ("Problem & Proposed Approach", [
        "Baseline problem: plain or single-mechanism communication can leave identity, key establishment, integrity, and freshness unaddressed.",
        "Proposed framework combines local account checks, ECDH/HKDF, AES-GCM, RSA signatures, counter checks, and a GUI attack simulator.",
        "The contribution is an educational integration and demonstration, not a production-ready protocol or independent security evaluation.",
    ], 1950),
    ("Standards & Related Work", [
        "NIST FIPS 197 defines AES; SP 800-38D specifies GCM authenticated encryption. [1], [2]",
        "NIST FIPS 186-5 covers digital signatures; the project uses RSA-2048 with PSS/SHA-256. [3]",
        "NIST SP 800-132 covers password-based key derivation; RFC 5869 defines HKDF. [4], [5]",
        "The report cites standards and documentation, but does not include a formal comparison of prior communication systems.",
    ], 1850),
    ("Requirements & Method", [
        "Hardware: laptop or desktop, at least 4 GB RAM recommended, and a network interface for TCP.",
        "Software: Python 3, PySide6, cryptography, TCP sockets, and Git/GitHub; the repository also provides pyproject.toml and uv.lock.",
        "Method: separate interface/account, cryptography, client/server, and attack-simulation responsibilities.",
        "No dataset is used; evaluation is based on cryptographic operations, protocol behavior, and GUI demonstrations.",
    ], 1850),
    ("System Architecture", None, 0),
    ("Registration & Login", [
        "GUI registration creates a random 16-byte salt and derives a SHA-256 PBKDF2 verifier with 100,000 iterations.",
        "The account file stores the salt and derived hash; login recomputes and compares the verifier.",
        "The current workspace auth.py was aligned with the GUI PBKDF2 record format; the supplied report PDF still describes the earlier mismatch.",
    ], 1750),
    ("Cryptographic Building Blocks", [
        "ECDH SECP256R1: client and server derive a 32-byte session key through HKDF-SHA256.",
        "AES-256-GCM: random 12-byte nonce; ciphertext includes the authentication tag; no additional authenticated data is supplied.",
        "RSA-2048/PSS with SHA-256: signature covers the textual counter, nonce, and ciphertext fields.",
        "PBKDF2-HMAC-SHA256: password verifier uses a random salt and 100,000 iterations in the GUI code.",
        "Key caveat: the server public key and client signing key are not bound to trusted identities.",
    ], 1700),
    ("ECDH + HKDF Key Agreement", [
        "Both endpoints create an elliptic-curve key pair on P-256; private keys stay local while public keys are exchanged.",
        "ECDH combines each endpoint’s private key with the peer’s public key to produce the same shared secret at both ends.",
        "HKDF-SHA256 turns that secret into a 32-byte AES key using the fixed info label secure-mobile-communication; salt is None.",
        "In this code, the client creates a new EC key pair for a send and the server key is process-scoped. The exchange is unauthenticated, so a network attacker could substitute keys.",
    ], 1450),
    ("AES-256-GCM Encryption", [
        "AES is a symmetric cipher: both sides use the same 32-byte session key. GCM combines encryption with an authentication tag.",
        "For each message, the client generates a random 12-byte nonce. The packet carries the nonce and ciphertext; the library appends a 16-byte tag to the ciphertext bytes.",
        "The receiver must use the same key and nonce. GCM verifies the tag before returning plaintext; altered ciphertext, nonce, or tag causes decryption failure.",
        "No additional authenticated data (AAD) is supplied, so packet metadata is protected separately by the RSA signature rather than by GCM AAD.",
    ], 1400),
    ("RSA-PSS Signatures & Replay", [
        "The client generates a 2048-bit RSA key and signs UTF-8 text: counter | nonce-hex | ciphertext-hex.",
        "The implementation uses RSA-PSS, MGF1-SHA256, SHA-256, and maximum-length PSS salt. The server verifies before replay checking and decryption.",
        "The server keeps a per-user counter in memory. Each client reads the latest value during authentication and sends the next one; server restart clears the replay history.",
        "The server verifies with the RSA public key supplied by that same client connection. This proves consistency with the supplied key, not who owns it; the signature also omits the username and ECDH transcript.",
    ], 1350),
    ("PBKDF2 Password Verification", [
        "Registration generates a random 16-byte salt and derives a 32-byte verifier with PBKDF2-HMAC-SHA256 and 100,000 iterations.",
        "The local users.json record stores the salt and derived verifier, not the original password. A unique salt prevents identical passwords from having identical stored values.",
        "At login, the application derives the verifier again from the entered password and stored salt, then compares it with the saved value.",
        "This slows offline guessing if the account file is copied; it does not encrypt the password while it travels to the TCP server. The current auth.py now matches the GUI record format.",
    ], 1350),
    ("Secure Message Workflow", None, 0),
    ("Attack Demonstrations", None, 0),
    ("Implementation Map", [
        "login.py / register.py — account windows, local PBKDF2 registration and login.",
        "dashboard.py / pages.py — navigation, dashboard, chat, key information, logs, and simulator dialogs.",
        "client.py / server.py — newline-delimited JSON over TCP; packet creation, signature/replay checks, decryption, and responses.",
        "crypto_utils.py — P-256 ECDH, HKDF-SHA256, AES-GCM, RSA-PSS, and a separate SHA-256 helper.",
        "auth.py — server-side account lookup; current workspace version reads the GUI PBKDF2 record format.",
        "replay_protection.py — shared per-user counter policy used by the TCP server and console checks.",
        "attacks.py / security_test.py — demonstration helpers and console checks; users.json stores local account records.",
    ], 1750),
    ("Interface: Login & Dashboard", None, 0),
    ("Interface: Chat & Keys", None, 0),
    ("Interface: Simulator & Activity Logs", None, 0),
    ("Attack Result Screenshots", None, 0),
    ("Attack Result Interpretation", [
        "Eavesdropping: the simulator displays the packet produced by the client and labels its contents protected; it does not sniff live network traffic.",
        "Tampering: the simulator changes ciphertext but keeps the original signature. The authenticated server session rejects it with SIGNATURE_INVALID.",
        "Replay: the simulator resubmits an accepted packet through the normal handshake. The server rejects its duplicate counter with REPLAY_ATTACK_DETECTED.",
        "The tampering and replay outcomes are now tied to the corresponding server checks, and normal GUI messages advance their counters instead of reusing 1.",
    ], 1550),
    ("Security Review: Identity & Trust", [
        "Client sends username and password as plaintext JSON over TCP; there is no TLS transport.",
        "The server ECDH public key is returned without a certificate, signature, or pinning check, so the client cannot authenticate the server key.",
        "The client supplies its own RSA public key on the same connection; it is not enrolled or bound to the username or ECDH transcript.",
        "The signature can check packet integrity relative to that supplied key, but does not prove a trusted sender identity or non-repudiation.",
    ], 1750),
    ("Security Review: Replay & Robustness", [
        "Replay state is tracked per user in server memory and is lost on server restart; counters are committed only after authenticated decryption succeeds.",
        "The client reads the server's latest counter during authentication and sends the next value, so repeated normal GUI messages work during the server process lifetime.",
        "Tampering and replay demonstrations now perform authentication and key setup; altered signatures and duplicate counters reach their intended rejection checks.",
        "TCP requests are limited to 1 MiB and each connection has a 10-second timeout. The server still handles clients sequentially, which limits concurrency.",
        "Dashboard security badges and initial activity entries are static UI text, not proof that a session was established.",
    ], 1650),
    ("Testing & Reported Evidence", [
        "security_test.py now runs eight isolated checks for PBKDF2 authentication, ECDH, AES-GCM, replay-counter ordering, and RSA-PSS; all eight passed in the current environment.",
        "A localhost client/server check accepted two successive messages, rejected a tampered packet with SIGNATURE_INVALID, and rejected a repeated packet with REPLAY_ATTACK_DETECTED.",
        "The tampering/replay helpers now complete authentication and key setup before submitting the captured packet, so the server's intended checks produce these results.",
        "Eavesdropping remains a local ciphertext display, not a live packet capture. Dashboard status cards and initial activity entries also remain static UI content.",
    ], 1550),
    ("Advantages & Limitations", [
        "Combines P-256 ECDH/HKDF, AES-GCM, RSA-PSS, and PBKDF2 in a navigable client/server demo; the GUI exposes account, message, key, and attack flows.",
        "Credentials travel as plaintext JSON over TCP. The server ECDH key and client RSA signing key are not authenticated or bound to the account identity.",
        "Replay state is per-user but in memory; it resets on server restart and is not persisted across sessions.",
        "Eavesdropping is a packet display rather than wire capture; tampering and replay exercise signature and counter rejection through the normal handshake.",
        "The server limits request size and connection wait time but handles clients sequentially, limiting concurrent use.",
    ], 1500),
    ("Future Work", [
        "Introduce authenticated peer identity with certificates or pinned keys; protect credentials in transit.",
        "Protect credentials in transit, authenticate peer keys, persist replay state safely, and add concurrent request handling.",
        "Support concurrent clients and stronger server-side account management; extend to native mobile platforms.",
        "Add reproducible automated security tests, formal protocol analysis, and independent review.",
    ], 1850),
    ("Conclusion", [
        "The prototype brings ECDH/HKDF, AES-GCM, RSA signatures, PBKDF2, and a PySide6 interface into one client/server demonstration.",
        "Its educational value is in showing complementary controls and the need to validate how they are composed.",
        "The identity and transport gaps remain important before making production security claims; the account format, normal counter flow, and attack checks now work consistently.",
    ], 1850),
    ("References", [
        "[1] NIST, Advanced Encryption Standard (AES), FIPS PUB 197.",
        "[2] NIST, Recommendation for Block Cipher Modes of Operation: GCM and GMAC, SP 800-38D.",
        "[3] NIST, Digital Signature Standard (DSS), FIPS PUB 186-5.",
        "[4] NIST, Recommendation for Password-Based Key Derivation, SP 800-132.",
        "[5] H. Krawczyk and P. Eronen, HMAC-based Extract-and-Expand Key Derivation Function, RFC 5869.",
        "[6] Python Cryptographic Authority, Python Cryptography Documentation.",
    ], 1400),
]


def build():
    with TemporaryDirectory(prefix="btp_expanded_") as temp:
        imgs = extract_report_images(temp)
        attack_capture_dir = PRESENTATION_DIR / "attack_results"
        attack_imgs = {
            "eavesdropping": attack_capture_dir / "eavesdropping.png",
            "tampering": attack_capture_dir / "tampering.png",
            "replay": attack_capture_dir / "replay.png",
        }
        if not all(path.exists() for path in attack_imgs.values()):
            attack_imgs = {
                "eavesdropping": imgs[18],
                "tampering": imgs[20],
                "replay": imgs[22],
            }
        else:
            attack_imgs = {name: path.read_bytes() for name, path in attack_imgs.items()}
        diagram_dir = PROJECT_ROOT / "assets/architecture_diagrams"
        crops = {
            "arch": crop_image(diagram_dir / "system_architecture.png", Path(temp) / "arch.png", "1060x315+0+95"),
            "registration": crop_image(diagram_dir / "registration_flow.png", Path(temp) / "registration.png", "1060x310+0+90"),
            "workflow": crop_image(diagram_dir / "secure_message_workflow.png", Path(temp) / "workflow.png", "1040x330+0+90"),
            "attacks": crop_image(diagram_dir / "attack_simulation.png", Path(temp) / "attacks.png", "1050x340+0+90"),
        }
        crypto_diagrams = {
            "ecdh": make_flow_diagram(temp, "ecdh_hkdf", "FROM PUBLIC SHARES TO SESSION KEY", [
                ("Client P-256 key pair", "Private key stays on client; public key is sent"),
                ("Server P-256 key pair", "Private key stays on server; public key is returned"),
                ("ECDH shared secret", "Each side combines its private key with peer public key"),
                ("HKDF-SHA256 → 32-byte key", "info label set; salt=None; feeds AES-256-GCM"),
            ]),
            "aes": make_flow_diagram(temp, "aes_gcm", "CONFIDENTIALITY + TAMPER CHECK", [
                ("Plaintext + 32-byte session key", "Message text and derived symmetric key"),
                ("AES-256-GCM encrypt", "Fresh random 12-byte nonce; AAD=None"),
                ("Packet fields", "Counter + nonce + ciphertext || 16-byte tag"),
                ("Verify tag, then decrypt", "Wrong key or modified input → reject; no plaintext"),
            ]),
            "signature": make_flow_diagram(temp, "rsa_signature", "SIGNATURE + REPLAY CHECK", [
                ("Fields to sign", "counter | nonce-hex | ciphertext-hex"),
                ("RSA-PSS / SHA-256", "Client private key; RSA-2048; MGF1-SHA256"),
                ("Server verifies signature", "Uses client public key supplied in connection"),
                ("Check counter, then decrypt", "Per-user in-memory counter; verification key is not identity proof"),
            ]),
            "pbkdf2": make_flow_diagram(temp, "pbkdf2", "PASSWORD RECORD AND LOGIN CHECK", [
                ("Registration input", "Password + random 16-byte salt"),
                ("PBKDF2-HMAC-SHA256", "100,000 iterations; derive 32-byte verifier"),
                ("Local record", "users.json stores salt + verifier"),
                ("Login", "Re-derive with saved salt; compare verifier"),
            ]),
        }
        with ZipFile(TEMPLATE) as zin:
            files = {info.filename: zin.read(info.filename) for info in zin.infolist()}

        # Preserve the template cover and fill it with report metadata.
        cover = parse_xml(files["ppt/slides/slide1.xml"])
        set_text(slide_shape(cover, "Title 1"), "Secure Mobile Communication Framework", 4300)
        set_cover_lines(slide_shape(cover, "Subtitle 2", ph_type="subTitle"), [
            "Using Hybrid Cryptographic Techniques",
            "M. Kavya Amrutha · 2023BCS0221",
            "Harissh Ragav Dhamodaran · 2023BCD0059",
            "A. Pranathi · 2023BCD0065",
            "K. Neharika · 2023BCS0053",
        ], 1550)
        set_cover_lines(slide_shape(cover, "Subtitle 2", no_placeholder=True), [
            "Course Code: CSS411",
            "Cryptography and Network Security",
        ], 1450)
        files["ppt/slides/slide1.xml"] = xml_bytes(cover)

        # Duplicate the template's content slide for each topic, preserving its theme, logo, and footer.
        base_slide = parse_xml(files["ppt/slides/slide2.xml"])
        base_rels = parse_xml(files["ppt/slides/_rels/slide2.xml.rels"])
        for rel in list(base_rels):
            if rel.get("Type", "").endswith("/notesSlide"):
                base_rels.remove(rel)
        for no, (title, bullets, size) in enumerate(SLIDES, start=2):
            s = deepcopy(base_slide)
            set_text(slide_shape(s, "Title 1"), title)
            set_slide_number(s, no)
            if bullets is None:
                remove_content_placeholder(s)
            else:
                set_bullets(slide_shape(s, "Content Placeholder 2"), bullets, size)
            files[f"ppt/slides/slide{no}.xml"] = xml_bytes(s)
            files[f"ppt/slides/_rels/slide{no}.xml.rels"] = xml_bytes(deepcopy(base_rels))

        # Create presentation relationships and slide IDs (cover + 22 content slides).
        pres = parse_xml(files["ppt/presentation.xml"])
        rels = parse_xml(files["ppt/_rels/presentation.xml.rels"])
        sld_list = pres.find("p:sldIdLst", NS)
        for item in list(sld_list):
            sld_list.remove(item)
        rel_id_by_slide = {}
        max_rel = max([int(m.group(1)) for rel in rels
                       if (m := re.fullmatch(r"rId(\d+)", rel.get("Id", "")))], default=0)
        for rel in list(rels):
            if rel.get("Type", "").endswith("/slide"):
                target = rel.get("Target", "")
                if target == "slides/slide1.xml":
                    rel_id_by_slide[1] = rel.get("Id")
                else:
                    rels.remove(rel)
        if 1 not in rel_id_by_slide:
            max_rel += 1
            rid = f"rId{max_rel}"
            ET.SubElement(rels, f"{{{NS['rel']}}}Relationship", {
                "Id": rid,
                "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide",
                "Target": "slides/slide1.xml",
            })
            rel_id_by_slide[1] = rid
        for no in range(2, len(SLIDES) + 2):
            max_rel += 1
            rid = f"rId{max_rel}"
            ET.SubElement(rels, f"{{{NS['rel']}}}Relationship", {
                "Id": rid,
                "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide",
                "Target": f"slides/slide{no}.xml",
            })
            rel_id_by_slide[no] = rid
        for no in range(1, len(SLIDES) + 2):
            ET.SubElement(sld_list, f"{{{NS['p']}}}sldId", {
                "id": str(255 + no), f"{{{NS['r']}}}id": rel_id_by_slide[no],
            })
        files["ppt/presentation.xml"] = xml_bytes(pres)
        files["ppt/_rels/presentation.xml.rels"] = xml_bytes(rels)

        # Add slide part declarations for the extra pages.
        types = parse_xml(files["[Content_Types].xml"])
        for no in range(11, len(SLIDES) + 2):
            part = f"/ppt/slides/slide{no}.xml"
            if not any(x.get("PartName") == part for x in types):
                ET.SubElement(types, f"{{{NS['ct']}}}Override", {
                    "PartName": part,
                    "ContentType": "application/vnd.openxmlformats-officedocument.presentationml.slide+xml",
                })
        if not any(x.get("Extension") == "png" for x in types):
            ET.SubElement(types, f"{{{NS['ct']}}}Default", {
                "Extension": "png", "ContentType": "image/png",
            })
        files["[Content_Types].xml"] = xml_bytes(types)

        # Refresh the slide count displayed in Office document properties.
        if "docProps/app.xml" in files:
            app = parse_xml(files["docProps/app.xml"])
            slides_node = app.find("ep:Slides", NS)
            if slides_node is not None:
                slides_node.text = str(len(SLIDES) + 1)
            files["docProps/app.xml"] = xml_bytes(app)

        # Insert the report diagrams and genuine report screenshots into the corresponding slides.
        slide_no_by_title = {title: i for i, (title, _, _) in enumerate(SLIDES, start=2)}
        image_slides = {
            slide_no_by_title["System Architecture"]: [("btp_architecture.png", crops["arch"], "System architecture block diagram", (0.95, 2.25, 11.45, 3.40))],
            slide_no_by_title["Registration & Login"]: [("btp_registration.png", crops["registration"], "Registration and login flow", (0.85, 2.75, 6.25, 1.83))],
            slide_no_by_title["ECDH + HKDF Key Agreement"]: [("crypto_ecdh_hkdf.png", crypto_diagrams["ecdh"], "ECDH and HKDF key derivation flow", (0.70, 2.12, 5.55, 4.00))],
            slide_no_by_title["AES-256-GCM Encryption"]: [("crypto_aes_gcm.png", crypto_diagrams["aes"], "AES-GCM encryption and authentication flow", (0.70, 2.12, 5.55, 4.00))],
            slide_no_by_title["RSA-PSS Signatures & Replay"]: [("crypto_rsa_pss.png", crypto_diagrams["signature"], "RSA-PSS signing and replay check flow", (0.70, 2.12, 5.55, 4.00))],
            slide_no_by_title["PBKDF2 Password Verification"]: [("crypto_pbkdf2.png", crypto_diagrams["pbkdf2"], "PBKDF2 registration and login flow", (0.70, 2.12, 5.55, 4.00))],
            slide_no_by_title["Secure Message Workflow"]: [("btp_workflow.png", crops["workflow"], "Secure message workflow", (1.05, 2.35, 11.05, 3.51))],
            slide_no_by_title["Attack Demonstrations"]: [("btp_attacks.png", crops["attacks"], "Attack simulation overview", (1.15, 2.30, 10.95, 3.55))],
            slide_no_by_title["Interface: Login & Dashboard"]: [
                ("ui_dashboard.png", imgs[4], "Security Dashboard screen", (0.72, 2.05, 7.25, 4.54)),
                ("ui_login.png", imgs[0], "Login screen", (8.15, 2.20, 1.88, 2.38)),
                ("ui_registration.png", imgs[2], "Registration screen", (10.20, 2.20, 1.95, 2.38)),
            ],
            slide_no_by_title["Interface: Chat & Keys"]: [
                ("ui_secure_chat.png", imgs[6], "Secure Chat screen", (0.78, 2.35, 5.65, 3.53)),
                ("ui_crypto_keys.png", imgs[8], "Cryptographic Keys screen", (6.85, 2.35, 5.65, 3.53)),
            ],
            slide_no_by_title["Interface: Simulator & Activity Logs"]: [
                ("ui_activity_logs.png", imgs[24], "Activity Logs screen", (5.05, 2.28, 7.20, 4.37)),
                ("ui_attack_menu.png", imgs[10], "Attack Simulator menu", (0.83, 2.37, 4.05, 4.06)),
            ],
            slide_no_by_title["Attack Result Screenshots"]: [
                ("result_eavesdropping.png", attack_imgs["eavesdropping"], "Eavesdropping result shown by the current GUI", (0.48, 2.65, 3.70, 3.39)),
                ("result_tampering.png", attack_imgs["tampering"], "Tampering signature rejection shown by the current GUI", (4.82, 2.65, 3.70, 3.35)),
                ("result_replay.png", attack_imgs["replay"], "Replay counter rejection shown by the current GUI", (9.15, 2.65, 3.70, 3.35)),
            ],
        }
        for no, images in image_slides.items():
            for name, data, alt, box in images:
                attach_image(files, no, name, data, alt, box)

        figure_captions = {
            "System Architecture": [
                ("The interface connects to a TCP client/server path; cryptographic blocks protect message contents, while peer identity and transport protection remain separate concerns.", (0.95, 5.73, 11.45, 0.62), 1050),
            ],
            "Registration & Login": [
                ("Registration stores a salted PBKDF2 verifier; login derives it again and compares the result.", (0.85, 4.68, 6.25, 0.62), 1050),
            ],
            "ECDH + HKDF Key Agreement": [
                ("Both sides derive the same session key; unauthenticated public-key exchange leaves room for key substitution.", (0.70, 6.18, 5.55, 0.48), 950),
            ],
            "AES-256-GCM Encryption": [
                ("A fresh nonce and valid GCM tag are required to recover plaintext; the code supplies no AAD.", (0.70, 6.18, 5.55, 0.48), 950),
            ],
            "RSA-PSS Signatures & Replay": [
                ("The signature covers counter, nonce, and ciphertext; verification with an untrusted key does not establish sender identity.", (0.70, 6.18, 5.55, 0.48), 950),
            ],
            "PBKDF2 Password Verification": [
                ("A salted, iterated verifier supports local password checks; it does not protect credentials sent over plaintext TCP.", (0.70, 6.18, 5.55, 0.48), 950),
            ],
            "Secure Message Workflow": [
                ("Intended sequence: authenticate, derive a key, encrypt and sign, verify, check the counter, then decrypt.", (1.05, 5.92, 11.05, 0.50), 1050),
            ],
            "Attack Demonstrations": [
                ("The three scenarios illustrate the simulator’s UI; the result screenshots and following interpretation slide describe the observed behavior.", (1.15, 5.92, 10.95, 0.50), 1050),
            ],
            "Interface: Login & Dashboard": [
                ("Dashboard: status cards and activity entries are interface content, not proof of a verified live session.", (0.72, 1.62, 7.25, 0.36), 950),
                ("Login", (8.15, 1.62, 1.88, 0.36), 900),
                ("Registration", (10.20, 1.62, 1.95, 0.36), 900),
            ],
            "Interface: Chat & Keys": [
                ("Secure Chat form and displayed send result.", (0.78, 1.75, 5.65, 0.42), 1000),
                ("Cryptographic Keys information screen.", (6.85, 1.75, 5.65, 0.42), 1000),
            ],
            "Interface: Simulator & Activity Logs": [
                ("Attack simulator controls.", (0.83, 1.75, 4.05, 0.42), 1000),
                ("Activity log view; entries are UI-reported events.", (5.05, 1.75, 7.20, 0.42), 1000),
            ],
            "Attack Result Screenshots": [
                ("Eavesdropping: local packet display shows ciphertext, not plaintext.", (0.48, 1.83, 3.70, 0.70), 900),
                ("Tampering: changed ciphertext no longer matches its signature; server returns SIGNATURE_INVALID.", (4.82, 1.83, 3.70, 0.70), 900),
                ("Replay: duplicate counter is rejected; server returns REPLAY_ATTACK_DETECTED.", (9.15, 1.83, 3.70, 0.70), 900),
            ],
        }
        for title, entries in figure_captions.items():
            slide_no = slide_no_by_title[title]
            slide = parse_xml(files[f"ppt/slides/slide{slide_no}.xml"])
            for index, (caption, box, size) in enumerate(entries, start=1):
                add_caption(slide, caption, box, f"Figure Caption {index}", size)
            files[f"ppt/slides/slide{slide_no}.xml"] = xml_bytes(slide)

        # Registration page pairs the visual flow with concise implementation facts.
        registration_no = slide_no_by_title["Registration & Login"]
        s8 = parse_xml(files[f"ppt/slides/slide{registration_no}.xml"])
        body = slide_shape(s8, "Content Placeholder 2")
        set_box(body, (7.30, 2.05, 5.05, 4.45))
        registration_index = registration_no - 2
        set_bullets(body, SLIDES[registration_index][1], 1500)
        files[f"ppt/slides/slide{registration_no}.xml"] = xml_bytes(s8)

        for title, font_size in [
            ("ECDH + HKDF Key Agreement", 1350),
            ("AES-256-GCM Encryption", 1300),
            ("RSA-PSS Signatures & Replay", 1250),
            ("PBKDF2 Password Verification", 1250),
        ]:
            crypto_no = slide_no_by_title[title]
            crypto_slide = parse_xml(files[f"ppt/slides/slide{crypto_no}.xml"])
            crypto_body = slide_shape(crypto_slide, "Content Placeholder 2")
            set_box(crypto_body, (6.50, 2.00, 5.90, 4.55))
            set_bullets(crypto_body, SLIDES[crypto_no - 2][1], font_size)
            files[f"ppt/slides/slide{crypto_no}.xml"] = xml_bytes(crypto_slide)

        with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as out:
            for path, data in files.items():
                out.writestr(path, data)
    print(OUTPUT)


if __name__ == "__main__":
    build()

from pathlib import Path
import subprocess
from xml.sax.saxutils import escape

OUT = Path(__file__).parent
BG, INK, MUTED = "#fbf7fa", "#38243a", "#725d74"
PINK, LAV, BLUE, GREEN, GOLD, RED = "#d85b98", "#f5e5ef", "#e8edff", "#e6f4ef", "#fff2d9", "#fde8e8"


def svg(name, title, subtitle, width, height, body):
    s = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<defs><marker id="arrow" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 Z" fill="{PINK}"/></marker><filter id="shadow" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="4" stdDeviation="5" flood-color="#4b2840" flood-opacity=".12"/></filter></defs>
<rect width="100%" height="100%" rx="28" fill="{BG}"/><text x="40" y="52" font-family="Arial,sans-serif" font-size="27" font-weight="700" fill="{INK}">{escape(title)}</text><text x="40" y="80" font-family="Arial,sans-serif" font-size="14" fill="{MUTED}">{escape(subtitle)}</text>{body}</svg>'''
    p = OUT / f"{name}.svg"
    p.write_text(s)
    subprocess.run(["convert", "-background", "none", str(p), str(OUT / f"{name}.png")], check=True)


def box(x, y, w, h, title, desc, fill=LAV, badge=None):
    extra = f'<rect x="{x+14}" y="{y+13}" width="7" height="{h-26}" rx="4" fill="{PINK}"/>'
    badge_svg = f'<text x="{x+w-16}" y="{y+26}" text-anchor="end" font-family="Arial" font-size="10" font-weight="700" fill="{PINK}">{badge}</text>' if badge else ""
    return f'<g filter="url(#shadow)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{fill}" stroke="#eadbe6"/>{extra}{badge_svg}<text x="{x+34}" y="{y+34}" font-family="Arial" font-size="16" font-weight="700" fill="{INK}">{escape(title)}</text><text x="{x+34}" y="{y+57}" font-family="Arial" font-size="11" fill="{MUTED}">{escape(desc)}</text></g>'


def arrow(x1, y1, x2, y2, label=None, dashed=False):
    line = f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{PINK}" stroke-width="2.5" marker-end="url(#arrow)"'+(' stroke-dasharray="6 5"' if dashed else '')+'/>'
    if label:
        line += f'<text x="{(x1+x2)/2}" y="{(y1+y2)/2-8}" text-anchor="middle" font-family="Arial" font-size="10" font-weight="700" fill="{MUTED}">{escape(label)}</text>'
    return line


# Overall application and trust boundary
b = box(40,125,180,76,"User","Login / register",LAV)+box(265,125,210,76,"PySide6 dashboard","Chat · keys · attacks · logs",LAV)+box(520,125,205,76,"Client","Packet + crypto operations",BLUE)+box(795,125,205,76,"TCP server","Authentication + validation",GREEN)
b += arrow(220,163,265,163)+arrow(475,163,520,163)+arrow(725,163,795,163,"TCP · JSON lines")
b += '<rect x="490" y="231" width="530" height="150" rx="20" fill="#fff" stroke="#e8dce5" stroke-dasharray="6 5"/><text x="515" y="258" font-family="Arial" font-size="13" font-weight="700" fill="'+INK+'">Protected communication path</text>'
b += box(515,278,145,68,"ECDH","SECP256R1 → shared key",BLUE)+box(685,278,145,68,"AES-256-GCM","Encrypt + authenticate",LAV)+box(855,278,145,68,"RSA-2048","Sign + verify packet",GOLD)
b += arrow(660,312,685,312)+arrow(830,312,855,312)
b += box(40,278,180,68,"Account store","Local users.json",GOLD)+box(265,278,190,68,"PBKDF2-SHA256","Salted GUI registration",GOLD)
b += arrow(220,312,265,312)
b += '<text x="40" y="420" font-family="Arial" font-size="11" fill="'+MUTED+'">Code note: GUI registration uses salted PBKDF2; server auth.py currently checks a separate SHA-256 record format.</text>'
svg("system_architecture", "System Architecture", "Layered client–server design described in the report", 1060, 460, b)

# Registration flow
b = box(45,145,185,78,"Registration form","Username + password",LAV)+box(285,145,190,78,"Random salt","16 bytes per account",BLUE)+box(530,145,215,78,"PBKDF2-HMAC-SHA256","100,000 iterations",GOLD)+box(800,145,210,78,"Local user record","Store salt + derived hash",GREEN)
b += arrow(230,184,285,184)+arrow(475,184,530,184)+arrow(745,184,800,184)
b += box(165,300,230,78,"Login form","Enter username + password",LAV)+box(470,300,235,78,"Derive again","Use stored salt + same KDF",BLUE)+box(780,300,205,78,"Compare","Accept or reject login",GREEN)
b += arrow(395,339,470,339)+arrow(705,339,780,339)+arrow(905,223,700,300,"stored salt + hash",True)
b += '<text x="45" y="430" font-family="Arial" font-size="11" fill="'+MUTED+'">This diagram follows register.py’s GUI flow. auth.py currently uses unsalted SHA-256, so the server login path is not yet aligned.</text>'
svg("registration_flow", "Registration & Login", "Password storage flow documented for the PySide6 registration interface", 1060, 480, b)

# Secure message workflow
b = box(35,145,150,78,"Authenticate","Username + password",LAV)+box(220,145,165,78,"ECDH exchange","SECP256R1 public keys",BLUE)+box(420,145,160,78,"Session key","HKDF-SHA256",BLUE)+box(615,145,165,78,"Encrypt","AES-256-GCM",LAV)+box(815,145,175,78,"Sign packet","RSA-PSS / SHA-256",GOLD)
b += arrow(185,184,220,184)+arrow(385,184,420,184)+arrow(580,184,615,184)+arrow(780,184,815,184)
b += box(800,300,205,78,"TCP packet","Counter · nonce · cipher · sig",BLUE)+box(615,300,165,78,"Verify signature","Client RSA public key",GOLD)+box(420,300,160,78,"Replay check","Reject counter ≤ last",RED)+box(220,300,165,78,"Decrypt","AES-GCM tag check",GREEN)+box(35,300,150,78,"Accept","Deliver plaintext",GREEN)
b += arrow(900,223,900,300)+arrow(815,339,780,339)+arrow(615,339,580,339)+arrow(420,339,385,339)+arrow(220,339,185,339)
b += '<text x="35" y="430" font-family="Arial" font-size="11" fill="'+MUTED+'">The counter is checked before AES-GCM decryption. Any signature, replay, or authentication-tag failure rejects the packet.</text>'
svg("secure_message_workflow", "Secure Message Workflow", "Client-to-server packet creation and validation", 1040, 480, b)

# Attack simulation
b = box(50,150,195,86,"Client","Creates protected packet",BLUE)+box(390,150,230,86,"Network observation","Attacker can see TCP traffic",GOLD)+box(795,150,205,86,"Server","Verifies before delivery",GREEN)
b += arrow(245,193,390,193,"encrypted packet")+arrow(620,193,795,193,"forward / modify / replay")
b += box(70,315,250,90,"Eavesdropping","Captured ciphertext · plaintext stays hidden",BLUE)+box(405,315,250,90,"Tampering","Changed bytes · signature or GCM check fails",RED)+box(740,315,250,90,"Replay","Old counter · packet rejected",GOLD)
b += '<path d="M505 236 C505 265 195 265 195 315" fill="none" stroke="#b69caf" stroke-width="1.5" stroke-dasharray="5 5"/><path d="M505 236 L530 315" fill="none" stroke="#b69caf" stroke-width="1.5" stroke-dasharray="5 5"/><path d="M505 236 C505 265 865 265 865 315" fill="none" stroke="#b69caf" stroke-width="1.5" stroke-dasharray="5 5"/>'
b += '<text x="50" y="455" font-family="Arial" font-size="11" fill="'+MUTED+'">Attack demonstrations follow attacks.py and the client/server verification order.</text>'
svg("attack_simulation", "Attack Simulation", "Three demonstrations and the expected security outcome", 1050, 490, b)

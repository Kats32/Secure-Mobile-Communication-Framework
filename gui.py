from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QDialog,
)

from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtCore import Qt


class Dashboard(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Secure Mobile Communication Framework")
        self.resize(1500, 900)

        # -------------------------------------------------
        # FIND MARBLE IMAGE AUTOMATICALLY
        # -------------------------------------------------

        assets_folder = Path(__file__).resolve().parent / "assets"

        image_extensions = [
            "*.png",
            "*.jpg",
            "*.jpeg",
            "*.webp"
        ]

        self.background = QPixmap()

        for extension in image_extensions:

            images = list(assets_folder.glob(extension))

            if images:
                self.background = QPixmap(str(images[0]))
                break

        # -------------------------------------------------
        # MAIN LAYOUT
        # -------------------------------------------------

        main_layout = QHBoxLayout(self)

        main_layout.setContentsMargins(22, 22, 22, 22)
        main_layout.setSpacing(16)

        # -------------------------------------------------
        # SIDEBAR
        # -------------------------------------------------

        sidebar = QFrame()

        sidebar.setFixedWidth(220)

        sidebar.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 235);
                border-radius: 22px;
            }
        """)

        sidebar_layout = QVBoxLayout(sidebar)

        sidebar_layout.setContentsMargins(16, 20, 16, 20)
        sidebar_layout.setSpacing(12)

        # Logo

        logo = QLabel("✮")

        logo.setAlignment(Qt.AlignCenter)

        logo.setStyleSheet("""
            QLabel {
                color: #e44d87;
                font-size: 34px;
                font-weight: bold;
                background: transparent;
            }
        """)

        sidebar_layout.addWidget(logo)

        # Title

        title = QLabel("SECURE\nCOMMUNICATION")

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            QLabel {
                color: #52203f;
                font-size: 16px;
                font-weight: bold;
                letter-spacing: 1px;
                background: transparent;
            }
        """)

        sidebar_layout.addWidget(title)

        subtitle = QLabel("HYBRID CRYPTOGRAPHIC\nFRAMEWORK")

        subtitle.setAlignment(Qt.AlignCenter)

        subtitle.setStyleSheet("""
            QLabel {
                color: #c65a83;
                font-size: 8px;
                letter-spacing: 1px;
                background: transparent;
            }
        """)

        sidebar_layout.addWidget(subtitle)

        sidebar_layout.addSpacing(22)

        # -------------------------------------------------
        # SIDEBAR BUTTONS
        # -------------------------------------------------

        buttons = [
            "Dashboard",
            "Secure Chat",
            "Cryptographic Keys",
            "Attack Simulator",
            "Security Tests",
            "Activity Logs",
        ]

        for text in buttons:

            button = QPushButton("◆  " + text)

            button.setCursor(Qt.PointingHandCursor)

            button.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 10px;
                    border: none;
                    border-radius: 8px;
                    color: #602448;
                    background: transparent;
                    font-size: 12px;
                }

                QPushButton:hover {
                    background-color: rgba(228, 77, 135, 35);
                }
            """)

            if text == "Attack Simulator":

                button.clicked.connect(
                    self.show_attack_simulator
                )

            sidebar_layout.addWidget(button)

        sidebar_layout.addStretch()

        # Version

        version = QLabel("v1.0  •  SECURE SYSTEM")

        version.setAlignment(Qt.AlignCenter)

        version.setStyleSheet("""
            QLabel {
                color: #c87999;
                font-size: 8px;
                background: transparent;
            }
        """)

        sidebar_layout.addWidget(version)

        main_layout.addWidget(sidebar)

        # -------------------------------------------------
        # CONTENT AREA
        # -------------------------------------------------

        content = QWidget()

        content.setAttribute(
            Qt.WA_TranslucentBackground
        )

        content_layout = QVBoxLayout(content)

        content_layout.setContentsMargins(
            0, 0, 0, 0
        )

        content_layout.setSpacing(16)

        # -------------------------------------------------
        # HEADER
        # -------------------------------------------------

        header_layout = QHBoxLayout()

        heading = QLabel("Security Dashboard")

        heading.setStyleSheet("""
            QLabel {
                color: #542040;
                font-size: 48px;
                font-weight: bold;
                background: transparent;
            }
        """)

        header_layout.addWidget(heading)

        header_layout.addStretch()

        online = QFrame()

        online.setFixedSize(135, 70)

        online.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 235);
                border-radius: 15px;
            }
        """)

        online_layout = QHBoxLayout(online)

        status_dot = QLabel("●")

        status_dot.setStyleSheet("""
            QLabel {
                color: #d83f79;
                font-size: 14px;
                background: transparent;
            }
        """)

        status_text = QLabel("SYSTEM ONLINE")

        status_text.setStyleSheet("""
            QLabel {
                color: #d83f79;
                font-size: 10px;
                font-weight: bold;
                background: transparent;
            }
        """)

        online_layout.addWidget(status_dot)
        online_layout.addWidget(status_text)

        header_layout.addWidget(online)

        content_layout.addLayout(header_layout)

        # -------------------------------------------------
        # WELCOME TEXT
        # -------------------------------------------------

        welcome = QLabel(
            "Welcome back. Your secure communication environment is ready.\n"
        )

        welcome.setStyleSheet("""
            QLabel {
                color: #542040;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)

        content_layout.addWidget(welcome)

        content_layout.addSpacing(55)

        # -------------------------------------------------
        # SECURITY CARDS
        # -------------------------------------------------

        cards_layout = QHBoxLayout()

        cards_layout.setSpacing(12)

        cards = [
            ("◧", "AES ENCRYPTION", "ACTIVE"),
            ("◧", "ECDH KEY EXCHANGE", "ACTIVE"),
            ("✦", "RSA SIGNATURE", "VERIFIED"),
        ]

        for icon_text, title_text, status in cards:

            card = QPushButton()

            card.setCursor(Qt.PointingHandCursor)

            card.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 235);
                    border: none;
                    border-radius: 18px;
                    text-align: left;
                    padding: 0px;
                }

                QPushButton:hover {
                    background-color: rgba(255, 245, 250, 245);
                    border: 1px solid rgba(216, 63, 121, 80);
                }

                QPushButton:pressed {
                    background-color: rgba(250, 230, 240, 245);
                }
            """)

            card.setFixedHeight(145)

            card_layout = QVBoxLayout(card)

            card_layout.setContentsMargins(
                18, 16, 18, 16
            )

            card_layout.setSpacing(6)

            icon = QLabel(icon_text)

            icon.setStyleSheet("""
                QLabel {
                    color: #111111;
                    font-size: 22px;
                    background: transparent;
                }
            """)

            card_layout.addWidget(icon)

            card_title = QLabel(title_text)

            card_title.setStyleSheet("""
                QLabel {
                    color: #542040;
                    font-size: 10px;
                    font-weight: bold;
                    background: transparent;
                }
            """)

            card_layout.addWidget(card_title)

            card_layout.addStretch()

            card_status = QLabel("● " + status)

            card_status.setStyleSheet("""
                QLabel {
                    color: #d83f79;
                    font-size: 10px;
                    font-weight: bold;
                    background: transparent;
                }
            """)

            card_layout.addWidget(card_status)

            card.clicked.connect(
                lambda checked=False,
                name=title_text:
                self.show_crypto_details(name)
            )

            cards_layout.addWidget(card)

        content_layout.addLayout(cards_layout)

        # -------------------------------------------------
        # SECURITY STATUS
        # -------------------------------------------------

        security_frame = QFrame()

        security_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 235);
                border-radius: 18px;
            }
        """)

        security_layout = QVBoxLayout(security_frame)

        security_layout.setContentsMargins(
            20, 16, 20, 16
        )

        security_layout.setSpacing(8)

        security_title = QLabel("SECURITY STATUS")

        security_title.setStyleSheet("""
            QLabel {
                color: #542040;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
        """)

        security_layout.addWidget(security_title)

        security_items = [
            ("Authentication", "VERIFIED"),
            ("ECDH Key Exchange", "SECURE"),
            ("Message Encryption", "ACTIVE"),
            ("Replay Protection", "ENABLED"),
            ("Tamper Detection", "ENABLED"),
        ]

        for item, status in security_items:

            row = QHBoxLayout()

            left = QLabel("●  " + item)

            left.setStyleSheet("""
                QLabel {
                    color: #8b4b69;
                    font-size: 11px;
                    background: transparent;
                }
            """)

            right = QLabel(status)

            right.setAlignment(Qt.AlignRight)

            right.setStyleSheet("""
                QLabel {
                    color: #d83f79;
                    font-size: 10px;
                    font-weight: bold;
                    background: transparent;
                }
            """)

            row.addWidget(left)
            row.addStretch()
            row.addWidget(right)

            security_layout.addLayout(row)

        content_layout.addWidget(security_frame)

        # -------------------------------------------------
        # RECENT ACTIVITY
        # -------------------------------------------------

        activity_frame = QFrame()

        activity_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 235);
                border-radius: 18px;
            }
        """)

        activity_layout = QVBoxLayout(activity_frame)

        activity_layout.setContentsMargins(
            20, 16, 20, 16
        )

        activity_layout.setSpacing(8)

        activity_title = QLabel("RECENT ACTIVITY")

        activity_title.setStyleSheet("""
            QLabel {
                color: #542040;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
        """)

        activity_layout.addWidget(activity_title)

        activities = [
            ("22:41", "ECDH key exchange completed"),
            ("22:42", "Secure session established"),
            ("22:43", "Message encryption activated"),
            ("22:44", "RSA signature verified"),
        ]

        for time, message in activities:

            activity = QLabel(
                "◆  " + time + "    " + message
            )

            activity.setStyleSheet("""
                QLabel {
                    color: #9a607c;
                    font-size: 10px;
                    padding: 2px;
                    background: transparent;
                }
            """)

            activity_layout.addWidget(activity)

        content_layout.addWidget(activity_frame)

        main_layout.addWidget(content)

    # =====================================================
    # ATTACK SIMULATOR
    # =====================================================

    def show_attack_simulator(self):

        dialog = QDialog(self)

        dialog.setWindowTitle(
            "Attack Simulator"
        )

        dialog.setFixedSize(
            600,
            560
        )

        dialog.setStyleSheet("""
            QDialog {
                background-color: #fff7fb;
                border-radius: 20px;
            }

            QLabel {
                background: transparent;
            }

            QPushButton {
                background-color: #d83f79;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px;
                font-size: 11px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #c52f68;
            }

            QPushButton:pressed {
                background-color: #a92355;
            }
        """)

        layout = QVBoxLayout(dialog)

        layout.setContentsMargins(
            35, 30, 35, 30
        )

        layout.setSpacing(15)

        # Title

        logo = QLabel("⚠")

        logo.setAlignment(Qt.AlignCenter)

        logo.setStyleSheet("""
            QLabel {
                color: #d83f79;
                font-size: 32px;
                font-weight: bold;
            }
        """)

        layout.addWidget(logo)

        title = QLabel(
            "ATTACK SIMULATOR"
        )

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            QLabel {
                color: #542040;
                font-size: 24px;
                font-weight: bold;
            }
        """)

        layout.addWidget(title)

        description = QLabel(
            "Select an attack to simulate against the secure session."
        )

        description.setAlignment(Qt.AlignCenter)

        description.setStyleSheet("""
            QLabel {
                color: #9a607c;
                font-size: 11px;
            }
        """)

        layout.addWidget(description)

        layout.addSpacing(10)

        # -------------------------------------------------
        # EAVESDROPPING
        # -------------------------------------------------

        eavesdrop_button = QPushButton(
            "◉   EAVESDROPPING\n"
            "     Capture encrypted communication"
        )

        eavesdrop_button.setFixedHeight(75)

        eavesdrop_button.clicked.connect(
            self.simulate_eavesdropping
        )

        layout.addWidget(eavesdrop_button)

        # -------------------------------------------------
        # TAMPERING
        # -------------------------------------------------

        tamper_button = QPushButton(
            "✦   TAMPERING\n"
            "     Modify encrypted message"
        )

        tamper_button.setFixedHeight(75)

        tamper_button.clicked.connect(
            self.simulate_tampering
        )

        layout.addWidget(tamper_button)

        # -------------------------------------------------
        # REPLAY
        # -------------------------------------------------

        replay_button = QPushButton(
            "↻   REPLAY ATTACK\n"
            "     Resend captured message"
        )

        replay_button.setFixedHeight(75)

        replay_button.clicked.connect(
            self.simulate_replay
        )

        layout.addWidget(replay_button)

        layout.addStretch()

        close_button = QPushButton("CLOSE")

        close_button.setFixedWidth(120)

        close_button.clicked.connect(
            dialog.close
        )

        layout.addWidget(
            close_button,
            alignment=Qt.AlignCenter
        )

        dialog.exec()

    # =====================================================
    # ATTACK PLACEHOLDERS
    # =====================================================

    def simulate_eavesdropping(self):

        self.show_attack_result(
            "Eavesdropping Attack",
            "Encrypted packet captured.\n\n"
            "The attacker can observe ciphertext,\n"
            "but the plaintext remains protected.",
            "✓ Confidentiality protected"
        )

    def simulate_tampering(self):

        self.show_attack_result(
            "Tampering Attack",
            "Ciphertext modification detected.\n\n"
            "The modified message failed the\n"
            "integrity verification.",
            "✓ Message rejected\n"
            "✓ Integrity protected"
        )

    def simulate_replay(self):

        self.show_attack_result(
            "Replay Attack",
            "Previously captured message detected.\n\n"
            "The message counter prevents reuse\n"
            "of an earlier authenticated message.",
            "✓ Replay rejected\n"
            "✓ Replay protection active"
        )

    # =====================================================
    # ATTACK RESULT DIALOG
    # =====================================================

    def show_attack_result(
        self,
        attack_type,
        description,
        result
    ):

        dialog = QDialog(self)

        dialog.setWindowTitle(
            "Attack Detected"
        )

        dialog.setFixedSize(
            520,
            420
        )

        dialog.setStyleSheet("""
            QDialog {
                background-color: #fff7fb;
            }

            QLabel {
                background: transparent;
            }

            QPushButton {
                background-color: #d83f79;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 25px;
                font-size: 11px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #c52f68;
            }
        """)

        layout = QVBoxLayout(dialog)

        layout.setContentsMargins(
            30, 25, 30, 25
        )

        layout.setSpacing(12)

        alert = QLabel("⚠")

        alert.setAlignment(Qt.AlignCenter)

        alert.setStyleSheet("""
            QLabel {
                color: #d83f79;
                font-size: 38px;
                font-weight: bold;
            }
        """)

        layout.addWidget(alert)

        heading = QLabel(
            "ATTACK DETECTED"
        )

        heading.setAlignment(Qt.AlignCenter)

        heading.setStyleSheet("""
            QLabel {
                color: #542040;
                font-size: 22px;
                font-weight: bold;
            }
        """)

        layout.addWidget(heading)

        attack = QLabel(
            "Type:  " + attack_type
        )

        attack.setStyleSheet("""
            QLabel {
                color: #d83f79;
                font-size: 13px;
                font-weight: bold;
            }
        """)

        layout.addWidget(attack)

        info = QLabel(description)

        info.setWordWrap(True)

        info.setStyleSheet("""
            QLabel {
                color: #8b4b69;
                font-size: 11px;
                padding: 10px;
            }
        """)

        layout.addWidget(info)

        result_label = QLabel(
            "RESULT\n\n" + result
        )

        result_label.setStyleSheet("""
            QLabel {
                color: #542040;
                background-color: rgba(216, 63, 121, 20);
                border-radius: 12px;
                padding: 15px;
                font-size: 11px;
                font-weight: bold;
            }
        """)

        layout.addWidget(result_label)

        layout.addStretch()

        close_button = QPushButton("CLOSE")

        close_button.clicked.connect(
            dialog.close
        )

        layout.addWidget(
            close_button,
            alignment=Qt.AlignCenter
        )

        dialog.exec()

    # =====================================================
    # CRYPTO DETAILS
    # =====================================================

    def show_crypto_details(self, crypto_type):

        dialog = QDialog(self)

        dialog.setWindowTitle(crypto_type)

        dialog.setFixedSize(
            480,
            430
        )

        dialog.setStyleSheet("""
            QDialog {
                background-color: #fff7fb;
                border-radius: 20px;
            }

            QLabel {
                background: transparent;
            }

            QPushButton {
                background-color: #d83f79;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 25px;
                font-size: 11px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #c52f68;
            }
        """)

        layout = QVBoxLayout(dialog)

        layout.setContentsMargins(
            30, 25, 30, 25
        )

        layout.setSpacing(12)

        logo = QLabel("✦")

        logo.setAlignment(Qt.AlignCenter)

        logo.setStyleSheet("""
            QLabel {
                color: #d83f79;
                font-size: 30px;
                font-weight: bold;
            }
        """)

        layout.addWidget(logo)

        title = QLabel(crypto_type)

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            QLabel {
                color: #542040;
                font-size: 20px;
                font-weight: bold;
            }
        """)

        layout.addWidget(title)

        if crypto_type == "AES ENCRYPTION":

            details = [
                ("STATUS", "ACTIVE"),
                ("ALGORITHM", "AES-256-GCM"),
                ("PURPOSE", "Message Encryption"),
                ("CONFIDENTIALITY", "PROTECTED"),
                ("INTEGRITY", "VALID"),
                ("SESSION", "SECURE"),
            ]

        elif crypto_type == "ECDH KEY EXCHANGE":

            details = [
                ("STATUS", "COMPLETED"),
                ("CURVE", "SECP256R1"),
                ("PURPOSE", "Secure Key Exchange"),
                ("SHARED KEY", "ESTABLISHED"),
                ("SESSION KEY", "ACTIVE"),
                ("KEY EXCHANGE", "SECURE"),
            ]

        else:

            details = [
                ("STATUS", "VERIFIED"),
                ("ALGORITHM", "RSA-2048"),
                ("PURPOSE", "Digital Signature"),
                ("SIGNATURE", "VALID"),
                ("AUTHENTICATION", "SUCCESS"),
                ("INTEGRITY", "VERIFIED"),
            ]

        for label_text, value_text in details:

            row = QHBoxLayout()

            label = QLabel(label_text)

            label.setStyleSheet("""
                QLabel {
                    color: #9a607c;
                    font-size: 10px;
                    font-weight: bold;
                }
            """)

            value = QLabel(value_text)

            value.setAlignment(Qt.AlignRight)

            value.setStyleSheet("""
                QLabel {
                    color: #d83f79;
                    font-size: 10px;
                    font-weight: bold;
                }
            """)

            row.addWidget(label)
            row.addStretch()
            row.addWidget(value)

            layout.addLayout(row)

        layout.addStretch()

        close_button = QPushButton("CLOSE")

        close_button.setCursor(
            Qt.PointingHandCursor
        )

        close_button.clicked.connect(
            dialog.close
        )

        layout.addWidget(
            close_button,
            alignment=Qt.AlignCenter
        )

        dialog.exec()

    # =====================================================
    # DRAW MARBLE BACKGROUND
    # =====================================================

    def paintEvent(self, event):

        painter = QPainter(self)

        if not self.background.isNull():

            scaled = self.background.scaled(
                self.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )

            x = (
                self.width() -
                scaled.width()
            ) // 2

            y = (
                self.height() -
                scaled.height()
            ) // 2

            painter.drawPixmap(
                x,
                y,
                scaled
            )

        else:

            painter.fillRect(
                self.rect(),
                Qt.GlobalColor.lightGray
            )

        painter.end()


# ---------------------------------------------------------
# RUN APPLICATION
# ---------------------------------------------------------

if __name__ == "__main__":

    app = QApplication([])

    app.setStyle("Fusion")

    window = Dashboard()

    window.show()

    app.exec()
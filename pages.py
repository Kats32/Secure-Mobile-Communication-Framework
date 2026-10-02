from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLineEdit,
    QMessageBox
)

from PySide6.QtCore import Qt

from client import create_secure_packet


# =========================================================
# COMMON PAGE STYLE
# =========================================================

class BasePage(QWidget):

    def __init__(self):
        super().__init__()

        self.setAttribute(
            Qt.WA_TranslucentBackground
        )

    def create_title(self, text, subtitle):
        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            25, 25, 25, 25
        )

        layout.setSpacing(10)

        title = QLabel(text)

        title.setStyleSheet("""
            QLabel {
                color: #542040;
                font-size: 42px;
                font-weight: bold;
                background: transparent;
            }
        """)

        layout.addWidget(title)

        description = QLabel(subtitle)

        description.setStyleSheet("""
            QLabel {
                color: #8b4b69;
                font-size: 16px;
                background: transparent;
            }
        """)

        layout.addWidget(description)

        return layout


# =========================================================
# SECURE CHAT
# =========================================================

class SecureChatPage(BasePage):

    def __init__(self, dashboard):
        super().__init__()

        self.dashboard = dashboard

        layout = self.create_title(
            "Secure Chat",
            "Send a message through the secure communication framework."
        )

        layout.addSpacing(20)

        card = QFrame()

        card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 235);
                border-radius: 18px;
            }
        """)

        card_layout = QVBoxLayout(card)

        card_layout.setContentsMargins(
            25, 25, 25, 25
        )

        card_layout.setSpacing(15)

        heading = QLabel(
            "SECURE MESSAGE"
        )

        heading.setStyleSheet("""
            QLabel {
                color: #542040;
                font-size: 18px;
                font-weight: bold;
                background: transparent;
            }
        """)

        card_layout.addWidget(heading)

        self.username = QLineEdit()

        self.username.setPlaceholderText(
            "Username"
        )

        self.username.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 245, 250, 240);
                border: 1px solid rgba(216, 63, 121, 70);
                border-radius: 10px;
                padding: 12px;
                color: #542040;
                font-size: 14px;
            }
        """)

        card_layout.addWidget(
            self.username
        )

        self.password = QLineEdit()

        self.password.setPlaceholderText(
            "Password"
        )

        self.password.setEchoMode(
            QLineEdit.Password
        )

        self.password.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 245, 250, 240);
                border: 1px solid rgba(216, 63, 121, 70);
                border-radius: 10px;
                padding: 12px;
                color: #542040;
                font-size: 14px;
            }
        """)

        card_layout.addWidget(
            self.password
        )

        self.message = QLineEdit()

        self.message.setPlaceholderText(
            "Enter secure message"
        )

        self.message.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 245, 250, 240);
                border: 1px solid rgba(216, 63, 121, 70);
                border-radius: 10px;
                padding: 12px;
                color: #542040;
                font-size: 14px;
            }
        """)

        card_layout.addWidget(
            self.message
        )

        send_button = QPushButton(
            "SEND SECURE MESSAGE"
        )

        send_button.setCursor(
            Qt.PointingHandCursor
        )

        send_button.setStyleSheet("""
            QPushButton {
                background-color: #d83f79;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 13px;
                font-size: 13px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #c52f68;
            }
        """)

        send_button.clicked.connect(
            self.send_message
        )

        card_layout.addWidget(
            send_button
        )

        layout.addWidget(card)

        layout.addStretch()

    def send_message(self):

        username = self.username.text().strip()
        password = self.password.text().strip()
        message = self.message.text().strip()

        if not username or not password or not message:

            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter username, password and message."
            )

            return

        try:

            packet = create_secure_packet(
                username,
                password,
                message
            )

            self.dashboard.last_packet = packet

            self.dashboard.add_activity(
                "Secure chat message encrypted"
            )

            QMessageBox.information(
                self,
                "Secure Communication",
                "Message encrypted successfully."
            )

            self.message.clear()

        except Exception as error:

            self.dashboard.add_activity(
                "Secure chat communication failed"
            )

            QMessageBox.critical(
                self,
                "Communication Error",
                str(error)
            )


# =========================================================
# CRYPTOGRAPHIC KEYS
# =========================================================

class CryptoKeysPage(BasePage):

    def __init__(self, dashboard):
        super().__init__()

        self.dashboard = dashboard

        layout = self.create_title(
            "Cryptographic Keys",
            "Cryptographic mechanisms used by the secure communication framework."
        )

        layout.addSpacing(20)

        self.add_crypto_card(
            layout,
            "AES-256-GCM",
            "MESSAGE ENCRYPTION",
            "Provides confidentiality and integrity for secure messages."
        )

        self.add_crypto_card(
            layout,
            "ECDH SECP256R1",
            "KEY EXCHANGE",
            "Establishes a shared session key between communicating users."
        )

        self.add_crypto_card(
            layout,
            "RSA-2048",
            "DIGITAL SIGNATURE",
            "Provides authentication and message integrity verification."
        )

        layout.addStretch()

    def add_crypto_card(
        self,
        layout,
        algorithm,
        purpose,
        description
    ):

        card = QPushButton()

        card.setCursor(
            Qt.PointingHandCursor
        )

        card.setFixedHeight(115)

        card.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 235);
                border: none;
                border-radius: 18px;
                text-align: left;
                padding: 15px;
            }

            QPushButton:hover {
                background-color: rgba(255, 245, 250, 245);
                border: 1px solid rgba(216, 63, 121, 80);
            }
        """)

        card_layout = QVBoxLayout(card)

        title = QLabel(
            algorithm + "   •   " + purpose
        )

        title.setStyleSheet("""
            QLabel {
                color: #542040;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
            }
        """)

        card_layout.addWidget(title)

        info = QLabel(
            description
        )

        info.setWordWrap(True)

        info.setStyleSheet("""
            QLabel {
                color: #8b4b69;
                font-size: 13px;
                background: transparent;
            }
        """)

        card_layout.addWidget(info)

        card.clicked.connect(
            lambda checked=False,
            name=self.get_dashboard_crypto_name(
                algorithm
            ):
            self.dashboard.show_crypto_details(name)
        )

        layout.addWidget(card)

    def get_dashboard_crypto_name(self, algorithm):

        if algorithm == "AES-256-GCM":
            return "AES ENCRYPTION"

        if algorithm == "ECDH SECP256R1":
            return "ECDH KEY EXCHANGE"

        return "RSA SIGNATURE"

# =========================================================
# ACTIVITY LOGS
# =========================================================

class ActivityLogsPage(BasePage):

    def __init__(self, dashboard):
        super().__init__()

        self.dashboard = dashboard

        self.layout = self.create_title(
            "Activity Logs",
            "Complete history of security and communication events."
        )

        self.layout.addSpacing(20)

        self.log_frame = QFrame()

        self.log_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 235);
                border-radius: 18px;
            }
        """)

        self.log_layout = QVBoxLayout(
            self.log_frame
        )

        self.log_layout.setContentsMargins(
            20, 20, 20, 20
        )

        self.log_layout.setSpacing(8)

        self.layout.addWidget(
            self.log_frame
        )

        self.layout.addStretch()

    def refresh(self):

        while self.log_layout.count():

            item = self.log_layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        if not hasattr(
            self.dashboard,
            "activity_history"
        ):

            label = QLabel(
                "No activity recorded yet."
            )

            label.setStyleSheet("""
                QLabel {
                    color: #9a607c;
                    font-size: 14px;
                    background: transparent;
                }
            """)

            self.log_layout.addWidget(label)

            return

        if not self.dashboard.activity_history:

            label = QLabel(
                "No activity recorded yet."
            )

            label.setStyleSheet("""
                QLabel {
                    color: #9a607c;
                    font-size: 14px;
                    background: transparent;
                }
            """)

            self.log_layout.addWidget(label)

            return

        for timestamp, message in reversed(
            self.dashboard.activity_history
        ):

            activity = QLabel(
                "◆  " +
                timestamp +
                "    " +
                message
            )

            activity.setStyleSheet("""
                QLabel {
                    color: #8b4b69;
                    font-size: 13px;
                    padding: 5px;
                    background: transparent;
                }
            """)

            self.log_layout.addWidget(
                activity
            )
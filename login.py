import json
import os
import hashlib
import binascii

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox
)
from PySide6.QtCore import Qt

from register import RegisterDialog


USERS_FILE = "users.json"


def load_users():
    if not os.path.exists(USERS_FILE):
        return {}

    try:
        with open(USERS_FILE, "r") as file:
            return json.load(file)
    except:
        return {}


def verify_password(password, salt_hex, stored_hash):

    salt = binascii.unhexlify(salt_hex)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        100000
    )

    calculated_hash = binascii.hexlify(password_hash).decode()

    return calculated_hash == stored_hash


class LoginWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Secure Mobile Communication Framework"
        )

        self.setFixedSize(500, 600)

        self.setStyleSheet("""
            QWidget {
                background: #f9edf4;
            }

            QLabel {
                color: #542040;
            }

            QLineEdit {
                background: white;
                border: 1px solid #d8a8c1;
                border-radius: 10px;
                padding: 13px;
                font-size: 15px;
                color: #542040;
            }

            QLineEdit:focus {
                border: 2px solid #b84f87;
            }

            QPushButton {
                background: #602448;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 13px;
                font-size: 15px;
                font-weight: bold;
            }

            QPushButton:hover {
                background: #7b315b;
            }

            QPushButton#registerButton {
                background: transparent;
                color: #602448;
                border: 1px solid #d8a8c1;
            }

            QPushButton#registerButton:hover {
                background: #f0d9e5;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(55, 50, 55, 50)
        layout.setSpacing(15)

        logo = QLabel("✮")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("""
            font-size: 42px;
            color: #602448;
        """)

        title = QLabel("SECURE\nCOMMUNICATION")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            letter-spacing: 1px;
        """)

        subtitle = QLabel(
            "HYBRID CRYPTOGRAPHIC FRAMEWORK"
        )
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 12px;
            color: #8a6075;
        """)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        login_button = QPushButton("LOGIN")
        login_button.clicked.connect(self.login)

        register_button = QPushButton("CREATE NEW ACCOUNT")
        register_button.setObjectName("registerButton")
        register_button.clicked.connect(self.open_register)

        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addWidget(subtitle)

        layout.addSpacing(30)

        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)

        layout.addSpacing(10)

        layout.addWidget(login_button)
        layout.addWidget(register_button)

        layout.addStretch()

        self.setLayout(layout)

        self.dashboard = None

    def open_register(self):

        dialog = RegisterDialog(self)

        if dialog.exec():
            self.username_input.clear()
            self.password_input.clear()
            self.username_input.setFocus()

    def login(self):

        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(
                self,
                "Login",
                "Please enter your username and password."
            )
            return

        users = load_users()

        if username not in users:
            QMessageBox.warning(
                self,
                "Login Failed",
                "Invalid username or password."
            )
            return

        user_data = users[username]

        if not verify_password(
            password,
            user_data["salt"],
            user_data["password_hash"]
        ):
            QMessageBox.warning(
                self,
                "Login Failed",
                "Invalid username or password."
            )
            return

        self.open_dashboard(username)

    def open_dashboard(self, username):

        from dashboard import Dashboard

        self.dashboard = Dashboard(username)
        self.dashboard.show()

        self.close()


if __name__ == "__main__":

    app = QApplication([])

    app.setStyle("Fusion")

    window = LoginWindow()
    window.show()

    app.exec()
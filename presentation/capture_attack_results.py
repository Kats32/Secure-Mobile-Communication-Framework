"""Capture current attack-result dialogs from an isolated local demo run."""

import contextlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

PRESENTATION_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PRESENTATION_DIR.parent
OUTPUT_DIR = PRESENTATION_DIR / "attack_results"
PYTHON = PROJECT_ROOT / ".venv/bin/python"


def main():
    sys.path.insert(0, str(PROJECT_ROOT))
    import auth

    original_user_file = auth.USER_FILE
    server = None
    try:
        with tempfile.TemporaryDirectory(prefix="smcf-attack-capture-") as temp_dir:
            auth.USER_FILE = str(Path(temp_dir) / "users.json")
            username = "presentation-capture-user"
            password = "temporary-capture-password"
            if not auth.register(username, password):
                raise RuntimeError("Could not create the temporary capture account")

            environment = os.environ.copy()
            environment["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + environment.get("PYTHONPATH", "")
            server = subprocess.Popen(
                [str(PYTHON), "-u", str(PROJECT_ROOT / "server.py")],
                cwd=temp_dir,
                env=environment,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(0.6)
            if server.poll() is not None:
                raise RuntimeError("The temporary server did not start on localhost:5000")

            from client import send_message
            from attacks import eavesdropping_demo, replay_demo, tampering_demo

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                packet = send_message(
                    username=username,
                    password=password,
                    message="Confidential demo message",
                )
            eavesdropping = eavesdropping_demo(packet)
            tampering = tampering_demo(packet, username, password)
            replay = replay_demo(packet, username, password)
            if tampering["status"] != "BLOCKED" or replay["status"] != "BLOCKED":
                raise RuntimeError(f"Attack checks did not block as expected: {tampering}, {replay}")

            from PySide6.QtCore import QTimer
            from PySide6.QtWidgets import QApplication
            from dashboard import Dashboard

            application = QApplication.instance() or QApplication([])
            dashboard = Dashboard(username)
            dashboard.show()
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

            def capture_dialog(result, filename):
                destination = OUTPUT_DIR / filename

                def capture_when_ready():
                    dialog = application.activeModalWidget()
                    if dialog is None:
                        QTimer.singleShot(50, capture_when_ready)
                        return
                    if not dialog.grab().save(str(destination)):
                        raise RuntimeError(f"Could not save {destination}")
                    dialog.accept()

                QTimer.singleShot(100, capture_when_ready)
                dashboard.show_attack_result(result)
                if not destination.exists():
                    raise RuntimeError(f"Dialog was not captured: {destination}")
                print(f"Captured {destination.name}")

            capture_dialog(eavesdropping, "eavesdropping.png")
            capture_dialog(tampering, "tampering.png")
            capture_dialog(replay, "replay.png")
            dashboard.close()
            print("Tampering result:", tampering["result"])
            print("Replay result:", replay["result"])
    finally:
        auth.USER_FILE = original_user_file
        if server is not None:
            server.terminate()
            try:
                server.wait(timeout=2)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait()


if __name__ == "__main__":
    main()

# GUI Screenshots for the Project Report

Capture the application screens below and save them in a `screenshots/` folder in the project directory. Use PNG format and keep the application window fully visible.

## Run the GUI

From the project directory, activate the virtual environment and launch the login window:

```bash
source .venv/bin/activate
python login.py
```

If dependencies are not installed in the environment yet:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install PySide6 cryptography
python login.py
```

Create a demo account from **CREATE NEW ACCOUNT**, then log in to open the dashboard.

## Required Screenshots

| Suggested filename | Screen to capture | How to open it |
| --- | --- | --- |
| `login.png` | Login screen | Capture the first screen after running `login.py`. |
| `registration.png` | Registration screen | Click **CREATE NEW ACCOUNT**. |
| `dashboard.png` | Main Security Dashboard | Log in with the demo account. |
| `secure_chat.png` | Secure Chat page | Choose **Secure Chat** in the dashboard navigation. |
| `cryptographic_keys.png` | Cryptographic Keys page | Choose **Cryptographic Keys**. |
| `attack_simulator.png` | Attack Simulator | Choose **Attack Simulator**. |
| `attack_eavesdropping_result.png` | Eavesdropping result | From the simulator, choose **EAVESDROPPING**, then enter the demo account credentials and a sample message. |
| `attack_tampering_result.png` | Tampering result | Open the simulator and choose **TAMPERING**, then enter the credentials and a sample message. |
| `attack_replay_result.png` | Replay result | Open the simulator and choose **REPLAY ATTACK**, then enter the credentials and a sample message. |
| `activity_logs.png` | Activity Logs page | Choose **Activity Logs** after running the attack demonstrations. |

The attack demonstrations use TCP communication. Before taking those result screenshots, start the server in another terminal from the project directory:

```bash
source .venv/bin/activate
python server.py
```

Keep the server terminal running while you use the simulator. The GUI account and server now use the same salted PBKDF2 record format.

## Capture and Add to the Report

- **Windows:** Press **Win + Shift + S**, select the application window, then save the capture as the filename in the table.
- **macOS:** Press **Cmd + Shift + 4**, then press **Space** and select the application window.
- **Linux:** Use **PrtScn** or the desktop screenshot utility and choose the application window.

Use a sample message such as `Report demonstration message`. Avoid showing real passwords or personal information. In Word, replace each matching screenshot placeholder with its image; the architecture diagrams are already embedded in the report.

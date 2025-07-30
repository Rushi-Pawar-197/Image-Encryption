# 🔐 Image Encryption Tool

Securely encrypt and decrypt images using **AES-256** and **RSA-4096** with a hardened QR-based key-sharing mechanism and a single master code for protection.

---

## 🚀 Features

- 📂 **Encrypts any image folder** and compresses into a `.zip`
- 🔑 **Generates strong RSA key pair** (4096-bit)
- 🔒 **Encrypts using AES-256**, AES key protected via RSA
- 📄 **Saves key info as obfuscated, base64-encoded QR code**
- 🧠 **Single master code (e.g., `3248-7110-9831`)** derives hidden secrets (no need to store keys)
- 🧪 **Decryption recovers original images in seconds**
- ❌ **No password on ZIP** – master code is the only secret needed
- 🌈 **Beautiful terminal output with `rich`** for clarity

---

## 🧰 Setup Instructions

Make sure you're using **Python 3.8+** and run the following to get started:

```bash
# Clone this repo and navigate to the project
python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

---

## 🧠 How It Works

### 1. Encryption

```bash
python main.py
```

- Choose option `1` to Send
- 🔐 RSA keys are generated (`d`, `n`)
- 🤯 These keys are **mathematically dirtied** using A & B derived from a 12-digit master code
- 🔒 AES encrypts each image
- 🗃️ Encrypted AES key is stored alongside encrypted `.bin` files in a ZIP
- 📄 Keys (now dirty) are saved in **obfuscated JSON → base64 → QR**
- ✅ Final master code like `1994-6211-1540` is shown only once!

📦 **Output:**
```
output/send/archive.zip      # Contains encrypted files + AES key (RSA-encrypted)
output/send/qr_code.png      # Contains encrypted RSA private key (dirty)
```

---

### 2. Decryption

```bash
python main.py
```

- Choose option `2` to Receive
- Paste the **12-digit master code**
- 🔓 RSA private key is **undirtied** using A & B from master code
- 🧠 AES key is decrypted
- 📂 Images are fully recovered

📂 **Output:**
```
output/receive/*.png
```

---

## 🔐 Security Architecture

| Layer | Algorithm | Strength |
|-------|-----------|----------|
| RSA   | 4096 bits | Military-grade public-key encryption |
| AES   | 256 bits  | Secure symmetric encryption |
| Obfuscation | Base64 + reverse + noise | Hides actual key structure in QR |
| Master Secret | 12-digit code → A & B | Secret never saved anywhere |
| QR Encoding | Holds encoded key data | Human-shareable, machine-protected |

🛡️ **Even if ZIP and QR are leaked, without the master code, decrypting is infeasible.**

---

## 💬 Example Run

```
🛡️   Choose your action:
    [1]   🔐  Send    
    [2]   🔓  Receive 
    [3]   🚪  Clean-up
    [4]   🚪  Exit    

>: 1

🔐 Generating RSA keys...
📄 --> Keys-QR code saved to: output/send/qr_code.png
📦 --> Zip created at: output/send/archive.zip
🛡️  Master code  : 1994-6211-1540
```

```
>: 2

🛡️  Paste master code here : 1994-6211-1540

📦 <-- Zip extracted at: output/bin
🔑 <-- Keys loaded from: output/send/qr_code.png
✅🔓  Decrypted in 3s   ⏱
```

---

## 🧼 Clean-up (Optional)

Choose option `3` from the menu to empty all intermediate directories, including the '/data' directory.

---

## 📌 Final Notes

- Only **master code** must be kept safe.
- QR and zip can be transmitted publicly.
- Designed for **personal or research-grade secure communication.**
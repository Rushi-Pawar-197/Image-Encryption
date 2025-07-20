# 🔐 RSA Image Encryption Project

A Python project to encrypt and decrypt images using RSA encryption, with optional ZIP compression and QR code-based key sharing.

---

## 🚀 Features

- 🔑 RSA key generation
- 🖼️ Image encryption and decryption
- 🗜️ ZIP compression with password protection
- 📷 QR code generation and scanning for key sharing
- ✔️ File integrity check using hash verification

---

## 🛠️ Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/yourusername/rsa-image-encryption.git
cd rsa-image-encryption
pip install -r requirements.txt
```

## 📦 Use Case

This project is ideal for securely sharing sensitive images over untrusted networks by combining **RSA encryption**, **password-protected ZIP compression**, and **QR-based key exchange**.

### 🔸 1. Sending Encrypted Images

Securely encrypt and prepare images for transfer:

- 📁 **Input**: Place image(s) in the `data/` directory.
- ▶️ **Run**: `python send.py`
- 📦 **Output** (in `output/send/`):
  - `encrypted_images.zip`: Password-protected ZIP file containing RSA-encrypted images.
  - `key_qr.png`: QR code with the encrypted RSA keys for secure transfer.

### 🔸 2. Receiving & Decrypting Images

Decrypt received files and restore original images:

- 📥 **Input**: Copy both `encrypted_images.zip` and `key_qr.png` into `output/send/`
- ▶️ **Run**: `python receive.py`
- 🖼️ **Output**: Decrypted image(s) saved to `output/receive/`

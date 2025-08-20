# 🔐 File Encryption Tool

A secure file encryption and decryption system built with **RSA-4096 + AES-256**, reinforced by a **random 12-digit Master Code**. The Master Code is transformed into a **48-character derived string**, which is then used to construct key material (`A` and `B`) that provides additional layers of protection.

This ensures that even if RSA/AES keys were somehow accessed directly, without the correct Master Code and mapping logic, decryption is infeasible.

---

## ✨ Features

* **Hybrid Encryption:** Combines RSA-4096 (for key encapsulation) with AES-256 (for file encryption).
* **Master Code Protection:** 12-digit Master Code → 3 × 4-digit segments → mapped to 16-character strings → concatenated into a **48-char string**, which is then used to construct key materials `A` and `B`.
* **Random Master Code Generation:** Each encryption run generates a fresh Master Code and keypair.
* **Cross-Platform:** Works on any system with Python 3.11+.
* **Rich CLI Interface:** Emoji + styled logging for clarity.
* **Automatic Packaging:** Encrypted files and metadata bundled into a ZIP.
* **Clean-up Utility:** Removes data and all temporary files after operation. (Useful for a clean start)

---

## 🚀 Quick Start

1. Place files inside `/data/`
2. Run: `python main.py`
3. Share the generated `bundle.zip` + Master Code
4. Receiver runs `python main.py` with `bundle.zip` → files restored

---

## ⚠️ File Size Note

* Encryption/decryption works best up to \~1.5 GB files on an 8 GB RAM system.
* Very large files (e.g., 4 GB videos) may fail due to memory limits.
* Actual limit depends on available RAM.

---

## 🔒 Security

* **RSA-4096 + AES-256 Hybrid Encryption**
* **Master Code Strength:** 12-digit Master Code = 10^12 combinations.
* **Derived String Strength:** Each Master Code maps to a **48-char string**, expanding entropy dramatically.
* **Combined Security Estimate:** RSA-4096 + AES-256 + Master Code entropy + derived 48-char mappings.
* **Independence:** Each encryption run generates a fresh RSA-4096 + AES-256 keypair.
* **Master Code Safety:** The Master Code is randomly generated during encryption. Even if by chance the same Master Code appears in two sessions, they remain cryptographically independent and secure.
* ⚠️ **If the Master Code is lost, files cannot be recovered.**

---

| Component                  | Role in Encryption                                    | Strength / Entropy                                                                   |
| -------------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------ |
| **RSA-4096**               | Protects AES key and ensures secure key exchange      | \~150+ bits equivalent classical security (considered unbreakable with current tech) |
| **AES-256**                | Encrypts file contents (any file format, byte-level)  | 256-bit symmetric security                                                           |
| **12-digit Master Code**   | User input for key derivation, mapped to lookup table | 10¹² combinations (\~40 bits)                                                        |
| **48-char Derived String** | Generated from Master Code via lookup mapping         | Extremely high entropy (≈ 280 bits depending on charset)                             |
| **Combined System**        | Hybrid of RSA + AES + Master Code + Lookup            | Practically unbreakable without correct Master Code                                  |


---

## 🛠️ Extensibility

* Extend preprocessing in `utility.py` to support directories instead of flat files.
* Modify Rich config in `utility.py` to customize logging style.

---

## 📦 File Structure

```
/project-root
│── main.py              # Entry point
│── codebase/
│   ├── constants.py     # Fixed values & mappings
│   ├── data_processing.py  # Encryption/Decryption logic
│   ├── utility.py       # Logging, helpers, cleanup
│   └── __init__.py
│
│── data/                # Input files for encryption
│── output/              # Encrypted/Decrypted results
```

---

## ⚡ Example Run

**Encryption:**

```
>: 1
🚀 Initiating Encryption
📦 Files collected
🔑 Master Code generated: 9037-9602-1574
📦 Bundle created at /output/send/bundle.zip
```

**Decryption (with wrong Master Code):**

```
>: 2
🚀 Initiating Decryption
📦 <-- Zip extracted
🔑 <-- Keys loaded
⚠️   RSA decryption unsuccessful
🔑  Could not retrieve AES key
💥  Execution aborted
💡  Verify the Master-code and try again
```

---

## 🗑️ Clean-up

Removes all files in '/data', all temporary archives and bin files after send/receive to keep the environment safe.

---

## 📜 License

MIT License. Free to use and modify.

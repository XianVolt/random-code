"""
Simple text encryption/decryption tool.

Install the dependency first:
    python -m pip install cryptography

Run:
    python encryption.py
"""

import base64
import getpass
import os

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def make_fernet(password: str, salt: bytes) -> Fernet:
    """Create an encryption key from the password and a random salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600_000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))
    return Fernet(key)


def encrypt_text(text: str, password: str) -> str:
    salt = os.urandom(16)
    cipher = make_fernet(password, salt)
    encrypted = cipher.encrypt(text.encode("utf-8")).decode("ascii")
    # Save the salt with the encrypted text; the password is never saved.
    return salt.hex() + ":" + encrypted


def decrypt_text(data: str, password: str) -> str:
    salt_hex, encrypted = data.strip().split(":", 1)
    salt = bytes.fromhex(salt_hex)
    cipher = make_fernet(password, salt)
    return cipher.decrypt(encrypted.encode("ascii")).decode("utf-8")


def main() -> None:
    print("=== TEXT ENCRYPTION TOOL ===")
    print("1. Encrypt text")
    print("2. Decrypt text")

    choice = input("Choose 1 or 2: ").strip()

    if choice == "1":
        message = input("\nEnter the text to encrypt: ")
        password = getpass.getpass("Create a password: ")
        if not password:
            print("Password cannot be empty.")
            return

        result = encrypt_text(message, password)
        print("\nENCRYPTED TEXT (copy and save this):")
        print(result)

    elif choice == "2":
        data = input("\nPaste the encrypted text: ").strip()
        password = getpass.getpass("Enter the password: ")

        try:
            result = decrypt_text(data, password)
            print("\nDECRYPTED TEXT:")
            print(result)
        except (ValueError, InvalidToken, UnicodeDecodeError):
            print("Could not decrypt. Check the encrypted text and password.")

    else:
        print("Invalid choice. Please choose 1 or 2.")


if __name__ == "__main__":
    main()

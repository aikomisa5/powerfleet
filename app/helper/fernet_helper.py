import os

from cryptography.fernet import Fernet

# Assuming 'fernet_key' is loaded securely
DB_SECRET_KEY = os.getenv("DB_SECRET_KEY")
fernet = Fernet(DB_SECRET_KEY)


def encrypt_data(data: str) -> bytes:
    return fernet.encrypt(data.encode())


def decrypt_data(encrypted_data: bytes) -> str:
    return fernet.decrypt(encrypted_data).decode()
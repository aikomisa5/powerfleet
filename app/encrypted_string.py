from sqlalchemy.types import TypeDecorator, LargeBinary
from sqlalchemy import text
from sqlalchemy.orm import Session

class EncryptedString(TypeDecorator):
    impl = LargeBinary

    def __init__(self, *args, **kwargs):
        self.key = kwargs.pop("key")
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        """ Se ejecuta al guardar -> cifra """
        if value is None:
            return None
        # Se encripta en Python, no con SQL
        from cryptography.fernet import Fernet
        f = Fernet(self.key)
        return f.encrypt(value.encode())


def process_result_value(self, value, dialect):
        """ Se ejecuta al leer -> descifra """
        if value is None:
            return None
        from cryptography.fernet import Fernet
        f = Fernet(self.key)
        return f.decrypt(value).decode()

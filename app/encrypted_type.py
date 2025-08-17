from sqlalchemy.types import TypeDecorator, LargeBinary
from app.helper.fernet_helper import encrypt_data, decrypt_data


# Assuming 'fernet_instance' is your initialized Fernet object
class EncryptedType(TypeDecorator):
    impl = LargeBinary  # Store as binary in the database

    def process_bind_param(self, value, dialect):
        if value is not None:
            return encrypt_data(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return decrypt_data(value)
        return value
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
        # usamos función de Postgres directamente
        return Session.object_session(self)._execute_clauseelement(
            text("SELECT pgp_sym_encrypt(:value, :key)").bindparams(value=value, key=self.key)
        ).scalar()

    def process_result_value(self, value, dialect):
        """ Se ejecuta al leer -> descifra """
        if value is None:
            return None
        return Session.object_session(self)._execute_clauseelement(
            text("SELECT pgp_sym_decrypt(:value, :key)").bindparams(value=value, key=self.key)
        ).scalar()

import bcrypt
class PasswordEncrytor:
    
    @classmethod
    def encrypt(cls, password:str, *params) -> str:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return password_hash

    @classmethod
    def validate(cls, password:str, password_hash:str):
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
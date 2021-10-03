class PasswordEncrytor:
    
    @classmethod
    def encrypt(cls, password:str, **params) -> str:
        return password[::-1]
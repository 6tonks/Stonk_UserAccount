class PasswordValidator:
    
    @classmethod
    def is_valid(cls, password:str, **params) -> bool:
        return len(password) < 256 and len(password) > 4
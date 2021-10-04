import re

class PasswordValidator:
    
    @classmethod
    def is_valid(cls, password:str, **params) -> bool:
        valid_length = len(password) < 256 and len(password) > 8
        
        symbols = set("~`! @#$%^&*()_-+={[}]|\:;\"'<,>.?/")
        has_symbol = any(c in symbols for c in password)
        has_numeric = re.search('\d', password) is not None
        has_upper = re.search('[A-Z]', password) is not None
        has_lower = re.search('[a-z]', password) is not None

        return all((valid_length, has_symbol, has_numeric, has_upper, has_lower))
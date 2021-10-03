
from typing import Optional

#----------TESTING ONLY------------------
USERS = []

class UsersModel:

    @classmethod
    def create(cls, name, email, password_hash):
        USERS.append({'id': len(USERS), "name": name, "email": email, "password": password_hash})
        print(f"Created {name}, {email}, {password_hash}")
        return

    @classmethod
    def find_by_template(cls, template):
        return [user for user in USERS if all(user[key] == value\
             for key, value in template.items() if value is not None)]

class UserException(Exception):
    pass

class UserNameExistsException(Exception):
    pass

class UserEmailExistsException(Exception):
    pass

#------------------------------------------

class PasswordValidator:
    
    @classmethod
    def is_valid(cls, password:str, **params) -> bool:
        return len(password) < 256 and len(password) > 4

class PasswordEncrytor:
    
    @classmethod
    def encrypt(cls, password:str, **params) -> str:
        return password[::-1]

class UserResource:

    @classmethod
    def create(cls, user_args, address_args = {}):
        if any(field is None for field in user_args.values()):
            return {'status': 404}
        
        password = user_args['password']
        if not PasswordValidator.is_valid(password):
            return {'status': 404}

        password_hash = PasswordEncrytor.encrypt(password)
        try:
            UsersModel.create(user_args['name'], user_args['email'], password_hash)
            return {'status': 200}
        except UserNameExistsException:
            return {'status': 404}
        except UserEmailExistsException:
            return {'status': 404}

    @classmethod
    def find(cls, user_args = {}, address_args = {}):
        users = UsersModel.find_by_template(user_args)
        return {"result": users, "status": 200}

    @classmethod
    def find_by_id(cls, _id):
        return cls.find(user_args = {'id': _id})
    
    @classmethod
    def update(cls, _id, **template):
        raise NotImplementedError
    
    @classmethod
    def delete(cls, _id, password):
        raise NotImplementedError
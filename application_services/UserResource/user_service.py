
from typing import Dict, List, Optional

from database_services.BaseUserModel import BaseUserModel, UserEmailExistsException

#----------TESTING ONLY------------------
USERS = {}

class UsersModel(BaseUserModel):

    @classmethod
    def create(cls, name, email, password_hash):
        if any(user['email'] == email for user in USERS.values()):
            raise UserEmailExistsException()

        new_user = {"id": len(USERS), "name": name, "email": email, "pwHash": password_hash}
        USERS[new_user['id']] = new_user
        return new_user

    @classmethod
    def find_by_template(cls, template):
        return [user for user in USERS.values() if all(user[key] == value\
             for key, value in template.items() if value is not None)]

    @classmethod
    def find_by_address(cls, user_args: Dict[str, str], address_args: Dict[str, str]) \
            -> List[Dict[str, str]]:
        raise NotImplementedError()

    @classmethod
    def update(cls, _id: str, user_args: Dict[str, str]) -> Dict[str, str]:
        if int(_id) not in USERS:
            return

        user = USERS[int(_id)]
        user.update(user_args)
        return user

    @classmethod
    def delete(cls, _id: str) -> None:
        if int(_id) not in USERS:
            return

        del USERS[_id]
        return

#------------------------------------------

class PasswordValidator:
    
    @classmethod
    def is_valid(cls, password:str, **params) -> bool:
        return len(password) < 256 and len(password) > 4

class PasswordEncrytor:
    
    @classmethod
    def encrypt(cls, password:str, **params) -> str:
        return password[::-1]

class UserResourceException(Exception):
    @classmethod
    def response(cls, message_args = {}, description_args = {}):
        return {
            "message": cls.message(**message_args), 
            "description": cls.description(**description_args)
        }

    @classmethod
    def message(cls):
        raise NotImplementedError()
    
    @classmethod
    def description(cls):
        raise NotImplementedError()

class InvalidPassword(UserResourceException):
    @classmethod
    def message(cls):
        return "Password is invalid."

    @classmethod
    def description(cls):
        return ""

class MissingRequiredFields(UserResourceException):
    @classmethod
    def message(cls):
        return "Required Fields are missing."

    @classmethod
    def description(cls, names = []):
        if names:
            return f"The following fields are missing: {', '.join(names)}."
        return ""

class AlreadyTakenValue(UserResourceException):
    @classmethod
    def message(cls, name):
        return f"{name} could not be registered."

    @classmethod
    def description(cls, name, value):
        return f"{value} for {name} has already been taken."

class UserNotFound(UserResourceException):
    @classmethod
    def message(cls):
        return "User not found."

    @classmethod
    def description(cls):
        return ""

class UserResource:

    @classmethod
    def create(cls, user_args, address_args = {}):

        # All fields in user args must be filled in
        if any(field is None for field in user_args.values()):
            missing = [name for name, value in user_args.items() if value is None]
            return MissingRequiredFields.response(description_args = {'names': missing}), 400
        
        password = user_args['password']
        if not PasswordValidator.is_valid(password):
            return InvalidPassword.response(), 400

        password_hash = PasswordEncrytor.encrypt(password)
        try:
            user = UsersModel.create(user_args['name'], user_args['email'], password_hash)
            return user, 201
        except UserEmailExistsException:
            return AlreadyTakenValue.response(
                message_args={'name': 'email'}, 
                description_args={'name':'email', 'value': user_args['email']}), 404

    @classmethod
    def find(cls, user_args = {}, address_args = {}):
        if "password" in user_args and user_args["password"] is not None:
            password = user_args["password"]
            password_hash = PasswordEncrytor.encrypt(password)
            del user_args["password"]
            user_args["pwHash"] = password_hash

        user_args = {f:v for f, v in user_args.items() if v is not None}
        address_args = {f:v for f, v in address_args.items() if v is not None}
        if len(address_args) == 0:
            users = UsersModel.find_by_template(user_args)
        else:
            users = UsersModel.find_by_address(user_args = user_args, address_args = address_args)

        for user in users:
            del user['pwHash']
        return {"users": users}, 200

    @classmethod
    def find_by_id(cls, _id):
        users, status = cls.find(user_args = {'id': _id})
        if status == 200 and len(users) == 1:
            return users['users'][0], 200
        elif status == 200:
            return UserNotFound.response(), 404
        return users, status
    
    @classmethod
    def update(cls, _id, user_args):
        user = UsersModel.update(_id, user_args)
        return user, 200
    
    @classmethod
    def delete(cls, _id, password):
        user = UsersModel.delete(_id)
        return user, 200

from typing import Dict, List, Optional
from database_services.BaseUserModel import BaseUserModel, UserEmailExistsException
from database_services.BaseAddressModel import BaseAddressModel

from dataclasses import dataclass

from password_encryption import PasswordEncrytor
from password_validation import PasswordValidator

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

@dataclass
class UserResource:
    user_model: BaseUserModel
    address_model: BaseAddressModel

    @classmethod
    def clean_users(cls, users):
        for user in users:
            if 'pwHash' in user:
                del user['pwHash']
        return users

    @classmethod
    def clean_user(cls, user):
        del user['pwHash']
        return user

    def create(self, user_args, address_args = {}):

        # All fields in user args must be filled in
        if any(field is None for field in user_args.values()):
            missing = [name for name, value in user_args.items() if value is None]
            return MissingRequiredFields.response(description_args = {'names': missing}), 400
        
        password = user_args['password']
        if not PasswordValidator.is_valid(password):
            return InvalidPassword.response(), 400

        password_hash = PasswordEncrytor.encrypt(password)
        try:
            user = self.user_model.create(user_args['name'], user_args['email'], password_hash)
            return self.clean_user(user), 201
        except UserEmailExistsException:
            return AlreadyTakenValue.response(
                message_args={'name': 'email'}, 
                description_args={'name':'email', 'value': user_args['email']}), 404

    def find(self, user_args = {}, address_args = {}):
        if "password" in user_args and user_args["password"] is not None:
            password = user_args["password"]
            password_hash = PasswordEncrytor.encrypt(password)
            del user_args["password"]
            user_args["pwHash"] = password_hash

        user_args = {f:v for f, v in user_args.items() if v is not None}
        address_args = {f:v for f, v in address_args.items() if v is not None}
        if len(address_args) == 0:
            users = self.user_model.find_by_template(user_args)
        else:
            users = self.user_model.find_by_address(user_args = user_args, address_args = address_args)
        return {"users": self.clean_users(users)}, 200

    def find_by_id(self, _id):
        users, status = self.find(user_args = {'id': _id})
        if status == 200 and len(users) == 1:
            return self.clean_user(users['users'][0]), 200
        elif status == 200:
            return UserNotFound.response(), 404
        return users, status
    
    def update(self, _id, user_args):
        user = self.user_model.update(_id, user_args)
        return self.clean_user(user), 200
    
    def delete(self, _id, password):
        user = self.user_model.delete(_id)
        return user, 200

    def find_address(self, _id):
        address = self.user_model.find_address(_id)
        return address, 200

    def update_address(self, _id, address_args):
        address = self.user_model.find_address(_id)
        new_address = self.address_model.update(address['id'], address_args)
        return new_address, 200
    
    def delete_address(self, _id, password):
        user = self.user_model.delete_address(_id)
        return self.clean_user(user), 200
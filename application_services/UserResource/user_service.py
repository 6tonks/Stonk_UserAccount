from typing import Tuple
from dataclasses import dataclass

from application_services.BaseResource import \
    BaseResource, InvalidArguement, ResourceError, sends_response, throws_resource_errors

from application_services.UserResource.Model.BaseUserModel import BaseUserModel, UserEmailExistsException
from database_services.BaseAddressModel import BaseAddressModel

from application_services.UserResource.password_encryption import PasswordEncrytor
from application_services.UserResource.password_validation import PasswordValidator

import re

class UserResourceError(ResourceError):
    code = 2000
    
    def __init__(self):
        super().__init__()

class InvalidEmail(UserResourceError, InvalidArguement):
    code = 2001
    message = "The given email is invalid"
    description = ""
    status = 400

class InvalidPassword(UserResourceError, InvalidArguement):
    code = 2002
    message = "The given password is invalid"
    description = ""
    status = 400

    def __init__(self):
        super().__init__()

class EmailAlreadyInUse(UserResourceError):
    code = 2003
    message = "The given email is already in use"
    description = ""
    status = 400

    def __init__(self):
        super().__init__()

class UserNotFound(UserResourceError):
    code = 2004
    message = "User not found"
    description = ""
    status = 404

    def __init__(self):
        super().__init__()

class IncorrectPassword(UserResourceError):
    code = 2005
    message = "Password is incorrect"
    description = ""
    status = 400

    def __init__(self):
        super().__init__()

class NoAccountWithEmail(UserResourceError):
    code = 2006
    message = "Could not find account with email"
    description = "Account with email {} is not registered"
    status = 400

    def __init__(self, email = None):
        super().__init__()
        if email is None:
            self.description = ""
        else:
            self.description = self.description.format(email)

@dataclass
class UserResource(BaseResource):
    user_model: BaseUserModel
    address_model: BaseAddressModel
    required_sign_up_fields: Tuple[str] = ('firstName', 'lastName', 'email', 'password')

    @classmethod
    def clean_users(cls, users):
        return [cls.clean_user(user) for user in users]

    @classmethod
    def clean_user(cls, user):
        if 'pwHash' in user:
            del user['pwHash']
        return user

    @throws_resource_errors
    def validate_email(self, email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.fullmatch(regex, email):
            yield InvalidEmail()

    @throws_resource_errors
    def validate_password(self, password):
        valid = PasswordValidator.is_valid(password)
        if not valid:
            yield InvalidPassword()

    @throws_resource_errors
    def verify_password(self, _id, password):
        users = self._find({"id": _id})
        yield users
        password_hash = users[0]['pwHash']

        if not PasswordEncrytor.validate(password, password_hash):
            yield IncorrectPassword()

    @throws_resource_errors
    def generate_user_creation_fields(self, user_args):
        yield self.ensure_fields_in_args(user_args, self.required_sign_up_fields)
        yield self.validate_email(user_args['email'])
        yield self.validate_password(user_args['password'])

        password_hash = PasswordEncrytor.encrypt(user_args['password'], user_args['email'])
        create_args = user_args.copy()
        del create_args['password']
        create_args['pwHash'] = password_hash

        yield create_args

    @throws_resource_errors
    def verify(self, user_args):
        """Valids the users information"""
        yield self.ensure_fields_in_args(user_args, ['email', 'password'])
        users = self._find(user_args)
        yield users

        if len(users) != 1:
            yield NoAccountWithEmail(user_args['email'])
        user = users.pop()

        user_password = user_args['password']
        user_password_hash = user['pwHash']
        if not PasswordEncrytor.validate(user_password, user_password_hash):
            yield IncorrectPassword()

        yield user

    @throws_resource_errors
    def _find(self, user_args = {}, address_args = {}):
        if "password" in user_args and user_args["password"] is not None:
            user_args = user_args.copy()
            del user_args["password"]

        user_args = {f:v for f, v in user_args.items() if v is not None}
        address_args = {f:v for f, v in address_args.items() if v is not None}

        if len(address_args) == 0:
            users = self.user_model.find_by_template(user_args)
        else:
            users = self.user_model.find_by_address(user_args = user_args, address_args = address_args)
        yield users

    @sends_response
    def create(self, user_args):
        create_user_fields = self.generate_user_creation_fields(user_args)
        yield create_user_fields

        try:
            user = self.user_model.create(create_user_fields)
            yield self.clean_user(user), 201
        except UserEmailExistsException:
            yield EmailAlreadyInUse()

    @sends_response
    def find(self, user_args = {}, address_args = {}):
        if "password" in user_args and user_args["password"] is not None:
            user_args = user_args.copy()
            del user_args["password"]

        user_args = {f:v for f, v in user_args.items() if v is not None}
        address_args = {f:v for f, v in address_args.items() if v is not None}

        if len(address_args) == 0:
            users = self.user_model.find_by_template(user_args)
        else:
            users = self.user_model.find_by_address(user_args = user_args, address_args = address_args)
        yield {"users": self.clean_users(users)}, 200

    @sends_response
    def find_by_id(self, _id):
        users = self._find(user_args = {'id': _id})
        yield users
        if len(users['users']) != 1:
            yield UserNotFound()
        yield self.clean_user(users['users'][0]), 200

    @sends_response
    def update(self, _id, user_args):
        yield self.ensure_fields_in_args(user_args, ["password"])
        yield self.verify_password(_id, user_args['password'])
        user = self.user_model.update(_id, user_args)
        yield self.clean_user(user), 200
    
    @throws_resource_errors
    def delete(self, _id, user_args):
        yield self.ensure_fields_in_args(user_args, ["password"])
        yield self.verify_password(_id, user_args['password'])
        user = self.user_model.delete(_id)
        yield user, 200

    @sends_response
    def find_address(self, _id):
        address = self.user_model.find_address(_id)
        yield address, 200

    @sends_response
    def update_address(self, _id, address_args):
        address = self.user_model.find_address(_id)
        new_address = self.address_model.update(address['id'], address_args)
        yield new_address, 200
    
    @sends_response
    def delete_address(self, _id, password):
        user = self.user_model.delete_address(_id)
        yield self.clean_user(user), 200
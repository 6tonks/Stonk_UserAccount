from typing import Tuple
from dataclasses import dataclass

from application_services.BaseResource import BaseResource, ResourceError, ResourceErrorCollection
from application_services.UserResource.Model.BaseUserModel import BaseUserModel, UserEmailExistsException
from database_services.BaseAddressModel import BaseAddressModel

from application_services.UserResource.password_encryption import PasswordEncrytor
from application_services.UserResource.password_validation import PasswordValidator

import re

class UserResourceError(ResourceError):
    code = 2000
    
    def __init__(self):
        super().__init__()

class InvalidEmail(UserResourceError):
    code = 2001
    message = "The given email is invalid"
    description = ""

class InvalidPassword(UserResourceError):
    code = 2002
    message = "The given password is invalid"
    description = ""

    def __init__(self):
        super().__init__()

class EmailAlreadyInUse(UserResourceError):
    code = 2003
    message = "The given email is already in use"
    description = ""

    def __init__(self):
        super().__init__()

class UserNotFound(UserResourceError):
    code = 2004
    message = "User not found"
    description = ""

    def __init__(self):
        super().__init__()

class IncorrectPassword(UserResourceError):
    code = 2005
    message = "Password is incorrect"
    description = ""

    def __init__(self):
        super().__init__()

class NoAccountWithEmail(UserResourceError):
    code = 2006
    message = "Could not find account with email"
    description = "Account with email {} is not registered"

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

    def validate_email(self, email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.fullmatch(regex, email):
            return False, ResourceErrorCollection(InvalidEmail())
        return True, None


    def validate_password(self, password):
        valid = PasswordValidator.is_valid(password)
        if not valid:
            return False, ResourceErrorCollection(InvalidPassword())
        return True, None

    def verify_password(self, _id, password):
        suc, users, error = self._find({"id": _id})
        if not suc:
            return False, error

        try:
            password_hash = users[0]['pwHash']
        except Exception:
            raise Exception(f"Could not find pwHash in {users}")
        if not PasswordEncrytor.validate(password, password_hash):
            return False, ResourceErrorCollection(IncorrectPassword())
        return True, None

    def sign_up(self, user_args):
        # required fields check
        suc, errors = self.ensure_fields_in_args(user_args, self.required_sign_up_fields)
        if not suc:
            return False, None, errors

        # validate emails
        suc, errors = self.validate_email(user_args['email'])
        if not suc:
            return False, None, errors

        # validate password
        suc, errors = self.validate_password(user_args['password'])
        if not suc:
            return False, None, errors

        password_hash = PasswordEncrytor.encrypt(user_args['password'], user_args['email'])
        create_args = user_args.copy()
        del create_args['password']
        create_args['pwHash'] = password_hash

        return True, create_args, None
    
    def verify(self, user_args):
        """Valids the users information"""
        suc, errors = self.ensure_fields_in_args(user_args, ['email', 'password'])
        if not suc:
            return False, None, errors

        suc, users, errors = self._find(user_args)
        if not suc:
            return False, None, errors
        if len(users) != 1:
            return False, None, ResourceErrorCollection(NoAccountWithEmail(user_args['email']))
        user = users.pop()

        suc, errors = self.verify_password(user['id'], user_args['password'])
        if not suc:
            return False, None, errors

        suc, users, error = self._find(user_args)
        if not suc:
            return False, None, errors
        return True, users[0], None

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
        return True, users, None

    def create(self, user_args):
        suc, create_user_fields, errors = self.sign_up(user_args)
        if not suc:
            return errors.response(), 400

        try:
            user = self.user_model.create(create_user_fields)
            return self.clean_user(user), 201
        except UserEmailExistsException:
            return ResourceErrorCollection(EmailAlreadyInUse()).response(), 404

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
        return {"users": self.clean_users(users)}, 200

    def find_by_id(self, _id):
        users, status = self.find(user_args = {'id': _id})
        if status == 200 and len(users['users']) == 1:
            return self.clean_user(users['users'][0]), 200
        elif status == 200:
            return ResourceErrorCollection(UserNotFound()).response(), 404
        return users, status

    def update(self, _id, user_args):
        suc, errors = self.required_sign_up_fields(user_args, ["password"])
        if not suc:
            return errors.response(), 400
        password = user_args['password']

        suc, errors = self.verify_password(_id, password)
        if not suc:
            return errors.response(), 404

        user = self.user_model.update(_id, user_args)
        return self.clean_user(user), 200
    
    def delete(self, _id, user_args):
        suc, errors = self.required_sign_up_fields(user_args, ["password"])
        if not suc:
            return errors.response(), 400
        password = user_args['password']

        suc, errors = self.verify_password(_id, password)
        if not suc:
            return errors.response(), 404

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
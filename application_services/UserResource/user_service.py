from typing import Tuple
from dataclasses import dataclass
from enum import Enum
from application_services.AddressResource.address_service import ADDRESS_ARGS

from application_services.BaseResource import \
    BaseResource, sends_response, throws_resource_errors
from application_services.UserResource.UserError import *

from application_services.UserResource.Model.BaseUserModel import BaseUserModel, UserEmailExistsException
from application_services.AddressResource.Model.BaseAddressModel import BaseAddressModel

from application_services.UserResource.password_encryption import PasswordEncrytor
from application_services.UserResource.password_validation import PasswordValidator

import re

class USER_ARGS(Enum):
    ID = 'userID'
    FIRST_NAME = 'nameFirst'
    LAST_NAME = 'nameLast'
    EMAIL = 'email'
    PASSWORD = "password"
    PASSWORD_HASH = "pwHash"
    ADDRESS_ID = "addressID"
    @property
    def str(self):
        return self.value

@dataclass
class UserResource(BaseResource):
    user_model: BaseUserModel
    address_model: BaseAddressModel
    required_sign_up_fields: Tuple[str] = (
        USER_ARGS.FIRST_NAME.str, 
        USER_ARGS.LAST_NAME.str,
        USER_ARGS.EMAIL.str,
        USER_ARGS.PASSWORD.str
    )
    allowed_response_fields: Tuple[str] = (
        USER_ARGS.ID.str,
        USER_ARGS.FIRST_NAME.str, 
        USER_ARGS.LAST_NAME.str,
        USER_ARGS.EMAIL.str,
        USER_ARGS.ADDRESS_ID.str,
    )


    @classmethod
    def clean_users(cls, users):
        return [cls.clean_user(user) for user in users]

    @classmethod
    def clean_user(cls, user):
        return {k: v for k, v in user.items() if k in cls.allowed_response_fields}

    @throws_resource_errors
    def validate_email(self, email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.fullmatch(regex, email):
            yield InvalidEmail()

    @throws_resource_errors
    def validate_password(self, password):
        if not PasswordValidator.is_valid(password):
            yield InvalidPassword()

    @throws_resource_errors
    def verify_password(self, _id, password):
        users = self._find({USER_ARGS.ID.str: _id})
        yield users
        password_hash = users[0][USER_ARGS.PASSWORD_HASH.str]

        if not PasswordEncrytor.validate(password, password_hash):
            yield IncorrectPassword()

    @throws_resource_errors
    def generate_user_creation_fields(self, user_args):
        yield self.ensure_fields_in_args(user_args, self.required_sign_up_fields)
        yield self.validate_email(user_args[USER_ARGS.EMAIL.str])
        yield self.validate_password(user_args[USER_ARGS.PASSWORD.str])

        password_hash = PasswordEncrytor.encrypt(user_args[USER_ARGS.PASSWORD.str], user_args[USER_ARGS.EMAIL.str])
        create_args = user_args.copy()
        del create_args[USER_ARGS.PASSWORD.str]
        create_args[USER_ARGS.PASSWORD_HASH.str] = password_hash

        yield create_args

    @throws_resource_errors
    def verify(self, user_args):
        """Valids the users information"""
        yield self.ensure_fields_in_args(user_args, [USER_ARGS.EMAIL.str, USER_ARGS.PASSWORD.str])
        users = self._find(user_args)
        yield users

        if len(users) != 1:
            yield NoAccountWithEmail(user_args[USER_ARGS.EMAIL.str])
        user = users.pop()

        user_password = user_args[USER_ARGS.PASSWORD.str]
        user_password_hash = user[USER_ARGS.PASSWORD_HASH.str]
        if not PasswordEncrytor.validate(user_password, user_password_hash):
            yield IncorrectPassword()

        yield user

    @throws_resource_errors
    def _find(self, user_args = {}, address_args = {}):
        if USER_ARGS.PASSWORD.str in user_args:
            user_args = user_args.copy()
            del user_args[USER_ARGS.PASSWORD.str]

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
        except UserEmailExistsException:
            yield EmailAlreadyInUse()
        
        user = self.clean_user(user)
        yield user, 201

    @sends_response
    def find(self, user_args = {}, address_args = {}):
        if USER_ARGS.PASSWORD.str in user_args and user_args[USER_ARGS.PASSWORD.str] is not None:
            user_args = user_args.copy()
            del user_args[USER_ARGS.PASSWORD.str]

        user_args = {f:v for f, v in user_args.items() if v is not None}
        address_args = {f:v for f, v in address_args.items() if v is not None}

        if len(address_args) == 0:
            users = self.user_model.find_by_template(user_args)
        else:
            users = self.user_model.find_by_address(user_args = user_args, address_args = address_args)
        yield {"users": self.clean_users(users)}, 200

    @sends_response
    def find_by_id(self, _id):
        users = self._find(user_args = {USER_ARGS.ID.str: _id})
        yield users
        if len(users) != 1:
            yield UserNotFound()
        yield self.clean_user(users[0]), 200

    @sends_response
    def update(self, _id, user_args):
        if USER_ARGS.PASSWORD.str in user_args and USER_ARGS.PASSWORD.str is not None:
            password_hash = PasswordEncrytor.encrypt(user_args[USER_ARGS.PASSWORD.str], user_args[USER_ARGS.EMAIL.str])
            user_args = user_args.copy()
            del user_args[USER_ARGS.PASSWORD.str]
            user_args[USER_ARGS.PASSWORD_HASH.str] = password_hash

        users = self.user_model.update(_id, user_args)
        yield self.clean_user(users[0]), 200
    
    @throws_resource_errors
    def delete(self, _id):
        users = self.user_model.delete(_id)
        if len(users):
            yield UserCouldNotBeRemoved()
        yield {'Sucessfully Removed': True}, 200

    @sends_response
    def find_address(self, _id):
        address = self.user_model.find_address(_id)
        yield address, 200

    @sends_response
    def update_address(self, _userId, address_args):
        print("update_address", _userId)
        print("update_address", address_args)
        #check if user have addressid, if yes, update address, else insert a new one
        userRecord = self.user_model.find_by_template({"userID":_userId})
        print(userRecord)

        addressID = userRecord[0]['addressID']
        new_address = None
        # no address, insert new record
        if addressID == 0:
            print("creating new address record for user, userID: ", _userId)
            addressID = self.address_model.create(address_args)
            print("new address record created, addressID: ", addressID)
            #also update user table
            self.user_model.update(_userId, {"addressID" : addressID})
        else: # update
            print("updating existing record")
            self.address_model.update(addressID, address_args)

        new_address = self.address_model.find_by_template({'addressID': addressID})
        yield new_address, 200
    
    @sends_response
    def delete_address(self, _id):
        user = self.user_model.delete_address(_id)
        yield self.clean_user(user), 200

    @sends_response
    def get_id_before_execute(self, user_args, func):
        users = self._find(user_args = user_args)
        yield users
        if len(users) != 1:
            yield UserNotFound()
        _id = users[0][USER_ARGS.ID.str]
        return func(_id)
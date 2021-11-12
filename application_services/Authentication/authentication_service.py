from dataclasses import dataclass
from application_services.Authentication.Model.BaseTokenModel import BaseTokenModel
from application_services.BaseResource import BaseResource, ResourceError, sends_response, sends_app_service_reponse
from application_services.UserResource.user_service import USER_ARGS, UserResource

from enum import Enum

class NoSuchToken(ResourceError):
    code = 5000
    message = "Could not find given token associated with the user"
    description = ""
    status = 404

class TOKEN_ARGS(Enum):
    TOKEN = 'token'

    @property
    def str(self):
        return self.value

@dataclass
class Authenticator(BaseResource):
    token_model: BaseTokenModel
    user_resource: UserResource

    @sends_app_service_reponse
    def get_user_id(self, user_id, user_args):
        if user_id is not None:
            yield user_id
            return

        user = self.user_resource.verify(user_args = user_args)
        yield user
        yield user[USER_ARGS.ID.str]

    @sends_response
    def create_token(self, user_id =  None, user_args = None):
        user_id = self.get_user_id(user_id, user_args)
        yield user_id
        res = {"user_id": user_id, "Authentication Token": self.token_model.create(user_id)}
        yield res, 200

    @sends_response
    def verify_before_execute(self, user_id = None, token_args = {}, func = None, user_args = None):
        user_id = self.get_user_id(user_id, user_args)
        yield user_id
        yield self.ensure_fields_in_args(token_args, [TOKEN_ARGS.TOKEN.str])

        if not self.token_model.validate(token_args[TOKEN_ARGS.TOKEN.str], user_id):
            yield NoSuchToken()

        yield func()

    @sends_response
    def validate_token(self, user_id = None, token_args = {}, user_args = None):
        yield self.verify_before_execute(
            user_id, token_args, 
            lambda : ({"Token Found": True}, 200), user_args
        )

    @sends_response
    def delete_token(self, user_id = None, token_args = {}, user_args = None):
        user_id = self.get_user_id(user_id, user_args)
        yield user_id
        yield self.ensure_fields_in_args(token_args, [TOKEN_ARGS.TOKEN.str])

        if not self.token_model.validate(token_args[TOKEN_ARGS.TOKEN.str], user_id):
            yield NoSuchToken()
        
        self.token_model.delete(token_args[TOKEN_ARGS.TOKEN.str])
        yield {"Token Removed": True}, 200
from os import error
from application_services.BaseResource import BaseResource, ResourceError, sends_response, throws_resource_errors

class NoSuchToken(ResourceError):
    code = 5000
    message = "Could not find given token associated with the user"
    description = ""
    status = 400

class Authenticator(BaseResource):

    def __init__(self, token_model):
        self.token_model = token_model

    @sends_response
    def create_token(self, user_params, user_resource):
        user = user_resource.verify(user_args = user_params)
        yield user
        res = {"Authentication Token": self.token_model.create(user['userID'])}
        yield res, 200


    @sends_response
    def validate_token(self, token, user_params, user_resource):
        user = user_resource.verify(user_args = user_params)
        yield user
        if not self.token_model.validate(token, user['id']):
            yield NoSuchToken()

        yield {"Token Found": True}, 200

    @sends_response
    def delete_token(self, token, user_params, user_resource):
        user = user_resource.verify(user_args = user_params)
        yield user
        if not self.token_model.validate(token, user['id']):
            yield NoSuchToken()
        
        self.token_model.delete(token)
        yield {"Token Removed": True}, 200
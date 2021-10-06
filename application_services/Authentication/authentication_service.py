from os import error
from application_services.BaseResource import BaseResource, ResourceError, ResourceErrorCollection

class NoSuchToken(ResourceError):
    code = 5000
    message = "Could not find given token associated with the user"
    description = ""

class Authenticator(BaseResource):

    def __init__(self, token_model):
        self.token_model = token_model

    def create_token(self, user_params, user_resource):
        suc, user, errors = user_resource.verify(user_args = user_params)
        if not suc:
            return errors.response(), 400

        res = {"Authentication Token": self.token_model.create(user['userID'])}
        return res, 200


    def validate_token(self, token, user_params, user_resource):
        suc, user, errors = user_resource.verify(user_args = user_params)
        if not suc:
            return errors.response(), 400

        is_valid = self.token_model.validate(token, user['id'])
        if not is_valid:
            return ResourceErrorCollection(NoSuchToken()).response(), 404

        return {"Token Found": True}, 200

    def delete_token(self, token, user_params, user_resource):
        suc, user, errors = user_resource.verify(user_args = user_params)
        if not suc:
            return errors.response(), 400

        if not self.token_model.validate(token, user['id']):
            return ResourceErrorCollection(NoSuchToken()).response(), 404
        
        self.token_model.delete(token)
        return {"Token Removed": True}, 200
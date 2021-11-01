import json
from utils import token_args
from application_services.Authentication.Model.RDSTokenModel import RDSTokenModel
import re

secure_paths = [
    "/users/102"
]
public_paths = [
    "/"
]


def check_security(request):#, google, blueprint):

    path = request.path
    result_ok = False

    if path in secure_paths:
        temp_token_dict = token_args()
        temp_id = re.search('(?<=\/users\/)[0-9]+', path).group()
        if temp_token_dict:
            temp_token = temp_token_dict['token']
            print(temp_token)
            if RDSTokenModel.validate(temp_token, temp_id):
                result_ok = True
    elif path in public_paths:
        result_ok = True
    else:
        result_ok = False
    return result_ok

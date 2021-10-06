from flask import Flask, Response, request

from application_services.UserResource.user_service import UserResource
from application_services.Authentication.authentication_service import Authenticator

import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)

#from application_services.tests.TestUserModel import TestUserModel
from application_services.UserResource.Model.RDSUserModel import RDSUserModel
from application_services.tests.TestAddressModel import TestAddressModel
#from application_services.Authentication.Model.TestTokenModel import TestTokenModel
from application_services.Authentication.Model.RDSTokenModel import RDSTokenModel
user_resource = UserResource(RDSUserModel(), TestAddressModel())
authenticator = Authenticator(RDSTokenModel)
@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

def user_args_from_route():
    return {field: request.args.get(field) for field in (
        "firstName",
        "lastName",
        "email",
        "password"
    )}

def address_args_from_route():
    return {field: request.args.get(field) for field in (
        "address_first_line",
        "address_second_line",
        "address_city",
        "address_state",
        "address_zip_code",
        "address_country_code"
    )}

@app.route('/users', methods=['POST', 'GET'])
def users_route():
    """
    GET := Returns all users that satisfy params
    POST := Creates a user with name, email and password

    Currently also handles signup through POST
    """
    user_params = user_args_from_route()
    address_params = address_args_from_route()

    if request.method == 'POST':
        res, status = user_resource.create(user_args = user_params)
        rsp = Response(json.dumps(res), status=status, content_type="application/json")
        return rsp

    if request.method == 'GET':
        res, status = user_resource.find(user_args = user_params, address_args = address_params)
        rsp = Response(json.dumps(res), status=status, content_type="application/json")
        return rsp

@app.route('/users/<string:_id>', methods=['GET', 'PUT', 'DELETE'])
def user_by_id_route(_id: str):
    """
    GET := returns user for the given id
    PUT := updates the user
    DELETE := removes the user
    """
    user_params = user_args_from_route()

    if request.method == 'GET':
        res, status = user_resource.find_by_id(_id)
        rsp = Response(json.dumps(res), status=status, content_type="application/json")
        return rsp
    if request.method == 'PUT':
        res, status = user_resource.update(_id, user_params)
        rsp = Response(json.dumps(res), status=status, content_type="application/json")
        return rsp 
    if request.method == 'DELETE':
        res, status = user_resource.delete(_id, user_params["password"])
        rsp = Response(json.dumps(res), status=status, content_type="application/json")
        return rsp 

@app.route('/users/<string:_id>/addresses', methods=['GET', 'PUT', 'DELETE'])
def user_address_route(_id):
    if request.method == 'GET':
        res, status = user_resource.find_address(_id)
        rsp = Response(json.dumps(res), status=status, content_type="application/json")
        return rsp

    if request.method == 'PUT':
        address_params = address_args_from_route()
        res, status = user_resource.update_address(_id, address_params)
        rsp = Response(json.dumps(res), status=status, content_type="application/json")
        return rsp 

    if request.method == 'DELETE':
        user_params = user_args_from_route()
        res, status = user_resource.delete_address(_id, user_params["password"])
        rsp = Response(json.dumps(res), status=status, content_type="application/json")
        return rsp 


@app.route('/addresses', methods=['GET', 'PUT', 'DELETE'])
def addresses_route():
    # TO DO
    pass


@app.route('/addresses/<string:_id>', methods=['GET', 'PUT', 'DELETE'])
def address_by_id_route(_id):
    # TO DO
    pass

@app.route('/addresses/<string:_id>/users', methods=['GET'])
def users_in_address_route(_id):
    # TO DO
    pass

# Routes for log-in procedure

# log in
@app.route('/users/auth')
def generate_auth_token():
    user_params = user_args_from_route()
    res, status = authenticator.create_token(user_params, user_resource)
    rsp = Response(json.dumps(res), status=status, content_type="application/json")
    return rsp

# verify session
@app.route('/users/auth/<string:token>', methods = ['GET', 'DELETE'])
def modify_token(token):
    if request.method == 'GET':
        return verify_auth_token(token)
    if request.method == 'DELETE':
        return clear_auth_token(token)

def verify_auth_token(token):
    user_params = user_args_from_route()
    res, status = authenticator.validate_token(token, user_params, user_resource)
    rsp = Response(json.dumps(res), status=status, content_type="application/json")
    return rsp

# log out
def clear_auth_token(token):
    user_params = user_args_from_route()
    res, status = authenticator.delete_token(token, user_params, user_resource)
    rsp = Response(json.dumps(res), status=status, content_type="application/json")
    return rsp

if __name__ == '__main__':
    app.run(debug=True)
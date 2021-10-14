from flask import Flask, Response, request

from application_services.UserResource.user_service import UserResource
from application_services.AddressResource.address_service import AddressResource
from application_services.Authentication.authentication_service import Authenticator

import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)

from application_services.UserResource.Model.RDSUserModel import RDSUserModel
from application_services.tests.TestAddressModel import TestAddressModel
from application_services.Authentication.Model.RDSTokenModel import RDSTokenModel

user_resource = UserResource(RDSUserModel, TestAddressModel)
address_resource = AddressResource(TestAddressModel)
authenticator = Authenticator(RDSTokenModel, user_resource)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

def args_from_route(field_to_query):
    return {field: value \
        for field, query_names in field_to_query.items() \
        for value in (request.args.get(q_name) for q_name in query_names)\
        if value is not None
    }

def user_args():
    return args_from_route({
        "nameFirst": ("nameFirst", "firstName", "first_name", "name_first"),
        "nameLast": ("nameLast", "lastName", "last_name", "name_last"),
        "email": ("email", "Email", "e-mail"),
        "password": ("password",)
    })

def address_args():
    return args_from_route({
        "address_first_line": ("address_first_line", "first_line", "addressFirstLine", "firstLine"),
        "address_second_line": ("address_second_line", "second_line", "addressSecondLine", "secondLine"),
        "address_city": ("address_city", "city", "addressCity"),
        "address_state": ("address_state", "state", "addressState"),
        "address_zip_code": ("address_zip_code", "zip_code", "addressZipCode", "zipCode"),
        "address_country_code": ("address_country_code", "country_code", "addressCountryCode", "countryCode")
    })

def token_args():
    return args_from_route({
        "token": ("token", "auth_token", "authToken")
    })

def create_json_response(res, status):
    return Response(json.dumps(res), status=status, content_type="application/json")

def returns_json_response(func):
    def wrapper(*args, **kwargs):
        return create_json_response(*func(*args, **kwargs))
    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/users', methods=['POST', 'GET'])
@returns_json_response
def users_route():
    """
    GET := Returns all users that satisfy params
    POST := Creates a user with name, email and password

    Currently also handles signup through POST
    """
    user_params = user_args()
    if request.method == 'POST':
        return user_resource.create(user_args = user_params)
    if request.method == 'GET':
        return user_resource.find(user_args = user_params)

@app.route('/users/<string:_id>', methods=['GET', 'PUT', 'DELETE'])
@returns_json_response
def user_by_id_route(_id: str):
    """
    GET := returns user for the given id
    PUT := updates the user
    DELETE := removes the user
    """
    user_params = user_args()
    if request.method == 'GET':
        return user_resource.find_by_id(_id)
    if request.method == 'PUT':
        return authenticator.verify_before_execute(
            _id, token_args(), 
            lambda : user_resource.update(_id, user_params)
        )
    if request.method == 'DELETE':
        return authenticator.verify_before_execute(
            _id, token_args(), 
            lambda : user_resource.delete(_id)
        )

@app.route('/users/<string:_id>/addresses', methods=['GET', 'PUT', 'DELETE'])
@returns_json_response
def user_address_route(_id):
    if request.method == 'GET':
        return user_resource.find_address(_id)
    if request.method == 'PUT':
        address_params = address_args()
        return user_resource.update_address(_id, address_params)
    if request.method == 'DELETE':
        user_params = user_args()
        return user_resource.delete_address(_id, user_params["password"])

@app.route('/addresses', methods=['GET', 'PUT', 'DELETE'])
@returns_json_response
def addresses_route():
    if request.method == 'POST':
        return address_resource.create(address_args = address_args())
    if request.method == 'GET':
        return address_resource.find(address_args = address_args())

@app.route('/addresses/<string:_id>', methods=['GET', 'PUT', 'DELETE'])
@returns_json_response
def address_by_id_route(_id):
    if request.method == 'GET':
        return address_resource.find_address(_id)
    if request.method == 'PUT':
        return address_resource.update_address(_id, address_args())
    if request.method == 'DELETE':
        user_params = user_args()
        return address_resource.delete_address(_id, user_params["password"])

@app.route('/addresses/<string:_id>/users', methods=['GET'])
def users_in_address_route(_id):
    # TO DO
    pass

# Routes for log-in procedure

# sign-in and sign out
@app.route('/users/auth', methods = ['GET', 'DELETE'])
@returns_json_response
def auth_token_from_user_args():
    if request.method == 'GET':
        return authenticator.create_token(user_args = user_args())
    if request.method == 'DELETE':
        return authenticator.delete_token(user_args = user_args())

# sign-in and sign out
@app.route('/users/<string:_id>/auth', methods = ['GET', 'DELETE'])
@returns_json_response
def auth_token_from_user_id(_id):
    if request.method == 'GET':
        return authenticator.create_token(_id, token_args = token_args())
    if request.method == 'DELETE':
        return authenticator.delete_token(_id, token_args = token_args())

@app.route('/users/<string:_id>/auth/verify', methods = ['GET'])
@returns_json_response
def verify_auth_token_from_id(_id):
    return authenticator.validate_token(_id, token_args = token_args())

@app.errorhandler(404)
@returns_json_response
def page_not_found(e):
    return {'message': "Page not found", 'description': str(e)}, 404

# subscribtion to changes
# send on creation/delete
# user_id_list

if __name__ == '__main__':
    app.run(debug=True)
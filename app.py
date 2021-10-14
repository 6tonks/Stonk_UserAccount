from os import stat
from re import S
from flask import Flask, Response, request

from application_services.UserResource.user_service import USER_ARGS, UserResource
from application_services.AddressResource.address_service import AddressResource
from application_services.Authentication.authentication_service import Authenticator

import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)

from application_services.UserResource.Model.RDSUserModel import RDSUserModel
from application_services.AddressResource.Model.RDSAddressModel import RDSAddressModel
from application_services.Authentication.Model.RDSTokenModel import RDSTokenModel

user_resource = UserResource(RDSUserModel, RDSAddressModel)
address_resource = AddressResource(RDSAddressModel)
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

from application_services.AddressResource.address_service import ADDRESS_ARGS
def address_args(_id = None):
    args = args_from_route({
        ADDRESS_ARGS.FIRST_LINE.str: ("address_first_line", "first_line", "addressFirstLine", "firstLine"),
        ADDRESS_ARGS.SECOND_LINE.str: ("address_second_line", "second_line", "addressSecondLine", "secondLine"),
        ADDRESS_ARGS.CITY.str: ("address_city", "city", "addressCity"),
        ADDRESS_ARGS.STATE.str: ("address_state", "state", "addressState"),
        ADDRESS_ARGS.ZIP_CODE.str: ("address_zip_code", "zip_code", "addressZipCode", "zipCode"),
        ADDRESS_ARGS.COUNTRY_CODE.str: ("address_country_code", "country_code", "addressCountryCode", "countryCode")
    })
    if _id is not None:
        args['addressId'] = _id
    return

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


@app.route('/')
@returns_json_response
def index():
    return {
        'message': "Wellcome to the Stonks! user service",
        'links': [
            {
                'rel': 'self',
                'href': '/'
            },
            {
                'rel': 'users',
                'href': '/users'
            },
            {
                'rel': 'addresses',
                'href': '/addresses'
            }
        ]
    
    }, 200

@app.route('/users', methods=['POST', 'GET'])
@returns_json_response
def users_route():
    """
    GET := Returns all users that satisfy params
    POST := Creates a user with name, email and password

    Currently also handles signup through POST
    """
    user_params = user_args()
    if request.method == 'GET':
        resp, status = user_resource.find(user_args = user_params)
        if status == 200:
            resp['links'] = [
                {
                    'rel': 'self',
                    'href': f'/users'
                }               
            ]
        return resp, status
    if request.method == 'POST':
        return user_resource.create(user_args = user_params)

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
        resp, status = user_resource.find_by_id(_id)
        if status == 200:
            resp['links'] = [
                {
                    'rel': 'self',
                    'href': f'/users/{_id}'
                },
                {
                    "rel": "address",
                    'href': f'/address/{resp[USER_ARGS.ADDRESS_ID.str]}'
                }                
            ]
        return resp, status
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
        resp, status = user_resource.find_address(_id)
        if status == 200:
            resp['links'] = [
                {
                    'rel': 'self',
                    'href': f'/users/{_id}/addresses'
                },
                {
                    'rel': 'address',
                    'href': f'addresses/{resp[USER_ARGS.ADDRESS_ID.str]}'
                }
            ]
        return resp, status
    if request.method == 'PUT':
        address_params = address_args()
        return user_resource.update_address(_id, address_params)
    if request.method == 'DELETE':
        user_params = user_args()
        return user_resource.delete_address(_id, user_params["password"])

@app.route('/addresses', methods=['GET', 'PUT', 'DELETE'])
@returns_json_response
def addresses_route():
    if request.method == 'GET':
        resp, status = address_resource.find(address_args = address_args())
        if status == 200:
            resp['links'] = [
                {
                    'rel': 'self',
                    'href': f'/addresses'
                }
            ]
        return resp, status
    if request.method == 'POST':
        return address_resource.create(address_args = address_args())

@app.route('/addresses/<string:_id>', methods=['GET', 'PUT', 'DELETE'])
@returns_json_response
def address_by_id_route(_id):
    if request.method == 'GET':
        resp, status = address_resource.find_address(_id)
        if status == 200:
            resp['links'] = [
                {
                    'rel': 'self',
                    'href': f'/addresses/{_id}'
                }
            ]
        return resp, status
    if request.method == 'PUT':
        return address_resource.update_address(_id, address_args())
    if request.method == 'DELETE':
        user_params = user_args()
        return address_resource.delete_address(_id, user_params["password"])

@app.route('/addresses/<string:_id>/users', methods=['GET', 'POST'])
def users_in_address_route(_id):
    if request.method == 'GET':
        resp, status = user_resource.find(user_args = user_args(), address_args = address_args(_id = _id))
        if status == 200:
            resp['links'] = [
                {
                    'rel': 'self',
                    'href': f'/addresses/{_id}/users'
                }
            ]
        return resp, status
    
    if request.method == 'POST':
        return user_resource.get_id_before_execute(
            user_args = user_args(),
            func = lambda user_id: authenticator.verify_before_execute(
                user_id = user_id, token_args=token_args(),
                func = lambda : user_resource.update_address(user_id, address_args(_id = _id))
            )
        )

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
from flask import Flask, Response, request, url_for

from application_services.UserResource.user_service import UserResource

import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)

from application_services.unit_tests.TestUserModel import TestUserModel
from application_services.unit_tests.TestAddressModel import TestAddressModel
user_resource = UserResource(TestUserModel(), TestAddressModel())

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

# Routes for sign_in and sign_out
@app.route('/users/<string:_id>/session', methods=['GET', 'POST', 'DELETE'])
def sign_in(_id):
    # TO DO
    pass

if __name__ == '__main__':
    app.run(debug=True)

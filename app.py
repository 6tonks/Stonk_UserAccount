from flask import Flask, Response, request, url_for

from application_services.UserResource.user_service import UserResource

import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

def user_args_from_route():
    return {field: request.args.get(field) for field in (
        "name",
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
    """
    user_params = user_args_from_route()
    address_params = address_args_from_route()

    if request.method == 'POST':
        res, status = UserResource.create(user_args = user_params, address_args = address_params)
        rsp = Response(json.dumps(res), status=status, content_type="application/json")
        return rsp

    if request.method == 'GET':
        res, status = UserResource.find(user_args = user_params, address_args = address_params)
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
        res, status = UserResource.find_by_id(_id)
        rsp = Response(json.dumps(res), status=status, content_type="application/json")
        return rsp
    if request.method == 'PUT':
        res, status = UserResource.update(_id, user_params)
        rsp = Response(json.dumps(res), status=status, content_type="application/json")
        return rsp 
    if request.method == 'DELETE':
        res, status = UserResource.delete(_id, user_params["password"])
        rsp = Response(json.dumps(res), status=status, content_type="application/json")
        return rsp 

@app.route('/users/<string:_id>/addresses', methods=['GET', 'PUT', 'DELETE'])
def user_address_route(_id):
    # TO DO
    pass

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

if __name__ == '__main__':
    app.run(debug=True)

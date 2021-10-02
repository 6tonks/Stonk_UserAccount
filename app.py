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
    name = request.args.get("name")
    email = request.args.get("email")
    password = request.args.get("password")

    return name, email, password

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
    name, email, password = user_args_from_route()
    address_params = address_args_from_route()

    if request.method == 'POST':
        res = UserResource.create(name = name, email = email, password = password)
        rsp = Response(json.dump(res), status=res['status'], content_type="application/json")
        return rsp

    if request.method == 'GET':
        res = UserResource.find(name, email, password, **address_params)
        rsp = Response(json.dumps(res), status=res['status'], content_type="application/json")
        return rsp

@app.route('/users/<string:_id>', methods=['GET', 'PUT', 'DELETE'])
def user_by_id_route(_id: str):
    """
    GET := returns user for the given id
    PUT := updates the user
    DELETE := removes the user
    """
    name, email, password = user_args_from_route()

    if request.method == 'GET':
        res = UserResource.find_by_id(_id)
        rsp = Response(json.dumps(res), status=res['status'], content_type="application/json")
        return rsp
    if request.method == 'PUT':
        res = UserResource.update(_id, name, email, password)
        rsp = Response(json.dumps(res), status=res['status'], content_type="application/json")
        return rsp 
    if request.method == 'DELETE':
        res = UserResource.delete(_id, password)
        rsp = Response(json.dumps(res), status=res['status'], content_type="application/json")
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

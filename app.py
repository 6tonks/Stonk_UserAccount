from flask import Flask, request
from flask_cors import CORS

from config.response_args import RESPONSE_ARGS
import config.aws_config as aws_config
from config.aws_config import SNS_ARNS, SNS_TOPICS

from middleware.simple_notification_service import send_sns_message

from utils import (
    user_resource,
    address_resource,
    authenticator,
    user_args,
    address_args,
    token_args,
    returns_json_response,
    USER_ARGS)

import json
import logging
import middleware.simple_security as simple_security

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Flask(__name__)
CORS(app)


@app.before_request
def before_request_func():
    result_ok = simple_security.check_security(request)

    if not result_ok:
        return {"Error": "Invalid authentication token"}, 401


@app.after_request
def post_request(response):
    # Check URL to see if it matchs SNS config
    if aws_config.ENABLE_USER_ACTIVITY:
        body = json.loads(response.get_data())
        if RESPONSE_ARGS.CREATED.str in body and \
                body[RESPONSE_ARGS.CREATED.str] == RESPONSE_ARGS.USER.str:
            id = send_sns_message(SNS_ARNS[SNS_TOPICS.USER_ACTIVITY], json.dumps(body), {})
            logger.info(f"Created user message with id {id} sent")
        if RESPONSE_ARGS.DELETED.str in body and \
                body[RESPONSE_ARGS.DELETED.str] == RESPONSE_ARGS.USER.str:
            id = send_sns_message(SNS_ARNS[SNS_TOPICS.USER_ACTIVITY], json.dumps(body), {})
            logger.info(f"Deleted user message with id {id} sent")

    return response

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

@app.route('/users', methods=['GET', 'POST'])
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

@app.route('/addresses', methods=['GET', 'PUT'])
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
        resp, status = address_resource.find_by_id(_id)
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

#region Routes for sign-in procedure
@app.route('/users/auth', methods = ['GET', 'DELETE'])
@returns_json_response
def auth_token_from_user_args():
    if request.method == 'GET':
        return authenticator.create_token(user_args = user_args())
    if request.method == 'DELETE':
        return authenticator.delete_token(user_args = user_args())

@app.route('/users/<string:_id>/auth', methods = ['GET', 'DELETE'])
@returns_json_response
def auth_token_from_user_id(_id):
    if request.method == 'GET':
        return authenticator.create_token(_id, token_args = token_args())
    if request.method == 'DELETE':
        return authenticator.delete_token(_id, token_args = token_args())
#endregion

@app.route('/users/<string:_id>/auth/verify', methods = ['GET'])
@returns_json_response
def verify_auth_token_from_id(_id):
    return authenticator.validate_token(_id, token_args = token_args())

@app.errorhandler(404)
@returns_json_response
def page_not_found(e):
    return {'message': "Page not found", 'description': str(e)}, 404


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
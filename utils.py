from flask import Response, request

from application_services.UserResource.user_service import USER_ARGS, UserResource
from application_services.AddressResource.address_service import ADDRESS_ARGS, AddressResource
from application_services.Authentication.authentication_service import Authenticator

from application_services.UserResource.Model.RDSUserModel import RDSUserModel
from application_services.AddressResource.Model.RDSAddressModel import RDSAddressModel
from application_services.Authentication.Model.RDSTokenModel import RDSTokenModel

import json

user_resource = UserResource(RDSUserModel, RDSAddressModel)
address_resource = AddressResource(RDSAddressModel)
authenticator = Authenticator(RDSTokenModel, user_resource)

def args_from_route(field_to_query):
    return {field: value \
        for field, query_names in field_to_query.items() \
        for value in (request.args.get(q_name) for q_name in query_names)\
        if value is not None
    }

def user_args(_id = None):
    args = args_from_route({
        USER_ARGS.FIRST_NAME.str: ("nameFirst", "firstName", "first_name", "name_first"),
        USER_ARGS.LAST_NAME.str: ("nameLast", "lastName", "last_name", "name_last"),
        USER_ARGS.EMAIL.str: ("email", "Email", "e-mail"),
        USER_ARGS.PASSWORD.str: ("password",)
    })
    if _id is not None:
        args[USER_ARGS.ID.str] = _id
    return args

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
        args[ADDRESS_ARGS.ID.str] = _id
    return args

def token_args():
    return args_from_route({
        "token": ("token", "auth_token", "authToken")
    })

def returns_json_response(func):
    def wrapper(*args, **kwargs):
        res, status = func(*args, **kwargs)
        return Response(json.dumps(res), status=status, content_type="application/json")
    wrapper.__name__ = func.__name__
    return wrapper
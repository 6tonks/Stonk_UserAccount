# Test for CREATE, READ, UPDATE, DESTROY user for user service
from application_services.UserResource.user_service import UserResource
from application_services.AddressResource.Model import TestAddressModel
from application_services.UserResource.Model import TestUserModel

user_resource = UserResource(TestUserModel, TestAddressModel)

def create_user(email, firstName, lastName, password):
    return user_resource.create({
        "lastName": lastName, 
        "firstName": firstName, 
        "email": email,
        "password": password
    })


def test1():
    print( create_user(**{
        "lastName": "Bar", 
        "firstName": "Foo", 
        "email": "FooBar@gmail.com",
        "password": "FooBar"
    }))
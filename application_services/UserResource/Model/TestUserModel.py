from typing import Dict, List
from application_services.UserResource.Model.BaseUserModel import BaseUserModel, UserEmailExistsException

USERS = {}

def clear_users():
    for k in USERS.keys():
        del USERS[k]

def populate_db_scenario1():
    clear_users()
    USERS['1'] = {
        "lastName": "Bar", 
        "firstName": "Foo", 
        "email": "foobar@gmail.com", 
        "pwHash": ''
    }
    USERS['2'] = {
        "lastName": "Car", 
        "firstName": "Foo", 
        "email": "foocar@gmail.com", 
        "pwHash": ''
    }

class TestUserModel(BaseUserModel):

    @classmethod
    def create(cls, create_args):
        if any(user['email'] == create_args['email'] for user in USERS.values()):
            raise UserEmailExistsException()

        new_user = create_args.copy()
        new_user["id"] = str(len(USERS))
        USERS[new_user['id']] = new_user
        if "pwHash" not in new_user:
            raise Exception(f"Hash not in {new_user}")
        return new_user.copy()

    @classmethod
    def find_by_template(cls, template):
        return [user.copy() for user in USERS.values() if all(user[key] == value\
             for key, value in template.items() if value is not None)]

    @classmethod
    def update(cls, _id: str, user_args: Dict[str, str]) -> Dict[str, str]:
        if int(_id) not in USERS:
            return

        user = USERS[_id]
        user.update(user_args)
        return user.copy()

    @classmethod
    def delete(cls, _id: str) -> None:
        if int(_id) not in USERS:
            return

        del USERS[_id]
        return

    @classmethod
    def find_by_address(cls, user_args: Dict[str, str], address_args: Dict[str, str]) \
            -> List[Dict[str, str]]:
        raise NotImplementedError()
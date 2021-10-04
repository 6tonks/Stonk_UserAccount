from typing import Dict, List
from database_services.BaseUserModel import BaseUserModel, UserEmailExistsException

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
    def create(cls, name, email, password_hash):
        if any(user['email'] == email for user in USERS.values()):
            raise UserEmailExistsException()

        new_user = {"id": len(USERS), "name": name, "email": email, "pwHash": password_hash}
        USERS[new_user['id']] = new_user
        return new_user

    @classmethod
    def find_by_template(cls, template):
        return [user for user in USERS.values() if all(user[key] == value\
             for key, value in template.items() if value is not None)]

    @classmethod
    def update(cls, _id: str, user_args: Dict[str, str]) -> Dict[str, str]:
        if int(_id) not in USERS:
            return

        user = USERS[int(_id)]
        user.update(user_args)
        return user

    @classmethod
    def delete(cls, _id: str) -> None:
        if int(_id) not in USERS:
            return

        del USERS[int(_id)]
        return

    @classmethod
    def find_by_address(cls, user_args: Dict[str, str], address_args: Dict[str, str]) \
            -> List[Dict[str, str]]:
        raise NotImplementedError()
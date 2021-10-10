from typing import Dict, List

import pymysql

from application_services.UserResource.Model.BaseUserModel import BaseUserModel, UserEmailExistsException
import database_services.RDBService as d_service


# or maybe should just name it UserModel?
class RDSUserModel(BaseUserModel):
    Duplicate_Entry_ErrorCode = 1062

    @classmethod
    def create(cls, user_args: Dict[str, str]) -> Dict[str, str]:
        """Add the user to the DB
                  :param dict reg_info: dictionary contained all info need to reg, which are:
                   email
                   pwHash
                   lastName
                   firstName
          """

        user_PK = None  # may use it later
        # Try to add user to DB
        try:
            user_PK = d_service.insert_new_record("Stonk", "User",
                                                  {
                                                      "userID": 'DEFAULT',
                                                      "email": user_args['email'],
                                                      "pwHash": user_args['pwHash'],
                                                      "nameLast": user_args['lastName'],
                                                      "nameFirst": user_args['firstName'],
                                                      "addressID": "NULL"
                                                  },
                                                  True
                                                  )
        except pymysql.Error as e:
            print("RDSUserModel: ", "SQL exception: ", e)
            if e.args[0] == cls.Duplicate_Entry_ErrorCode:
                print(RDSUserModel, "Duplicate entry (probably email)")
                raise UserEmailExistsException("email_already_exist")
                return None

        print("RDSUserModel", "New User Added Success, UserPK: ", user_PK)
        return user_args

    @classmethod
    def find_by_template(cls, user_args: Dict[str, str]) -> List[Dict[str, str]]:
        return d_service.get_by_template("Stonk", "User", user_args)

    @classmethod
    def update(cls, _id: str, user_args: Dict[str, str]) -> Dict[str, str]:
        d_service.update_record_with_keys("Stonk", "User", {"userID": _id}, user_args)
        return d_service.get_by_template("Stonk", "User", {"userID": _id})

    @classmethod
    def delete(cls, _id: str) -> None:
        d_service.remove_old_record("Stonk", "User", "userID", _id)
        return d_service.get_by_template("Stonk", "User", {"userID": _id})

    @classmethod
    def find_by_address(cls, user_args: Dict[str, str], address_args: Dict[str, str]) -> List[Dict[str, str]]:
        pass

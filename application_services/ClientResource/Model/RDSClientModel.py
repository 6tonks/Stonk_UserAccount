from typing import Dict, List
import database_services.RDBService as d_service

import pymysql

class ClientCreationFailed(Exception):
    pass

# or just name it TokenModel?
class RDSClientModel:
    @classmethod
    def create(cls, client_args):
        try:
            client_PK = d_service.insert_new_record(
                "Stonk", "appClient",
                {
                    "clientID": 'DEFAULT',
                    "listenURL": client_args['listenURL'],
                }, True
            )
        except pymysql.Error as e:
            print("RDSUserModel: ", "SQL exception: ", e)
            raise ClientCreationFailed()
        return client_args

    @classmethod
    def find_by_template(cls, client_args: Dict[str, str]) -> List[Dict[str, str]]:
        return d_service.get_by_template("Stonk", "appClient", client_args)

    @classmethod
    def delete(cls, _id):
        d_service.remove_old_record("Stonk", "appClient", "clientID", _id)
        return d_service.get_by_template("Stonk", "appClient", {"clientID": _id})
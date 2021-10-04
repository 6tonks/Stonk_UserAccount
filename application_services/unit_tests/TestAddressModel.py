from typing import Dict, List
from database_services.BaseAddressModel import BaseAddressModel

ADDRESSES = {}

class TestAddressModel(BaseAddressModel):    
    @classmethod
    def create(cls, address_args: Dict[str, str]) -> Dict[str, str]:
        """
            Creates a user
            @param address_args 
            @return created object
        """
        address_args['id'] = ADDRESSES.append(address_args)
        return address_args

    @classmethod
    def find_by_template(cls, address_args: Dict[str, str]) -> List[Dict[str, str]]:
        return [user for user in ADDRESSES.values() if all(user[key] == value\
             for key, value in address_args.items() if value is not None)]

    @classmethod
    def update(cls, _id: str, address_args: Dict[str, str]) -> Dict[str, str]:
        raise NotImplementedError()

    @classmethod
    def delete(cls, _id: str) -> None:
        raise NotImplementedError()
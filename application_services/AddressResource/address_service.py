from os import error
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from application_services.BaseResource import BaseResource, InvalidArguement, ResourceError, ResourceErrorCollection
from database_services.BaseAddressModel import BaseAddressModel

import re

class AddressResourceError(ResourceError):
    code = 4000
    
    def __init__(self):
        super().__init__()

class AddressNotFound(AddressResourceError):
    code = 4001
    message = "Address not found"
    description = ""

@dataclass
class AddressResource(BaseResource):
    address_model: BaseAddressModel
    required_address_fields: Tuple[str] = (
        'address_first_line', 
        'address_second_line', 
        'address_city', 
        'address_state',
        'address_zip_code',
        'address_country_code'
    )

    def create(self, address_args):
        suc, errors = self.ensure_fields_in_args(address_args, self.required_address_fields)
        if not suc:
            return errors.response(), 400
        
        address = self.address_model.create(address_args)
        return address, 201

    def _find(self, address_args):
        address_args = {f:v for f, v in address_args.items() if v is not None}
        addresses = self.address_model.find_by_template(address_args)
        return True, addresses, None

    def find(self, address_args = {}):
        suc, addresses, errors = self._find(address_args)
        if not suc:
            return errors.response(), 404
        return {"Addresses": addresses}, 200

    def find_by_id(self, _id):
        suc, addresses, errors = self._find({'id': _id})
        if not suc:
            return errors.response(), 404

        if len(addresses) == 0:
            return ResourceErrorCollection(AddressNotFound()), 404

        return addresses[0], 200

    def update(self, _id, user_args):
        suc, addresses, errors = self._find({'id': _id})
        if not suc:
            return errors.response(), 404

        if len(addresses) == 0:
            return ResourceErrorCollection(AddressNotFound()), 404
        
        address = self.address_model.update(_id, user_args)
        return address, 200
    
    def delete(self, _id, user_args):
        suc, addresses, errors = self._find({'id': _id})
        if not suc:
            return errors.response(), 404

        if len(addresses) == 0:
            return ResourceErrorCollection(AddressNotFound()), 404

        user = self.address_model.delete(_id)
        return user, 200
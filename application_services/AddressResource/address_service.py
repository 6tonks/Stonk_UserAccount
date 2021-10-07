from os import error
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from application_services.BaseResource import BaseResource, ResourceError, sends_response, throws_resource_errors
from database_services.BaseAddressModel import BaseAddressModel


class AddressResourceError(ResourceError):
    code = 4000
    
    def __init__(self):
        super().__init__()

class AddressNotFound(AddressResourceError):
    code = 4001
    message = "Address not found"
    description = ""
    status = 404

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

    @sends_response
    def create(self, address_args):
        yield self.ensure_fields_in_args(address_args, self.required_address_fields)
        address = self.address_model.create(address_args)
        return address, 201

    @throws_resource_errors
    def _find(self, address_args):
        address_args = {f:v for f, v in address_args.items() if v is not None}
        yield self.address_model.find_by_template(address_args)

    @sends_response
    def find(self, address_args = {}):
        addresses = self._find(address_args)
        yield addresses
        yield {"Addresses": addresses}, 200

    @sends_response
    def find_by_id(self, _id):
        addresses = self._find({'id': _id})
        yield addresses
        if len(addresses) == 0:
            yield AddressNotFound()
        yield addresses[0], 200

    @sends_response
    def update(self, _id, user_args):
        addresses = self._find({'id': _id})
        yield addresses
        if len(addresses) == 0:
            yield AddressNotFound()
        
        address = self.address_model.update(_id, user_args)
        yield address, 200
    
    @sends_response
    def delete(self, _id, user_args):
        addresses = self._find({'id': _id})
        yield addresses

        if len(addresses) == 0:
            return AddressNotFound()

        user = self.address_model.delete(_id)
        yield user, 200
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from application_services.BaseResource import BaseResource, sends_response, sends_app_service_reponse
from application_services.AddressResource.Model.BaseAddressModel import BaseAddressModel

from application_services.AddressResource.AddressError import *

class ADDRESS_ARGS(Enum):
    ID = 'addressID'
    FIRST_LINE = 'firstLine'
    SECOND_LINE = 'secondLine'
    CITY = 'city'
    STATE = 'state'
    ZIP_CODE = 'zipCode'
    COUNTRY_CODE = 'countryCode'

    @property
    def str(self):
        return self.value

@dataclass
class AddressResource(BaseResource):
    address_model: BaseAddressModel
    required_address_fields: Tuple[str] = (
        ADDRESS_ARGS.FIRST_LINE.str,
        ADDRESS_ARGS.SECOND_LINE.str, 
        ADDRESS_ARGS.CITY.str,
        ADDRESS_ARGS.ZIP_CODE.str,
        ADDRESS_ARGS.COUNTRY_CODE.str
    )

    @sends_response
    def create(self, address_args):
        yield self.ensure_fields_in_args(address_args, self.required_address_fields)
        address = self.address_model.create(address_args)
        return address, 201

    @sends_app_service_reponse
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
        addresses = self._find({ADDRESS_ARGS.ID.str: _id})
        yield addresses
        if len(addresses) == 0:
            yield AddressNotFound()
        yield addresses[0], 200

    @sends_response
    def update(self, _id, address_args):
        addresses = self._find({ADDRESS_ARGS.ID.str: _id})
        yield addresses
        if len(addresses) == 0:
            yield AddressNotFound()
        
        address = self.address_model.update(_id, address_args)
        yield address, 200
    
    @sends_response
    def delete(self, _id):
        addresses = self._find({ADDRESS_ARGS.ID.str: _id})
        yield addresses

        if len(addresses) == 0:
            return AddressNotFound()

        user = self.address_model.delete(_id)
        yield user, 200
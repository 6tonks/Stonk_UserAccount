from application_services.AddressResource.Model.BaseAddressModel import BaseAddressModel
from typing import Dict, List
import database_services.RDBService as d_service
from application_services.AddressResource.address_service import ADDRESS_ARGS

class RDSAddressModel(BaseAddressModel):
    @classmethod
    def create(cls, address_args: Dict[str, str]) -> int:

        address_ID = d_service.insert_new_record("Stonk", "Address",
                                              {
                                                  "addressID": 'DEFAULT',
                                                  "countryCode": address_args[ADDRESS_ARGS.COUNTRY_CODE.str],
                                                  "zipCode": address_args[ADDRESS_ARGS.ZIP_CODE.str],
                                                  "state": address_args[ADDRESS_ARGS.STATE.str],
                                                  "city": address_args[ADDRESS_ARGS.CITY.str],
                                                  "firstLine": address_args[ADDRESS_ARGS.FIRST_LINE.str],
                                                  "secondLine": address_args[ADDRESS_ARGS.SECOND_LINE.str]
                                              },
                                              True
                                              )


        print("RDSUserModel", "New Address Added Success, UserPK: ", address_ID)
        return address_ID
        #raise NotImplementedError()

    @classmethod
    def find_by_template(cls, address_args: Dict[str, str]) -> List[Dict[str, str]]:
        print("RDSAddressModel.find_by_template()", address_args)
        return d_service.get_by_template("Stonk", "Address", address_args)

        #raise NotImplementedError()

    @classmethod
    def update(cls, _id: str, address_args: Dict[str, str]) -> Dict[str, str]:
        d_service.update_record_with_keys("Stonk", "Address", {"addressID":_id}, address_args)

    @classmethod
    def delete(cls, _id: str) -> None:
        raise NotImplementedError()
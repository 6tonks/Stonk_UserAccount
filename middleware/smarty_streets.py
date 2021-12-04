from typing import Dict
import requests

import local
import json

"""https://us-street.api.smartystreets.com/street-address?
	auth-id=YOUR+AUTH-ID+HERE&
	auth-token=YOUR+AUTH-TOKEN+HERE&
	license=us-rooftop-geocoding-cloud&
	street=1600+amphitheatre+pkwy&
	city=mountain+view&
	state=CA&
	candidates=10"""

base_url = 'https://us-street.api.smartystreets.com/street-address'
auth_id = getattr(local, "smarty_streets_auth_id")
auth_token = getattr(local, "smarty_streets_auth_token")
license = getattr(local, "smarty_streets_license")

FIRST_LINE = 'firstLine'
SECOND_LINE = 'secondLine'
CITY = 'city'
STATE = 'state'
ZIP_CODE = 'zipCode'
COUNTRY_CODE = 'countryCode'

def get_valid_address(address_args: Dict[str, str]) -> Dict[str, str]:
    params = {
        'auth-id': auth_id,
        'auth-token': auth_token,
        'license': license,
        'street': address_args.get('firstLine'),
        'street2': address_args.get('secondLine'),
        'city': address_args.get('city'),
        'state': address_args.get('state'),
        'zipcode': address_args.get('zipCode'),
    }

    resp = requests.get(base_url, params=params)
    results = json.loads(resp.content)
    if not results:
        return {}
    result = results.pop()
    if not result:
        return {}

    return_args = {
        'firstLine': result.get('delivery_line_1', ''), 
        'secondLine': result.get('delivery_line_2', ''),
        'city': result.get('components', {}).get('city_name', ''),
        'state': result.get('components', {}).get('state_abbreviation', ''),
        'zipCode': result.get('components', {}).get('zipcode', ''),
        'countryCode': result.get('metadata', {}).get('county_name', 'USA')
    }
    return return_args	
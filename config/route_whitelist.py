from enum import Enum, auto

class PermisionSettings(Enum):
    ALL = auto()
    AUTH = auto()

ALL = PermisionSettings.ALL
AUTH = PermisionSettings.AUTH

PERMISIONS = {
    "/": {
        "GET": ALL
    },
    "/users": {
        "GET": ALL,
        "POST": ALL
    },
    "/users/<string:id>": {
        "GET": ALL,
        "PUT": AUTH,
        "DELETE": AUTH
    },
    "/users/<string:id>/addresses": {
        "GET": ALL,
        "PUT": AUTH,
        "DELETE": AUTH
    },
    "/addresses": {
        "GET": ALL,
        "POST": ALL
    },
    "/addresses/<string:id>":{
        "GET": ALL,
        "PUT": AUTH,
        "DELETE": AUTH
    }
}
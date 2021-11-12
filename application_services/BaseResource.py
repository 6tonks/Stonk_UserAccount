from abc import ABC
from enum import Enum, auto
from typing import Dict, List, Tuple
from dataclasses import dataclass, field

from config.response_args import RESPONSE_ARGS

def sends_app_service_reponse(func):
    def wraper(*args, **kwargs):
        last_output = None
        for output in func(*args, **kwargs):
            last_output = output
            if isinstance(output, ResourceError):
                if not isinstance(output, ResourceErrorCollection):
                    output = ResourceErrorCollection(output)
                return output
        return last_output

    return wraper

def sends_response(func):
    func = sends_app_service_reponse(func)
    def wraper(*args, **kwargs):
        output = func(*args, **kwargs)
        if isinstance(output, ResourceError):
            return output.response(), output.status
        return output
    return wraper

class ResourceError(ABC):
    code: int
    message: str
    description: str
    suberrors: List
    status: int = 404

    def __init__(self):
        self.suberrors = []

    def response(self, suberrors = None):
        resp = {
            'code': self.code,
            'message': self.message,
            'description': self.description
        }
        suberrors = suberrors if suberrors is not None else self.suberrors
        if suberrors:
            resp['errors'] = [error.response() for error in suberrors]
        return resp
    
    def add(self, error):
        self.suberrors.append(error)
        return self
    
    def remove(self, error):
        self.suberrors.remove(error)
        return self

class ResourceErrorCollection(ResourceError):
    code = 1000
    message = "Collection of errors"
    description = ""

    def __init__(self, *errors):
        self.suberrors = list(errors[:])

    def response(self):
        if len(self) == 0:
            return {}
        self.status = self.suberrors[-1].status
        return {"error": [error.response() for error in self.suberrors]}

    def __len__(self):
        return len(self.suberrors)

    def extend(self, error_collection):
        return self.suberrors.extend(error_collection.suberrors)

class MissingArguementError(ResourceError):
    code = 1001
    message = "Missing value for a required arguement"
    description =  "Value for {arg} is missing"
    status = 400

    def __init__(self, arg):
        super().__init__()
        self.description = self.description.format(arg = arg)

class InvalidArguement(ResourceError):
    code = 1002
    message = "Invalid value for arguement"
    description = "{value} is not an appropriate value for {arg}"
    status = 400

    def __init__(self, value = None, arg = None):
        super().__init__()
        if value is None or arg is None:
            self.description = ""
        else:
            self.description = self.description.format(value = value, arg = arg)

class BaseResource(ABC):

    @classmethod
    def preprocess_args(cls, args: Dict):
        return {k: v for k, v in args.items() if v is not None}

    @classmethod
    @sends_app_service_reponse
    def ensure_fields_in_args(cls, args, required_fields) -> Tuple[bool, ResourceErrorCollection]:
        args = cls.preprocess_args(args)
        errors = ResourceErrorCollection()

        for field in required_fields:
            if field not in args or args[field] is None:
                errors.add( MissingArguementError(field) )
        
        yield errors if len(errors) > 0 else None
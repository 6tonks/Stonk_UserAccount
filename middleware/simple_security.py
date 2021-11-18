from dataclasses import dataclass
import json
from utils import token_args, user_args
from application_services.Authentication.Model.RDSTokenModel import RDSTokenModel
import re

from typing import Tuple
from dataclasses import dataclass, field

from utils import (
    authenticator
)

@dataclass
class Rule:
    path: str
    methods: Tuple[str] = ("GET",)

    def match(self, path: str, method: str) -> bool:
        if method.upper() not in self.methods or "ANY" in self.methods:
            return False

        curr = path.split("/")
        targ = self.path.split("/")
        return len(curr) == len(targ) \
            and all(c==t 
                for c, t in zip(curr, targ) 
                if not (len(t) and t[0] == "{" and t[-1]=="}") and not (t=="*"))

public_paths = [
    Rule("/"),
    Rule("/users", methods=("GET", "POST")),
    Rule("/users/auth"),
    Rule("/users/{user_id}"),
    Rule("/users/{user_id}/auth"),
    Rule("/users/{user_id}/auth/verify"),
    Rule("/users/{user_id}/addresses"),
    Rule("/addresses", methods=("ANY",)),
    Rule("/addresses/{address_id}", methods=("ANY",)),
    Rule("/addresses/{address_id}/users", methods=("ANY",)),
    Rule("/google-auth"),
    Rule("/login/google"),
    Rule("/login/google/authorized"),
]

def check_security(request) -> bool:#, google, blueprint):

    path, method = request.path, request.method
    for rule in public_paths:
        if rule.match(path, method):
            return True
    
    _, status = authenticator.validate_token(token_args= token_args(), user_args = user_args())
    if status >= 200 and status <= 300:
        return True

    return False

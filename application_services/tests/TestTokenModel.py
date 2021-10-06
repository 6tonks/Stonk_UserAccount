from database_services.BaseTokenModel import BaseTokenModel
import random

TOKENS = {}
class TestTokenModel(BaseTokenModel):

    @classmethod
    def create(cls, id):
        for _ in range(20):
            tok = str(random.randint(0, (len(TOKENS)+1) * 10))
            if tok not in TOKENS:
                TOKENS[tok] = id
                return tok
        
        raise Exception("Couldn't generate token. Very rare failure?")

    @classmethod
    def validate(cls, token, id):
        return token in TOKENS and TOKENS[token] == id

    @classmethod
    def delete(cls, token):
        if token in TOKENS:
            del TOKENS[token]
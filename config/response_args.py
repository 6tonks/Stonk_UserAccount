from enum import Enum

class RESPONSE_ARGS(Enum):
    CREATED = "created"
    DELETED = 'deleted'
    
    SUCCESS = "success"
    MESSAGE = "message"
    DESCRIPTION = "description"
    OBJECT_INFO = "info"

    USER = "user"
    ADDRESS = "address"

    @property
    def str(self):
        return self.value
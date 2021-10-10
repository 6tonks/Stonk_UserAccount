from application_services.BaseResource import InvalidArguement, ResourceError

class AddressResourceError(ResourceError):
    code = 4000
    
    def __init__(self):
        super().__init__()

class AddressNotFound(AddressResourceError):
    code = 4001
    message = "Address not found"
    description = ""
    status = 404
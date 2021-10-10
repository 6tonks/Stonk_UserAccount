from application_services.BaseResource import InvalidArguement, ResourceError

class UserResourceError(ResourceError):
    code = 2000
    
    def __init__(self):
        super().__init__()

class InvalidEmail(UserResourceError, InvalidArguement):
    code = 2001
    message = "The given email is invalid"
    description = ""
    status = 400

class InvalidPassword(UserResourceError, InvalidArguement):
    code = 2002
    message = "The given password is invalid"
    description = ""
    status = 400

    def __init__(self):
        super().__init__()

class EmailAlreadyInUse(UserResourceError):
    code = 2003
    message = "The given email is already in use"
    description = ""
    status = 400

    def __init__(self):
        super().__init__()

class UserNotFound(UserResourceError):
    code = 2004
    message = "User not found"
    description = ""
    status = 404

    def __init__(self):
        super().__init__()

class IncorrectPassword(UserResourceError):
    code = 2005
    message = "Password is incorrect"
    description = ""
    status = 400

    def __init__(self):
        super().__init__()

class NoAccountWithEmail(UserResourceError):
    code = 2006
    message = "Could not find account with email"
    description = "Account with email {} is not registered"
    status = 400

    def __init__(self, email = None):
        super().__init__()
        if email is None:
            self.description = ""
        else:
            self.description = self.description.format(email)

class UserCouldNotBeRemoved(UserResourceError):
    code = 2007
    message = "User could not be removed"
    description = ""
    status = 404
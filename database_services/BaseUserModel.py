from abc import ABC, abstractclassmethod, abstractmethod
from typing import Dict, List

class UserException(Exception):
    pass

class UserEmailExistsException(UserException):
    pass

class BaseUserModel(ABC):

    @abstractclassmethod
    def create(cls, user_args: Dict[str, str]) -> Dict[str, str]:
        """
            Creates a user
            @param user_args - includes first name, last name, password and email
            @return values for user object that is created
            @throws UserEmailExistsException if email already exists
        """
        raise NotImplementedError()

    @abstractclassmethod
    def find_by_template(cls, user_args: Dict[str, str]) -> List[Dict[str, str]]:
        raise NotImplementedError

    @abstractclassmethod
    def update(cls, _id: str, user_args: Dict[str, str]) -> Dict[str, str]:
        raise NotImplementedError()

    @abstractclassmethod
    def delete(cls, _id: str) -> None:
        raise NotImplementedError()

    @abstractclassmethod
    def find_by_address(cls, user_args: Dict[str, str], address_args: Dict[str, str]) \
            -> List[Dict[str, str]]:
        raise NotImplementedError()
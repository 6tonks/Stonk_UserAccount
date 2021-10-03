from typing import Dict, List
from abc import ABC, abstractclassmethod

class BaseAddressModel(ABC):

    @abstractclassmethod
    def create(cls, address_args: Dict[str, str]) -> Dict[str, str]:
        """
            Creates a user
            @param address_args 
            @return created object
        """
        raise NotImplementedError()

    @abstractclassmethod
    def find_by_template(cls, address_args: Dict[str, str]) -> List[Dict[str, str]]:
        raise NotImplementedError

    @abstractclassmethod
    def update(cls, _id: str, address_args: Dict[str, str]) -> Dict[str, str]:
        raise NotImplementedError()

    @abstractclassmethod
    def delete(cls, _id: str) -> None:
        raise NotImplementedError()
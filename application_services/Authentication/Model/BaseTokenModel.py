from abc import ABC, abstractclassmethod
from typing import Dict, List

class BaseTokenModel(ABC):

    @abstractclassmethod
    def create(cls, id: str) -> str:
        """Creates token assosciated with id and returns it"""
        raise NotImplementedError()

    @abstractclassmethod
    def validate(cls, token: str, id: str) -> bool:
        raise NotImplementedError()

    @abstractclassmethod
    def delete(cls, token:str) -> None:
        raise NotImplementedError()
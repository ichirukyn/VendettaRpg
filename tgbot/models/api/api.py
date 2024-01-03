from typing import Type, TypeVar, Generic

T = TypeVar('T')


class Response(Generic[T]):
    def __init__(self, response, type_: Type[T]):
        self._response = response
        self._type = type_

    @property
    def json(self) -> T:
        data = self._response.json()
        return self._type(**data)

    @property
    def status_code(self):
        return self._response.status_code

    @property
    def headers(self):
        return self._response.headers

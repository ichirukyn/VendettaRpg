from typing import Generic
from typing import Type
from typing import TypeVar

T = TypeVar('T')


class Response(Generic[T]):
    def __init__(self, response, type_: Type[T]):
        self._response = response
        self._type = type_

    async def json(self) -> T:
        data = await self._response.json()
        return self._type(**data)

    @property
    def status(self):
        return self._response.status

    @property
    def headers(self):
        return self._response.headers

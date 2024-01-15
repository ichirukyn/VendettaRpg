from abc import ABC
from abc import abstractmethod


class EffectABC(ABC):
    name = str
    type = str
    attribute = str
    value = int

    @abstractmethod
    def apply(self, hero) -> bool:
        pass

    @abstractmethod
    def cancel(self, hero):
        pass

    @abstractmethod
    def check(self):
        pass


class EffectParentABC(ABC):
    id = int
    name = str
    desc = str
    desc_short = str
    entity = None

    bonuses = []
    effects = []

    @abstractmethod
    def activate(self) -> str:
        pass

    @abstractmethod
    def deactivate(self) -> str:
        pass

    @abstractmethod
    def check(self) -> bool:
        pass

    @abstractmethod
    def apply(self):
        pass

    @abstractmethod
    def cancel(self):
        pass

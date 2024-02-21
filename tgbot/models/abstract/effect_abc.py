from abc import ABC
from abc import abstractmethod


class EffectABC(ABC):
    name = str
    type = str
    attribute = str
    value = int

    @abstractmethod
    def apply(self, hero, target=None) -> bool:
        pass

    @abstractmethod
    def cancel(self, hero, target=None):
        pass

    @abstractmethod
    def check(self, entity):
        pass


class EffectParentABC(ABC):
    id = int
    name = str
    desc = str
    desc_short = str

    bonuses = []
    effects = []

    @abstractmethod
    def activate(self, entity) -> str:
        pass

    @abstractmethod
    def deactivate(self, entity) -> str:
        pass

    @abstractmethod
    def check(self, entity) -> bool:
        pass

    @abstractmethod
    def apply(self, entity):
        pass

    @abstractmethod
    def cancel(self, entity):
        pass

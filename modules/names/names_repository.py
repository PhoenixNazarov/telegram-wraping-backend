from abc import ABC, abstractmethod
from typing import Optional

from modules.names.entity.name import Name


class NamesRepository(ABC):
    @abstractmethod
    async def save_name(self, name: Name) -> Name:
        pass

    @abstractmethod
    async def get_name(self, name_id: int) -> Optional[Name]:
        pass

    @abstractmethod
    async def get_names(self) -> list[Name]:
        pass

    @abstractmethod
    async def delete_name(self, name_id: int):
        pass

from abc import ABC, abstractmethod
from typing import Optional

from modules.names.entity.parsing import Parsing


class ParsingRepository(ABC):
    @abstractmethod
    async def save_parsing(self, parsing: Parsing) -> Parsing:
        pass

    @abstractmethod
    async def delete_parsing(self, parsing_id: int):
        pass

    @abstractmethod
    async def get_parsing(self, parsing_id: int) -> Optional[Parsing]:
        pass

    @abstractmethod
    async def get_parsings(self) -> list[Parsing]:
        pass

from abc import ABC, abstractmethod


class AccountCategoryRepository(ABC):
    @abstractmethod
    async def get_categories(self) -> list[str]:
        pass

    @abstractmethod
    async def add_category(self, category: str):
        pass

    @abstractmethod
    async def remove_category(self, category: str):
        pass

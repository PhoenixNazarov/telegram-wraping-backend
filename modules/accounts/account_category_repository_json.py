import json
import os
from pathlib import Path

from modules.accounts.account_category_repository import AccountCategoryRepository


def write_if_not_exist(path, string):
    if not os.path.exists(path):
        with open(path, 'w') as file:
            file.write(string)


class AccountCategoryRepositoryJson(AccountCategoryRepository):
    def __init__(self, path):
        self.path = Path(path)
        write_if_not_exist(self.path, '[]')

    def get_base(self):
        with open(self.path, 'r') as file:
            return json.loads(file.read())

    def save_base(self, data):
        with open(self.path, 'w') as file:
            file.write(json.dumps(data))

    async def get_categories(self) -> list[str]:
        return self.get_base()

    async def add_category(self, category: str):
        base = self.get_base()
        base.append(category)
        self.save_base(list(set(base)))

    async def remove_category(self, category: str):
        base = self.get_base()
        try:
            base.remove(category)
        except ValueError:
            pass
        self.save_base(list(set(base)))

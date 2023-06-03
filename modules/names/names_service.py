import itertools
import random
import string
from typing import Optional

from modules.names.entity.name import Name
from modules.names.names_repository import NamesRepository

username_addable = []

for i in list(itertools.permutations(string.ascii_lowercase + string.digits, 2)):
    username_addable.append(i[0] + i[1])

for i in list(itertools.permutations(string.ascii_lowercase + string.digits, 1)):
    username_addable.append(i[0])


class NamesService:
    def __init__(self, names_repository: NamesRepository):
        self.names_repository = names_repository

    def random_username(self, username: str):
        return username + random.choice(list(username_addable))

    async def get_names(self):
        return await self.names_repository.get_names()

    async def get_name(self, name_id: int):
        return await self.names_repository.get_name(name_id)

    async def add_name(self, user_id: int, first_name: str, last_name: str, about: str, username: str,
                       image: Optional[str], categories: list[str]):
        if not username:
            return
        name = Name(id=user_id, first_name=first_name if first_name != "" else None,
                    last_name=last_name if last_name != "" else None,
                    about=about if about != "" else None,
                    username=username,
                    new_username=self.random_username(username), image=image,
                    categories=categories)
        await self.names_repository.save_name(name)

    async def edit_name(self, name_id: int, first_name: Optional[str], last_name: Optional[str], about: Optional[str],
                        username: Optional[str], categories: list[str]) -> Optional[Name]:
        name = await self.names_repository.get_name(name_id)
        if not name:
            return None

        if first_name:
            name.first_name = first_name
        if last_name:
            name.last_name = last_name
        if about:
            name.about = about
        if username:
            name.new_username = username

        name.categories = categories

        return await self.names_repository.save_name(name)

    async def pop_random_name(self) -> Optional[Name]:
        names = await self.names_repository.get_names()
        if len(names) <= 0:
            return
        name = random.choice(names)
        return name

    async def delete_name(self, name_id: int):
        await self.names_repository.delete_name(name_id)

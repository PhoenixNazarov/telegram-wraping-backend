import json
import os
import shutil
from pathlib import Path
from typing import Optional

from modules.names.entity.name import Name
from modules.names.names_repository import NamesRepository


def create_dir_if_not_exist(path):
    if not os.path.exists(path):
        os.mkdir(path)


def write_if_not_exist(path, string):
    if not os.path.exists(path):
        with open(path, 'w') as file:
            file.write(string)


class NamesRepositoryJson(NamesRepository):
    def __init__(self, path: str):
        self.path = Path(path)

        self.image_path = self.path / "images"
        self.info_path = self.path / "info.json"

        create_dir_if_not_exist(self.path)
        create_dir_if_not_exist(self.image_path)
        write_if_not_exist(self.info_path, '{}')

    def get_base(self):
        with open(self.info_path, 'r') as file:
            return json.loads(file.read())

    def save_base(self, data):
        with open(self.info_path, 'w') as file:
            file.write(json.dumps(data))

    def get_image_path(self, user_id):
        return self.image_path / f"{user_id}.png"

    async def save_name(self, name: Name) -> Name:
        base = self.get_base()
        base[str(name.id)] = name.json()
        if name.image:
            if name.image != self.get_image_path(name.id):
                shutil.copy(name.image, self.get_image_path(name.id))
                name.image = self.get_image_path(name.id)
        self.save_base(base)
        return name

    async def get_name(self, name_id: int) -> Optional[Name]:
        base = self.get_base()
        if str(name_id) not in base:
            return None
        name = Name.parse_raw(base[str(name_id)])
        if os.path.exists(self.get_image_path(name_id)):
            name.image = self.get_image_path(name_id)
        return name

    async def get_names(self) -> list[Name]:
        base = self.get_base()
        out = []
        for i in base.values():
            name = Name.parse_raw(i)
            if os.path.exists(self.get_image_path(name.id)):
                name.image = self.get_image_path(name.id)
            out.append(name)
        return out

    async def delete_name(self, name_id: int):
        base = self.get_base()
        if str(name_id) not in base:
            return
        base.pop(str(name_id))
        self.save_base(base)
        if os.path.exists(self.get_image_path(name_id)):
            os.remove(self.get_image_path(name_id))

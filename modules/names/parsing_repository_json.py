import json
import os
from pathlib import Path
from typing import Optional

from modules.names.entity.parsing import Parsing
from modules.names.parsing_repository import ParsingRepository


def create_dir_if_not_exist(path):
    if not os.path.exists(path):
        os.mkdir(path)


def write_if_not_exist(path, string):
    if not os.path.exists(path):
        with open(path, 'w') as file:
            file.write(string)


class ParsingRepositoryJson(ParsingRepository):
    def __init__(self, path: str):
        self.path = Path(path)
        self.image_path = self.path / 'images'
        self.info_path = self.path / "info.json"

        create_dir_if_not_exist(self.path)
        create_dir_if_not_exist(self.image_path)
        write_if_not_exist(self.info_path, '{"id": 0, "parsings": {}}')

    def get_base(self):
        with open(self.info_path, 'r') as file:
            return json.loads(file.read())

    def save_base(self, data):
        with open(self.info_path, 'w') as file:
            file.write(json.dumps(data))

    async def save_parsing(self, parsing: Parsing) -> Parsing:
        base = self.get_base()
        if str(parsing.id) not in base['parsings']:
            base['id'] += 1
            parsing.id = base['id']
            parsing.image_dir = self.image_path
        base['parsings'][str(parsing.id)] = parsing.json()
        self.save_base(base)
        return parsing

    async def delete_parsing(self, parsing_id: int):
        base = self.get_base()
        if str(parsing_id) in base['parsings']:
            base['parsings'].pop(str(parsing_id))
            for i in os.listdir(self.image_path):
                os.remove(self.image_path / i)
            self.save_base(base)

    async def get_parsing(self, parsing_id: int) -> Optional[Parsing]:
        base = self.get_base()
        if str(parsing_id) in base['parsings']:
            return Parsing.parse_raw(base['parsings'][str(parsing_id)])

    async def get_parsings(self) -> list[Parsing]:
        base = self.get_base()
        return [Parsing.parse_raw(i) for i in base['parsings'].values()]

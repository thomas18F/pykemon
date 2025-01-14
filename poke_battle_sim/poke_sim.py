import csv
import random
import importlib.resources

import poke_battle_sim.conf.global_settings as gs


class PokeSim:
    _pokemon_stats = []
    _name_to_id = {}
    _natures = {}
    _nature_list = []
    _move_list = []
    _move_name_to_id = {}
    _type_effectives = []
    _type_to_id = {}
    _ability_list = []
    _abilities = {}
    _item_list = []
    _items = {}

    @classmethod
    def start(cls):
        if len(cls._pokemon_stats):
            return

        with open(importlib.resources.files(gs.DATA_DIR).joinpath(gs.POKEMON_STATS_CSV)) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            next(csv_reader)
            for row in csv_reader:
                for num in gs.POKEMON_STATS_NUMS:
                    row[num] = int(row[num])
                cls._pokemon_stats.append(row)
                cls._name_to_id[row[1]] = row[0]

        with open(importlib.resources.files(gs.DATA_DIR).joinpath(gs.NATURES_CSV)) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            next(csv_reader)
            for row in csv_reader:
                cls._natures[row[0]] = (int(row[1]), int(row[2]))
                cls._nature_list.append(row[0])

        with open(importlib.resources.files(gs.DATA_DIR).joinpath(gs.MOVES_CSV)) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            next(csv_reader)
            for row in csv_reader:
                for num in gs.MOVES_NUM:
                    if row[num]:
                        row[num] = int(row[num])
                cls._move_list.append(row)
                cls._move_name_to_id[row[1]] = row[0]

        with open(importlib.resources.files(gs.DATA_DIR).joinpath(gs.TYPE_EF_CSV)) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            next(csv_reader)
            line_count = 0
            for row in csv_reader:
                cls._type_to_id[row[0]] = line_count
                row = [float(row[i]) for i in range(1, len(row))]
                cls._type_effectives.append(row)
                line_count += 1

        with open(importlib.resources.files(gs.DATA_DIR).joinpath(gs.ABILITIES_CSV)) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            next(csv_reader)
            for row in csv_reader:
                cls._abilities[row[1]] = (row[0], row[2])
                cls._ability_list.append(row[1])

        with open(importlib.resources.files(gs.DATA_DIR).joinpath(gs.ITEMS_CSV)) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            next(csv_reader)
            for row in csv_reader:
                cls._items[row[1]] = (row[0], row[2])
                cls._item_list.append(row[1])

    @classmethod
    def _convert_name_to_id(cls, name: str) -> int:
        if name not in cls._name_to_id:
            return -1
        return cls._name_to_id[name]

    @classmethod
    def get_pokemon_id(cls, name_or_id: str | int) -> int | None:
        if not isinstance(name_or_id, (str, int)):
            return None
        p_id = name_or_id
        if isinstance(name_or_id, str):
            p_id = cls._convert_name_to_id(name_or_id.lower())
        if 0 < p_id < len(cls._pokemon_stats):
            return p_id
        return None

    @classmethod
    def get_pokemon(cls, name_or_id: str | int) -> list | None:
        p_id = cls.get_pokemon_id(name_or_id)
        if not p_id:
            return
        return cls._pokemon_stats[p_id - 1]

    @classmethod
    def nature_conversion(cls, nature: str) -> tuple[int, int] | None:
        if not isinstance(nature, str) or nature not in cls._natures:
            return
        return cls._natures[nature]

    @classmethod
    def get_move_data(cls, moves: [str]) -> list | None:
        if not isinstance(moves, list):
            return
        move_data = []
        move_ids = []
        for move in moves:
            if move not in cls._move_name_to_id:
                return
            move_data.append(cls._move_list[cls._move_name_to_id[move] - 1])
            if move_data[-1][0] in move_ids:
                return
            move_ids.append(move_data[-1][0])
        return move_data

    @classmethod
    def get_single_move(cls, move: str):
        return cls._move_list[cls._move_name_to_id[move] - 1]

    @classmethod
    def check_status(cls, status: str):
        return

    @classmethod
    def get_type_ef(cls, move_type: str, def_type: str) -> float | None:
        if move_type not in cls._type_to_id or def_type not in cls._type_to_id:
            raise Exception
        return cls._type_effectives[cls._type_to_id[move_type]][
            cls._type_to_id[def_type]
        ]

    @classmethod
    def get_all_types(cls) -> list:
        return list(cls._type_to_id.keys())

    @classmethod
    def is_valid_type(cls, type: str) -> bool:
        return type in cls._type_to_id

    @classmethod
    def filter_valid_types(cls, types: list[str]) -> list:
        return [type for type in types if type in cls._type_to_id]

    @classmethod
    def get_rand_move(cls) -> list:
        return random.choice(cls._move_list)

    @classmethod
    def get_rand_ability(cls) -> str:
        return random.choice(cls._ability_list)

    @classmethod
    def get_rand_item(cls) -> str:
        return random.choice(cls._item_list)

    @classmethod
    def get_rand_poke_id(cls) -> int:
        return random.randrange(1, len(cls._pokemon_stats))

    @classmethod
    def get_rand_stats(cls) -> list[int]:
        return [random.randrange(gs.STAT_ACTUAL_MIN, gs.STAT_ACTUAL_MAX + 1) for _ in range(6)]

    @classmethod
    def get_rand_gender(cls) -> str:
        return gs.POSSIBLE_GENDERS[random.randrange(len(gs.POSSIBLE_GENDERS))]

    @classmethod
    def get_rand_level(cls) -> int:
        return random.randrange(gs.LEVEL_MIN, gs.LEVEL_MAX + 1)

    @classmethod
    def get_rand_nature(cls) -> str:
        return random.choice(cls._nature_list)

    @classmethod
    def check_ability(cls, ability: str) -> bool:
        return ability in cls._abilities

    @classmethod
    def check_item(cls, item: str) -> bool:
        return item in cls._items

import unittest
from unittest.mock import patch

from poke_battle_sim import Pokemon, Trainer, Battle
from poke_battle_sim.util.process_ability import calculate_precision_modifier_abilities
from poke_battle_sim.util.process_item import use_item


class TestProcessAbility(unittest.TestCase):

    def test_precision_modifier_default(self):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        pokemon_2 = Pokemon(2, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])
        trainer_2 = Trainer('Misty', [pokemon_2])
        battle = Battle(trainer_1, trainer_2)
        battle.start()

        precision_modifier = calculate_precision_modifier_abilities(
            pokemon_1, pokemon_2, battle.battlefield, battle, pokemon_1.moves[0]
        )

        self.assertEqual(1, precision_modifier)

    def test_precision_modifier_sand_veil(self):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        pokemon_2 = Pokemon(2, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100], ability="sand-veil")
        trainer_1 = Trainer('Ash', [pokemon_1])
        trainer_2 = Trainer('Misty', [pokemon_2])
        battle = Battle(trainer_1, trainer_2)
        battle.start()

        precision_modifier = calculate_precision_modifier_abilities(
            pokemon_1, pokemon_2, battle.battlefield, battle, pokemon_1.moves[0]
        )

        self.assertEqual(1, precision_modifier)

    def test_precision_modifier_sand_veil_on_sand_storm(self):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        pokemon_2 = Pokemon(2, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100], ability="sand-veil")
        trainer_1 = Trainer('Ash', [pokemon_1])
        trainer_2 = Trainer('Misty', [pokemon_2])
        battle = Battle(trainer_1, trainer_2, weather="sandstorm")
        battle.start()

        precision_modifier = calculate_precision_modifier_abilities(
            pokemon_1, pokemon_2, battle.battlefield, battle, pokemon_1.moves[0]
        )

        self.assertEqual(0.8, precision_modifier)

    def test_precision_compound_eyes(self):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100], ability="compound-eyes")
        pokemon_2 = Pokemon(2, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])
        trainer_2 = Trainer('Misty', [pokemon_2])
        battle = Battle(trainer_1, trainer_2)
        battle.start()

        precision_modifier = calculate_precision_modifier_abilities(
            pokemon_1, pokemon_2, battle.battlefield, battle, pokemon_1.moves[0]
        )

        self.assertEqual(1.3, precision_modifier)


if __name__ == '__main__':
    unittest.main()

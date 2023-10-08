import unittest
from unittest.mock import patch

from poke_battle_sim import Pokemon, Trainer


class TestTrainer(unittest.TestCase):

    def test_initialize_trainer(self):
        pokemon = Pokemon(25, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer = Trainer('Ash', [pokemon])

        self.assertEqual(trainer.name, "Ash")
        self.assertFalse(trainer.in_battle)
        self.assertIsNone(trainer.selection)
        self.assertEqual(len(trainer.poke_list), 1)
        self.assertEqual(trainer.poke_list[0], pokemon)

    def test_initialize_trainer_with_multiple_pokemons(self):
        pokemon_1 = Pokemon(25, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        pokemon_2 = Pokemon(25, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        pokemon_3 = Pokemon(25, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        pokemon_4 = Pokemon(25, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        pokemon_5 = Pokemon(25, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        pokemon_6 = Pokemon(25, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer = Trainer('Ash', [pokemon_1, pokemon_2, pokemon_3, pokemon_4, pokemon_5, pokemon_6])

        self.assertEqual(trainer.name, "Ash")
        self.assertFalse(trainer.in_battle)
        self.assertIsNone(trainer.selection)
        self.assertEqual(len(trainer.poke_list), 6)
        self.assertEqual(trainer.poke_list[0], pokemon_1)
        self.assertEqual(trainer.poke_list[1], pokemon_2)
        self.assertEqual(trainer.poke_list[2], pokemon_3)
        self.assertEqual(trainer.poke_list[3], pokemon_4)
        self.assertEqual(trainer.poke_list[4], pokemon_5)
        self.assertEqual(trainer.poke_list[5], pokemon_6)

    def test_initialize_trainer_without_pokemons(self):
        with self.assertRaises(Exception) as context:
            Trainer('alone_Ash', [])
        self.assertEqual(str(context.exception), "Attempted to create Trainer with invalid number of Pokemon")

    def test_initialize_trainer_with_too_much_pokemons(self):
        pokemon_1 = Pokemon(25, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        pokemon_2 = Pokemon(25, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        pokemon_3 = Pokemon(25, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        pokemon_4 = Pokemon(25, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        pokemon_5 = Pokemon(25, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        pokemon_6 = Pokemon(25, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        pokemon_7 = Pokemon(25, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        with self.assertRaises(Exception) as context:
            Trainer('Ash', [pokemon_1, pokemon_2, pokemon_3, pokemon_4, pokemon_5, pokemon_6, pokemon_7])
        self.assertEqual(str(context.exception), "Attempted to create Trainer with invalid number of Pokemon")

    def test_initialize_trainer_with_duplicate_pokemon(self):
        pokemon_1 = Pokemon(25, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        pokemon_2 = Pokemon(25, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        with self.assertRaises(Exception) as context:
            Trainer('Ash', [pokemon_1, pokemon_2, pokemon_1])
        self.assertEqual(str(context.exception), "Attempted to create Trainer with duplicate Pokemon")

    def test_initialize_trainer_with_already_trained_pokemon(self):
        pokemon = Pokemon(25, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        Trainer('first_Ash', [pokemon])
        with self.assertRaises(Exception) as context:
            Trainer('another_Ash', [pokemon])
        self.assertEqual(str(context.exception), "Attempted to create Trainer with Pokemon in another Trainer's party")

    def test_is_valid_action_empty_list(self):
        pokemon = Pokemon(25, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer = Trainer('Ash', [pokemon])

        self.assertFalse(trainer.is_valid_action([]))

    def test_is_valid_action_not_enough_values(self):
        pokemon = Pokemon(25, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer = Trainer('Ash', [pokemon])

        self.assertFalse(trainer.is_valid_action(["move"]))

    @patch('poke_battle_sim.core.trainer.Trainer.can_use_move')
    def test_is_valid_action_move_test_use(self, mock_can_use_move):
        pokemon = Pokemon(25, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer = Trainer('Ash', [pokemon])

        mock_can_use_move.return_value = True
        self.assertTrue(trainer.is_valid_action(["move", "tackle"]))

    @patch('poke_battle_sim.core.trainer.Trainer.can_use_item')
    def test_is_valid_action_item_test_use(self, mock_can_use_item):
        pokemon = Pokemon(25, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer = Trainer('Ash', [pokemon])

        mock_can_use_item.return_value = True
        self.assertTrue(trainer.is_valid_action(["item", "oran-berry", "0"]))

    @patch('poke_battle_sim.core.trainer.Trainer.can_switch_out')
    def test_is_valid_action_switch_out_test_use(self, mock_can_switch_out):
        pokemon = Pokemon(25, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer = Trainer('Ash', [pokemon])

        mock_can_switch_out.return_value = True
        self.assertTrue(trainer.is_valid_action(["other", "switch"]))

    def test_can_switch_out_test_use_on_unstarted_trainer(self):
        pokemon = Pokemon(25, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer = Trainer('Ash', [pokemon])

        with self.assertRaises(Exception) as context:
            trainer.can_switch_out()
        self.assertEqual(str(context.exception), "Trainer must be in battle")


if __name__ == '__main__':
    unittest.main()

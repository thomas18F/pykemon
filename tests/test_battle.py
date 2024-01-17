import unittest
from unittest.mock import patch

from poke_battle_sim import Trainer, Pokemon, Battle
from poke_battle_sim.util import process_move


class TestBattle(unittest.TestCase):

    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_simple_battle(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        self.assertFalse(battle.battle_started)
        battle.start()
        self.assertTrue(battle.battle_started)
        self.assertEqual(0, battle.turn_count)

        mock_calculate_crit.return_value = False
        battle.turn(["move", "tackle"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Tackle!',
            'CHARMANDER fainted!',
            'Ash has defeated Misty!'
        ]

        self.assertEqual(expected_battle_text, battle.get_all_text())
        self.assertEqual('tackle', battle.last_move.name)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertEqual(trainer_1, battle.winner)
        self.assertEqual('other', battle.battlefield.get_terrain())

    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_pokemon_nickname_usage(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1], nickname="from Ash")
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 100], nickname="from Misty")
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["move", "tackle"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out FROM ASH!',
            'Misty sent out FROM MISTY!',
            'Turn 1:',
            'FROM MISTY used Tackle!',
            'FROM ASH used Tackle!',
            'FROM MISTY fainted!',
            'Ash has defeated Misty!'
        ]

        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    def test_battle_with_terrain(self):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2, terrain="water")

        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual('water', battle.battlefield.get_terrain())

    def test_battle_with_invalid_terrain(self):
        with self.assertRaises(Exception) as context:
            pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            trainer_1 = Trainer('Ash', [pokemon_1])

            pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
            trainer_2 = Trainer('Misty', [pokemon_2])

            Battle(trainer_1, trainer_2, terrain="invalid_terrain")
        self.assertEqual("Attempted to create Battle with invalid terrain type", str(context.exception))

    def test_battle_with_weather(self):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2, weather="rain")

        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual('rain', battle.battlefield.weather)

    def test_battle_with_invalid_weather(self):
        with self.assertRaises(Exception) as context:
            pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            trainer_1 = Trainer('Ash', [pokemon_1])

            pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
            trainer_2 = Trainer('Misty', [pokemon_2])

            Battle(trainer_1, trainer_2, weather="invalid_weather")
        self.assertEqual("Attempted to create Battle with invalid weather", str(context.exception))

    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_battle_with_weather_has_infinite_duration(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 1, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 1, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2, weather="rain")
        battle.start()

        expected_battle_text = ['Ash sent out BULBASAUR!', 'Misty sent out CHARMANDER!']

        mock_calculate_crit.return_value = False
        for turn_i in range(1, 12):
            battle.turn(["move", "tackle"], ["move", "tackle"])
            expected_battle_text += [
                'Turn ' + str(turn_i) + ':', 'BULBASAUR used Tackle!', 'CHARMANDER used Tackle!', 'Rain continues to fall.'
            ]
        self.assertEqual('rain', battle.battlefield.weather)

        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(11, battle.turn_count)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_critical_damage(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = True
        battle.turn(["move", "tackle"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Tackle!',
            'A critical hit!',
            'CHARMANDER fainted!',
            'Ash has defeated Misty!'
        ]

        self.assertTrue(battle.battle_started)
        self.assertEqual('tackle', battle.last_move.name)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertEqual(trainer_1, battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_no_pp_on_all_moves(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["tackle", "thunder"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        self.assertEqual(2, len(pokemon_1.moves))
        pokemon_1.moves[0].current_pp = 0
        pokemon_1.moves[1].current_pp = 0
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["move", "tackle"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR has no moves left!',
            'BULBASAUR used Struggle!',
            'CHARMANDER fainted!',
            'Ash has defeated Misty!'
        ]

        self.assertEqual('struggle', battle.last_move.name)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertEqual(trainer_1, battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    def test_no_pp_on_the_selected_move(self):
        with self.assertRaises(Exception) as context:
            pokemon_1 = Pokemon(1, 22, ["tackle", "thunder"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            self.assertEqual(2, len(pokemon_1.moves))

            pokemon_1.moves[0].current_pp = 0
            trainer_1 = Trainer('Ash', [pokemon_1])

            pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
            trainer_2 = Trainer('Misty', [pokemon_2])

            battle = Battle(trainer_1, trainer_2)
            battle.start()

            battle.turn(["move", "tackle"], ["move", "tackle"])
        self.assertEqual("Trainer 1 attempted to use move not in Pokemon's moveset", str(context.exception))

    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_default_trainer_selection(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
        pokemon_3 = Pokemon(5, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
        pokemon_4 = Pokemon(6, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2, pokemon_3, pokemon_4])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["move", "tackle"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Tackle!',
            'CHARMANDER fainted!',
            'Misty sent out CHARMELEON!'
        ]

        self.assertTrue(battle.battle_started)
        self.assertEqual('tackle', battle.last_move.name)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_trainer_selection_initialization(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        def selection_misty(trainer: Trainer):
            trainer.current_poke = trainer.poke_list[-1]
        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
        pokemon_3 = Pokemon(5, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
        pokemon_4 = Pokemon(6, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2, pokemon_3, pokemon_4], selection_misty)

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["move", "tackle"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Tackle!',
            'CHARMANDER fainted!',
            'Misty sent out CHARIZARD!'
        ]

        self.assertTrue(battle.battle_started)
        self.assertEqual('tackle', battle.last_move.name)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_invalid_pokemon_selection_trainer(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        def selection_misty(trainer: Trainer):
            trainer.current_poke = trainer.poke_list[0]

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
        pokemon_3 = Pokemon(5, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
        pokemon_4 = Pokemon(6, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2, pokemon_3, pokemon_4], selection_misty)

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["move", "tackle"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Tackle!',
            'CHARMANDER fainted!',
            'Misty sent out CHARMELEON!'
        ]

        self.assertTrue(battle.battle_started)
        self.assertEqual('tackle', battle.last_move.name)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    def test_battle_turn_without_start_battle(self):
        with self.assertRaises(Exception) as context:
            pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            trainer_1 = Trainer('Ash', [pokemon_1])

            pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[1, 100, 100, 100, 100, 1])
            trainer_2 = Trainer('Misty', [pokemon_2])

            battle = Battle(trainer_1, trainer_2)
            battle.turn(["move", "tackle"], ["move", "tackle"])
        self.assertEqual("Cannot use turn on Battle that hasn't started", str(context.exception))

    def test_launch_battle_with_trainer_already_in_battle(self):
        with self.assertRaises(Exception) as context:
            pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            trainer_1 = Trainer('Ash', [pokemon_1])

            pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            trainer_2 = Trainer('Misty', [pokemon_2])

            pokemon_3 = Pokemon(7, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            trainer_3 = Trainer('Red', [pokemon_3])

            battle_1 = Battle(trainer_1, trainer_2)
            battle_1.start()

            battle_2 = Battle(trainer_1, trainer_3)
            battle_2.start()

        self.assertEqual("Attempted to create Battle with Trainer already in battle", str(context.exception))

    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_use_heal_item(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100], cur_hp=50)
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(5, 22, ["splash"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["item", "oran-berry", "0"], ["move", "splash"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMELEON!',
            'Turn 1:',
            'Ash used one Oran Berry on BULBASAUR!',
            'BULBASAUR regained health!',
            'CHARMELEON used Splash!',
            'But nothing happened!'
        ]

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(60, battle.t1.current_poke.cur_hp)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_use_pp_restore_item(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        pokemon_1.moves[0].current_pp = 15
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(5, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["item", "leppa-berry", "0", "0"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMELEON!',
            'Turn 1:',
            'Ash used one Leppa Berry on BULBASAUR!',
            'BULBASAUR\'s Tackle\'s pp was restored!',
            'CHARMELEON used Tackle!'
        ]

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())
        self.assertEqual(25, battle.t1.current_poke.moves[0].current_pp)

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_automatic_use_of_item(self, mock_calculate_crit, mock_calculate_multiplier):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1], cur_hp=60, item="oran-berry")
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(5, 22, ["tackle"], "male", stats_actual=[100, 300, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        self.assertEqual('oran-berry', pokemon_1.item)
        self.assertEqual('oran-berry', pokemon_1.o_item)
        self.assertEqual('oran-berry', pokemon_1.h_item)

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "tackle"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMELEON!',
            'Turn 1:',
            'CHARMELEON used Tackle!',
            'BULBASAUR used Tackle!',
            'BULBASAUR ate its Oran Berry!',
            'BULBASAUR regained health!'
        ]

        self.assertIsNone(pokemon_1.item)
        self.assertEqual('oran-berry', pokemon_1.o_item)
        self.assertIsNone(pokemon_1.h_item)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(43, battle.t1.current_poke.cur_hp)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_automatic_use_of_item_not_working_on_potion(self, mock_calculate_crit, mock_calculate_multiplier):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1], cur_hp=60, item="potion")
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(5, 22, ["tackle"], "male", stats_actual=[100, 300, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        self.assertEqual('potion', pokemon_1.item)
        self.assertEqual('potion', pokemon_1.o_item)
        self.assertEqual('potion', pokemon_1.h_item)

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "tackle"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMELEON!',
            'Turn 1:',
            'CHARMELEON used Tackle!',
            'BULBASAUR used Tackle!'
        ]

        self.assertEqual('potion', pokemon_1.item)
        self.assertEqual('potion', pokemon_1.o_item)
        self.assertEqual('potion', pokemon_1.h_item)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(33, battle.t1.current_poke.cur_hp)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_switch_out(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        pokemon_2 = Pokemon(2, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1, pokemon_2])

        pokemon_3 = Pokemon(5, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_3])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["other", "switch"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMELEON!',
            'Turn 1:',
            'Ash sent out IVYSAUR!',
            'CHARMELEON used Tackle!'
        ]

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())
        self.assertEqual(pokemon_2, battle.t1.current_poke)

    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_wrong_action_type(self, mock_calculate_crit):
        with self.assertRaises(Exception) as context:
            pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            trainer_1 = Trainer('Ash', [pokemon_1])

            pokemon_2 = Pokemon(5, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            trainer_2 = Trainer('Misty', [pokemon_2])

            battle = Battle(trainer_1, trainer_2)
            battle.start()

            mock_calculate_crit.return_value = False
            battle.turn(["another command", "switch"], ["move", "tackle"])

        self.assertEqual("Trainer 1 invalid turn action", str(context.exception))

    def test_switch_out_with_one_pokemon_in_team(self):
        with self.assertRaises(Exception) as context:
            pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            trainer_1 = Trainer('Ash', [pokemon_1])

            pokemon_2 = Pokemon(5, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            trainer_2 = Trainer('Misty', [pokemon_2])

            battle = Battle(trainer_1, trainer_2)
            battle.start()

            battle.turn(["other", "switch"], ["move", "tackle"])
        self.assertEqual("Trainer attempted make an invalid switch out", str(context.exception))

    def test_switch_out_with_trapped_pokemon(self):
        with self.assertRaises(Exception) as context:
            pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            pokemon_2 = Pokemon(2, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            trainer_1 = Trainer('Ash', [pokemon_1, pokemon_2])

            pokemon_3 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
            trainer_2 = Trainer('Misty', [pokemon_3])

            battle = Battle(trainer_1, trainer_2)
            battle.start()

            pokemon_1.trapped = True

            battle.turn(["other", "switch"], ["move", "tackle"])
        self.assertEqual("Trainer attempted to switch out Pokemon that's trapped", str(context.exception))

    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_natural_cure_healing_on_switch_out(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100], ability="natural-cure")
        pokemon_2 = Pokemon(2, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        pokemon_1.nv_status = 5
        pokemon_1.nv_counter = 2
        trainer_1 = Trainer('Ash', [pokemon_1, pokemon_2])

        pokemon_3 = Pokemon(5, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_3])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["other", "switch"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMELEON!',
            'Turn 1:',
            'Ash sent out IVYSAUR!',
            'CHARMELEON used Tackle!'
        ]

        self.assertEqual(0, pokemon_1.nv_status)
        self.assertEqual(0, pokemon_1.nv_counter)
        self.assertEqual(0, pokemon_2.nv_status)
        self.assertEqual(0, pokemon_2.nv_counter)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())
        self.assertEqual(pokemon_2, battle.t1.current_poke)

    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_weather_ball_water_type(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["weather-ball"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["rain-dance"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["move", "weather-ball"], ["move", "rain-dance"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER used Rain Dance!',
            'It started to rain!',
            'BULBASAUR used Weather Ball!',
            "It's super effective!",
            'Rain continues to fall.'
        ]

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_weather_ball_rock_type(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["weather-ball"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["sandstorm"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["move", "weather-ball"], ["move", "sandstorm"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER used Sandstorm!',
            'A sandstorm brewed',
            'BULBASAUR used Weather Ball!',
            "It's super effective!",
            'The sandstorm is raging.',
            'CHARMANDER is buffeted by the Sandstorm!',
            'BULBASAUR is buffeted by the Sandstorm!'
        ]

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_weather_ball_clear_weather(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["weather-ball"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(92, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["move", "weather-ball"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out GASTLY!',
            'Turn 1:',
            'GASTLY used Tackle!',
            'BULBASAUR used Weather Ball!',
            "It doesn't affect GASTLY"
        ]

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move.give_nv_status')
    @patch('poke_battle_sim.util.process_move._calculate_hit_or_miss')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_fire_blast(self, mock_calculate_crit, mock_calculate_multiplier, mock_calculate_hit_or_miss, mock_status):
        pokemon_1 = Pokemon(1, 22, ["fire-blast"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_calculate_hit_or_miss.return_value = True
        battle.turn(["move", "fire-blast"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Fire Blast!',
            "It's not very effective...",
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(88, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move.give_nv_status')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_default_natural_power(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_status
    ):
        pokemon_1 = Pokemon(1, 22, ["nature-power"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "nature-power"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Nature Power!',
            'Nature Power turned into Tri Attack!',
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(81, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move.give_nv_status')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_natural_power_in_building(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_status
    ):
        pokemon_1 = Pokemon(1, 22, ["nature-power"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2, "building")
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "nature-power"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Nature Power!',
            'Nature Power turned into Tri Attack!',
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(81, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_natural_power_in_sand(
            self, mock_calculate_crit, mock_calculate_multiplier
    ):
        pokemon_1 = Pokemon(1, 22, ["nature-power"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2, "sand")
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "nature-power"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Nature Power!',
            'Nature Power turned into Earthquake!',
            "It's super effective!",
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(53, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._flinch')
    @patch('poke_battle_sim.util.process_move._calculate_hit_or_miss')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_natural_power_in_cave(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_calculate_hit_or_miss, mock_flinch
    ):
        pokemon_1 = Pokemon(1, 22, ["nature-power"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2, "cave")
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_calculate_hit_or_miss.return_value = True
        battle.turn(["move", "nature-power"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Nature Power!',
            'Nature Power turned into Rock Slide!',
            "It's super effective!",
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(64, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_natural_power_in_tall_grass(
            self, mock_calculate_crit, mock_calculate_multiplier
    ):
        pokemon_1 = Pokemon(1, 22, ["nature-power"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2, "tall-grass")
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "nature-power"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Nature Power!',
            'Nature Power turned into Seed Bomb!',
            "It's not very effective...",
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(86, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_hit_or_miss')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_natural_power_in_water(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_calculate_hit_or_miss
    ):
        pokemon_1 = Pokemon(1, 22, ["nature-power"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2, "water")
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_calculate_hit_or_miss.return_value = True
        battle.turn(["move", "nature-power"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Nature Power!',
            'Nature Power turned into Hydro Pump!',
            "It's super effective!",
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(49, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move.give_nv_status')
    @patch('poke_battle_sim.util.process_move._calculate_hit_or_miss')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_natural_power_in_snow(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_calculate_hit_or_miss, mock_status
    ):
        pokemon_1 = Pokemon(1, 22, ["nature-power"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2, "snow")
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_calculate_hit_or_miss.return_value = True
        battle.turn(["move", "nature-power"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Nature Power!',
            'Nature Power turned into Blizzard!',
            "It's not very effective...",
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(88, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move.give_nv_status')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_natural_power_in_ice(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_status
    ):
        pokemon_1 = Pokemon(1, 22, ["nature-power"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2, "ice")
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "nature-power"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Nature Power!',
            'Nature Power turned into Ice Beam!',
            "It's not very effective...",
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(90, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_earthquake(
            self, mock_calculate_crit, mock_calculate_multiplier
    ):
        pokemon_1 = Pokemon(1, 22, ["earthquake"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "earthquake"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Earthquake!',
            "It's super effective!",
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(53, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_earthquake_in_digging_opponent(
            self, mock_calculate_crit, mock_calculate_multiplier
    ):
        pokemon_1 = Pokemon(1, 22, ["earthquake"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["dig"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "earthquake"], ["move", "dig"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER burrowed its way under the ground!',
            'BULBASAUR used Earthquake!',
            "It's super effective!"
        ]

        self.assertEqual(10, pokemon_2.cur_hp)
        self.assertEqual(100, pokemon_1.moves[0].power)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_stealth_roc(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["stealth-rock"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        pokemon_3 = Pokemon(5, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2, pokemon_3])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["move", "stealth-rock"], ["move", "tackle"])
        battle.turn(["move", "stealth-rock"], ["other", "switch"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER used Tackle!',
            'BULBASAUR used Stealth Rock!',
            "Pointed stones float in the air around Misty's team!",
            'Turn 2:',
            'Misty sent out CHARMELEON!',
            'Pointed stones dug into CHARMELEON!',
            'BULBASAUR used Stealth Rock!',
            'But, it failed!'
        ]

        self.assertEqual(75, pokemon_3.cur_hp)

        self.assertEqual(0, battle.t1.stealth_rock)
        self.assertEqual(1, battle.t2.stealth_rock)
        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(2, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    def test_defog_stealth_roc(self):
        pokemon_1 = Pokemon(1, 22, ["defog"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["stealth-rock"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        battle.turn(["move", "defog"], ["move", "stealth-rock"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER used Stealth Rock!',
            "Pointed stones float in the air around Ash's team!",
            'BULBASAUR used Defog!',
            "CHARMANDER's evasion fell!"
        ]

        self.assertEqual(0, battle.t1.stealth_rock)
        self.assertEqual(0, battle.t2.stealth_rock)
        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    def test_defog_remove_fog(self):
        pokemon_1 = Pokemon(1, 22, ["defog"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["splash"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2, weather="fog")
        battle.start()

        battle.turn(["move", "defog"], ["move", "splash"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER used Splash!',
            'But nothing happened!',
            'BULBASAUR used Defog!',
            "CHARMANDER's evasion fell!"
        ]

        self.assertEqual("clear", battle.battlefield.weather)
        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_rapid_spin_stealth_roc(self, mock_calculate_crit, mock_calculate_multiplier):
        pokemon_1 = Pokemon(1, 22, ["rapid-spin"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["stealth-rock"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "rapid-spin"], ["move", "stealth-rock"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER used Stealth Rock!',
            "Pointed stones float in the air around Ash's team!",
            'BULBASAUR used Rapid Spin!'
        ]

        self.assertEqual(88, pokemon_2.cur_hp)

        self.assertEqual(0, battle.t1.stealth_rock)
        self.assertEqual(0, battle.t2.stealth_rock)
        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_surf(
            self, mock_calculate_crit, mock_calculate_multiplier
    ):
        pokemon_1 = Pokemon(1, 22, ["surf"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "surf"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Surf!',
            "It's super effective!",
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(58, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_surf_in_diving_opponent(
            self, mock_calculate_crit, mock_calculate_multiplier
    ):
        pokemon_1 = Pokemon(1, 22, ["surf"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["dive"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "surf"], ["move", "dive"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER hid underwater!',
            'BULBASAUR used Surf!',
            "It's super effective!"
        ]

        self.assertEqual(19, pokemon_2.cur_hp)
        self.assertEqual(90, pokemon_1.moves[0].power)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._generate_2_to_5')
    @patch('poke_battle_sim.util.process_move._calculate_hit_or_miss')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_whirlpool(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_calculate_hit_or_miss, mock_turns
    ):
        pokemon_1 = Pokemon(1, 22, ["whirlpool"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_calculate_hit_or_miss.return_value = True
        mock_turns.return_value = 2
        battle.turn(["move", "whirlpool"], ["move", "tackle"])

        self.assertEqual(75, pokemon_2.cur_hp)
        self.assertEqual(pokemon_1, pokemon_2.binding_poke)
        self.assertEqual("Whirlpool", pokemon_2.binding_type)
        self.assertEqual(1, pokemon_2.v_status[3])

        battle.turn(["move", "whirlpool"], ["move", "tackle"])

        self.assertEqual(50, pokemon_2.cur_hp)
        self.assertIsNone(pokemon_2.binding_poke)
        self.assertIsNone(pokemon_2.binding_type)

        battle.turn(["move", "whirlpool"], ["move", "tackle"])

        self.assertEqual(25, pokemon_2.cur_hp)
        self.assertEqual(pokemon_1, pokemon_2.binding_poke)
        self.assertEqual("Whirlpool", pokemon_2.binding_type)
        self.assertEqual(1, pokemon_2.v_status[3])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Whirlpool!',
            "It's super effective!",
            'CHARMANDER was trapped in the vortex!',
            'CHARMANDER used Tackle!',
            'CHARMANDER is hurt by Whirlpool!',
            'Turn 2:',
            'BULBASAUR used Whirlpool!',
            "It's super effective!",
            'CHARMANDER used Tackle!',
            'CHARMANDER is hurt by Whirlpool!',
            'Turn 3:',
            'BULBASAUR used Whirlpool!',
            "It's super effective!",
            'CHARMANDER was trapped in the vortex!',
            'CHARMANDER used Tackle!',
            'CHARMANDER is hurt by Whirlpool!'
        ]

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(3, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_hit_or_miss')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_whirlpool_in_diving_opponent(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_calculate_hit_or_miss
    ):
        pokemon_1 = Pokemon(1, 22, ["whirlpool"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["dive"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_calculate_hit_or_miss.return_value = True
        battle.turn(["move", "whirlpool"], ["move", "dive"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER hid underwater!',
            'BULBASAUR used Whirlpool!',
            "It's super effective!",
            'CHARMANDER was trapped in the vortex!',
            'CHARMANDER is hurt by Whirlpool!'
        ]

        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertEqual(60, pokemon_2.cur_hp)
        self.assertEqual(35, pokemon_1.moves[0].power)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_low_kick_in_diving_opponent(
            self, mock_calculate_crit, mock_calculate_multiplier
    ):
        pokemon_1 = Pokemon(1, 22, ["low-kick"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["dive"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "low-kick"], ["move", "dive"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER hid underwater!',
            'BULBASAUR used Low Kick!'
        ]

        self.assertEqual(94, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_gust(
            self, mock_calculate_crit, mock_calculate_multiplier
    ):
        pokemon_1 = Pokemon(1, 22, ["gust"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "gust"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Gust!',
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(90, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_hit_or_miss')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_gust_in_air_opponent(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_calculate_hit_or_miss
    ):
        pokemon_1 = Pokemon(1, 22, ["gust"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["bounce"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_calculate_hit_or_miss.return_value = True
        battle.turn(["move", "gust"], ["move", "bounce"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER sprang up!',
            'BULBASAUR used Gust!'
        ]

        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertEqual(81, pokemon_2.cur_hp)
        self.assertEqual(40, pokemon_1.moves[0].power)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_struggle(self, mock_calculate_crit, mock_calculate_multiplier):
        pokemon_1 = Pokemon(1, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        pokemon_1.moves[0].current_pp = 0
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["splash"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "tackle"], ["move", "splash"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR has no moves left!',
            'BULBASAUR used Struggle!',
            'BULBASAUR is hit with recoil!',
            'CHARMANDER used Splash!',
            'But nothing happened!'
        ]

        self.assertEqual(75, pokemon_1.cur_hp)
        self.assertEqual(75, pokemon_1.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual('splash', battle.last_move.name)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._flinch')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_stomp(
            self, mock_calculate_crit, mock_calculate_multiplier, _
    ):
        pokemon_1 = Pokemon(1, 22, ["stomp"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "stomp"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Stomp!',
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(0, pokemon_2.evasion_stage)
        self.assertEqual(84, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_stomp_in_minimized_opponent(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision
    ):
        pokemon_1 = Pokemon(1, 22, ["stomp"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["minimize"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 76
        battle.turn(["move", "stomp"], ["move", "minimize"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER used Minimize!',
            "CHARMANDER's evasion rose!",
            'BULBASAUR used Stomp!'
        ]

        self.assertEqual(1, pokemon_2.evasion_stage)
        self.assertEqual(70, pokemon_2.cur_hp)
        self.assertEqual(65, pokemon_1.moves[0].power)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_stomp_in_other_evasion_move_opponent(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision
    ):
        pokemon_1 = Pokemon(1, 22, ["stomp"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["double-team"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 76
        battle.turn(["move", "stomp"], ["move", "double-team"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER used Double Team!',
            "CHARMANDER's evasion rose!",
            'BULBASAUR used Stomp!',
            'CHARMANDER avoided the attack!'
        ]

        self.assertEqual(1, pokemon_2.evasion_stage)
        self.assertEqual(100, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_absorb(
            self, mock_calculate_crit, mock_calculate_multiplier
    ):
        pokemon_1 = Pokemon(1, 22, ["absorb"], "male", stats_actual=[100, 100, 100, 100, 100, 1], cur_hp=50)
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(7, 22, ["splash"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "absorb"], ["move", "splash"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out SQUIRTLE!',
            'Turn 1:',
            'SQUIRTLE used Splash!',
            'But nothing happened!',
            'BULBASAUR used Absorb!',
            "It's super effective!",
            "SQUIRTLE had it's energy drained!"
        ]

        self.assertEqual(59, pokemon_1.cur_hp)
        self.assertEqual(82, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_absorb_on_heal_block(
            self, mock_calculate_crit, mock_calculate_multiplier
    ):
        pokemon_1 = Pokemon(1, 22, ["absorb"], "male", stats_actual=[100, 100, 100, 100, 100, 1], cur_hp=50)
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(7, 22, ["heal-block"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "absorb"], ["move", "heal-block"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out SQUIRTLE!',
            'Turn 1:',
            'SQUIRTLE used Heal Block!',
            'BULBASAUR was prevented from healing!',
            'BULBASAUR used Absorb!',
            "It's super effective!"
        ]

        self.assertEqual(50, pokemon_1.cur_hp)
        self.assertEqual(82, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_hit_or_miss')
    def test_leech_seed(self, mock_calculate_hit_or_miss):
        pokemon_1 = Pokemon(1, 22, ["leech-seed"], "male", stats_actual=[100, 100, 100, 100, 100, 100], cur_hp=50)
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(7, 22, ["splash"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_hit_or_miss.return_value = True
        battle.turn(["move", "leech-seed"], ["move", "splash"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out SQUIRTLE!',
            'Turn 1:',
            'BULBASAUR used Leech Seed!',
            'SQUIRTLE was seeded!',
            'SQUIRTLE used Splash!',
            'But nothing happened!',
            "SQUIRTLE's health is sapped by Leech Seed!",
            'BULBASAUR regained health!'
        ]

        self.assertEqual(62, pokemon_1.cur_hp)
        self.assertEqual(88, pokemon_2.cur_hp)
        self.assertEqual(1, pokemon_2.v_status[2])

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_hit_or_miss')
    def test_leech_seed_on_heal_block(self, mock_calculate_hit_or_miss):
        pokemon_1 = Pokemon(1, 22, ["leech-seed"], "male", stats_actual=[100, 100, 100, 100, 100, 1], cur_hp=50)
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(7, 22, ["heal-block"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_hit_or_miss.return_value = True
        battle.turn(["move", "leech-seed"], ["move", "heal-block"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out SQUIRTLE!',
            'Turn 1:',
            'SQUIRTLE used Heal Block!',
            'BULBASAUR was prevented from healing!',
            'BULBASAUR used Leech Seed!',
            'SQUIRTLE was seeded!',
            "SQUIRTLE's health is sapped by Leech Seed!"
        ]

        self.assertEqual(50, pokemon_1.cur_hp)
        self.assertEqual(88, pokemon_2.cur_hp)
        self.assertEqual(1, pokemon_2.v_status[2])

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    def test_aqua_ring(self):
        pokemon_1 = Pokemon(1, 22, ["aqua-ring"], "male", stats_actual=[100, 100, 100, 100, 100, 100], cur_hp=50)
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(7, 22, ["splash"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        battle.turn(["move", "aqua-ring"], ["move", "splash"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out SQUIRTLE!',
            'Turn 1:',
            'BULBASAUR used Aqua Ring!',
            'BULBASAUR surrounded itself with a veil of water!',
            'SQUIRTLE used Splash!',
            'But nothing happened!',
            "A veil of water restored BULBASAUR's HP!"
        ]

        self.assertEqual(56, pokemon_1.cur_hp)
        self.assertEqual(100, pokemon_2.cur_hp)
        self.assertEqual(1, pokemon_1.v_status[8])

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    def test_aqua_ring_on_heal_block(self):
        pokemon_1 = Pokemon(1, 22, ["aqua-ring"], "male", stats_actual=[100, 100, 100, 100, 100, 1], cur_hp=50)
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(7, 22, ["heal-block"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        battle.turn(["move", "aqua-ring"], ["move", "heal-block"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out SQUIRTLE!',
            'Turn 1:',
            'SQUIRTLE used Heal Block!',
            'BULBASAUR was prevented from healing!',
            'BULBASAUR used Aqua Ring!',
            'BULBASAUR surrounded itself with a veil of water!'
        ]

        self.assertEqual(50, pokemon_1.cur_hp)
        self.assertEqual(100, pokemon_2.cur_hp)
        self.assertEqual(1, pokemon_1.v_status[8])

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move.paralyze')
    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_thunder(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_precision, mock_paralize
    ):
        pokemon_1 = Pokemon(1, 22, ["thunder"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_precision.return_value = 70
        battle.turn(["move", "thunder"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Thunder!',
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertEqual(75, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move.paralyze')
    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_thunder_in_sun_is_less_precise(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_precision, mock_paralize
    ):
        pokemon_1 = Pokemon(1, 22, ["thunder"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2, weather="sunny")
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_precision.return_value = 51
        battle.turn(["move", "thunder"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Thunder!',
            "BULBASAUR's attack missed!",
            'CHARMANDER used Tackle!',
            'The sunlight is strong.'
        ]

        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertEqual(100, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move.paralyze')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_thunder_in_rain_never_miss(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_paralize
    ):
        pokemon_1 = Pokemon(1, 22, ["thunder"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2, weather="rain")
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "thunder"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Thunder!',
            'CHARMANDER used Tackle!',
            'Rain continues to fall.'
        ]

        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertEqual(75, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move.paralyze')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_electric_move_on_volt_absorb(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_paralize
    ):
        pokemon_1 = Pokemon(1, 22, ["shock-wave"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(
            4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1], cur_hp=50, ability="volt-absorb"
        )
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2, weather="rain")
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "shock-wave"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Shock Wave!',
            'CHARMANDER absorbed shock-wave with Volt Absorb!',
            'CHARMANDER regained health!',
            'CHARMANDER used Tackle!',
            'Rain continues to fall.'
        ]

        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertEqual(75, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move.paralyze')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_electric_move_on_volt_absorb_on_heal_block(
            self, mock_calculate_crit, mock_calculate_multiplier, mock_paralize
    ):
        pokemon_1 = Pokemon(1, 22, ["shock-wave", "heal-block"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(
            4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1], cur_hp=50, ability="volt-absorb"
        )
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "heal-block"], ["move", "tackle"])

        self.assertEqual(50, pokemon_2.cur_hp)
        self.assertEqual(4, pokemon_2.heal_block_count)

        battle.turn(["move", "shock-wave"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Heal Block!',
            'CHARMANDER was prevented from healing!',
            'CHARMANDER used Tackle!',
            'Turn 2:',
            'BULBASAUR used Shock Wave!',
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertEqual(36, pokemon_2.cur_hp)
        self.assertEqual(3, pokemon_2.heal_block_count)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(2, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_smelling_salts(
            self, mock_calculate_crit, mock_calculate_multiplier
    ):
        pokemon_1 = Pokemon(1, 22, ["smelling-salts"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "smelling-salts"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Smelling Salts!',
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(83, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_smelling_salts_on_paralyzed_opponent(
            self, mock_calculate_crit, mock_calculate_multiplier
    ):
        pokemon_1 = Pokemon(1, 22, ["smelling-salts"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()
        process_move.paralyze(pokemon_2, battle)

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "smelling-salts"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'CHARMANDER is paralyzed! It may be unable to move!',
            'Turn 1:',
            'BULBASAUR used Smelling Salts!',
            'CHARMANDER was cured of paralysis!',
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertEqual(68, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move.give_nv_status')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_flamethrower(self, mock_calculate_crit, mock_calculate_multiplier, mock_status):
        pokemon_1 = Pokemon(1, 22, ["flamethrower"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        battle.turn(["move", "flamethrower"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Flamethrower!',
            "It's not very effective...",
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(90, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move.give_nv_status')
    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_flamethrower(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision, mock_status):
        pokemon_1 = Pokemon(1, 22, ["flamethrower"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 99
        battle.turn(["move", "flamethrower"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Flamethrower!',
            "It's not very effective...",
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(90, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move.give_nv_status')
    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_flamethrower_on_thick_fat(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision, mock_status):
        pokemon_1 = Pokemon(1, 22, ["flamethrower"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1], ability="thick-fat")
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 99
        battle.turn(["move", "flamethrower"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Flamethrower!',
            "It's not very effective...",
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertEqual(95, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_hyper_beam(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["splash", "hyper-beam"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 90
        battle.turn(["move", "hyper-beam"], ["move", "tackle"])

        self.assertTrue(pokemon_1.recharging)

        battle.turn(["move", "splash"], ["move", "tackle"])

        self.assertFalse(pokemon_1.recharging)

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Hyper Beam!',
            'CHARMANDER used Tackle!',
            'Turn 2:',
            'BULBASAUR must recharge!',
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertEqual(66, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(2, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_hyper_beam_miss(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["splash", "hyper-beam"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 91
        battle.turn(["move", "hyper-beam"], ["move", "tackle"])

        self.assertFalse(pokemon_1.recharging)

        battle.turn(["move", "splash"], ["move", "tackle"])

        self.assertFalse(pokemon_1.recharging)

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Hyper Beam!',
            "BULBASAUR's attack missed!",
            'CHARMANDER used Tackle!',
            'Turn 2:',
            'BULBASAUR used Splash!',
            'But nothing happened!',
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertEqual(100, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(2, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_seismic_toss(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["seismic-toss"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 99
        battle.turn(["move", "seismic-toss"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Seismic Toss!',
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(78, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_seismic_toss_on_ghost_pokemon(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["seismic-toss"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(92, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["move", "seismic-toss"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out GASTLY!',
            'Turn 1:',
            'BULBASAUR used Seismic Toss!',
            "It doesn't affect GASTLY",
            'GASTLY used Tackle!'
        ]

        self.assertEqual(100, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_night_shade(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["night-shade"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 99
        battle.turn(["move", "night-shade"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Night Shade!',
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(78, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_night_shade_on_normal_pokemon(self, mock_calculate_crit):
        pokemon_1 = Pokemon(1, 22, ["night-shade"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(132, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        battle.turn(["move", "night-shade"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out DITTO!',
            'Turn 1:',
            'BULBASAUR used Night Shade!',
            "It doesn't affect DITTO",
            'DITTO used Tackle!'
        ]

        self.assertEqual(100, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    def test_night_shade_on_air_pokemon(self, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["night-shade"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["fly"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_move_precision.return_value = 94
        battle.turn(["move", "night-shade"], ["move", "fly"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER flew up high!',
            'BULBASAUR used Night Shade!',
            'CHARMANDER avoided the attack!'
        ]

        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertEqual(100, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)

    def test_night_shade_on_protected_pokemon(self):
        pokemon_1 = Pokemon(1, 22, ["night-shade"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["protect"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        battle.turn(["move", "night-shade"], ["move", "protect"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER used Protect!',
            'BULBASAUR used Night Shade!',
            'CHARMANDER protected itself!'
        ]

        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertEqual(100, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_miss_night_shade(self, mock_calculate_crit, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["night-shade"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["sand-attack"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_move_precision.return_value = 99
        battle.turn(["move", "night-shade"], ["move", "sand-attack"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER used Sand Attack!',
            "BULBASAUR's accuracy fell!",
            'BULBASAUR used Night Shade!',
            "BULBASAUR's attack missed!"
        ]

        self.assertEqual(100, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_avoid_night_shade(self, mock_calculate_crit, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["night-shade"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["minimize"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_move_precision.return_value = 99
        battle.turn(["move", "night-shade"], ["move", "minimize"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER used Minimize!',
            "CHARMANDER's evasion rose!",
            'BULBASAUR used Night Shade!',
            'CHARMANDER avoided the attack!'
        ]

        self.assertEqual(100, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    def test_sand_attack(self, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["sand-attack"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["splash"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_move_precision.return_value = 99
        battle.turn(["move", "sand-attack"], ["move", "splash"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Sand Attack!',
            "CHARMANDER's accuracy fell!",
            'CHARMANDER used Splash!',
            'But nothing happened!'
        ]

        self.assertEqual(100, pokemon_2.cur_hp)
        self.assertEqual(0, pokemon_2.evasion_stage)
        self.assertEqual(-1, pokemon_2.accuracy_stage)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    def test_sand_attack_on_fly_pokemon(self, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["sand-attack"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(16, 22, ["splash"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_move_precision.return_value = 99
        battle.turn(["move", "sand-attack"], ["move", "splash"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out PIDGEY!',
            'Turn 1:',
            'BULBASAUR used Sand Attack!',
            "PIDGEY's accuracy fell!",
            'PIDGEY used Splash!',
            'But nothing happened!'
        ]

        self.assertEqual(100, pokemon_2.cur_hp)
        self.assertEqual(0, pokemon_2.evasion_stage)
        self.assertEqual(-1, pokemon_2.accuracy_stage)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    def test_sand_attack_on_levitating_pokemon(self, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["sand-attack"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["splash"], "male", stats_actual=[100, 100, 100, 100, 100, 1], ability="levitate")
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_move_precision.return_value = 99
        battle.turn(["move", "sand-attack"], ["move", "splash"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Sand Attack!',
            "CHARMANDER's accuracy fell!",
            'CHARMANDER used Splash!',
            'But nothing happened!'
        ]

        self.assertEqual(100, pokemon_2.cur_hp)
        self.assertEqual(0, pokemon_2.evasion_stage)
        self.assertEqual(-1, pokemon_2.accuracy_stage)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_fly(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["fly"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 90
        battle.turn(["move", "fly"], ["move", "tackle"])

        self.assertEqual(1, pokemon_1.invulnerability_count)
        self.assertEqual(100, pokemon_2.cur_hp)
        self.assertEqual(14, pokemon_1.moves[0].current_pp)

        battle.turn(["move", "fly"], ["move", "tackle"])

        self.assertEqual(0, pokemon_1.invulnerability_count)
        self.assertEqual(79, pokemon_2.cur_hp)
        self.assertEqual(14, pokemon_1.moves[0].current_pp)

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR flew up high!',
            'CHARMANDER used Tackle!',
            'BULBASAUR avoided the attack!',
            'Turn 2:',
            'BULBASAUR used Fly!',
            'CHARMANDER used Tackle!'
        ]
        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(2, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_fly_with_power_herb(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["fly"], "male", stats_actual=[100, 100, 100, 100, 100, 100], item="power-herb")
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 90
        battle.turn(["move", "fly"], ["move", "tackle"])

        self.assertEqual(0, pokemon_1.invulnerability_count)

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Fly!',
            'BULBASAUR became fully charged due to its Power Herb!',
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertEqual(79, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_dig(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["dig"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 90
        battle.turn(["move", "dig"], ["move", "tackle"])

        self.assertEqual(1, pokemon_1.invulnerability_count)
        self.assertEqual(9, pokemon_1.moves[0].current_pp)
        self.assertEqual(100, pokemon_2.cur_hp)

        battle.turn(["move", "dig"], ["move", "tackle"])

        self.assertEqual(0, pokemon_1.invulnerability_count)
        self.assertEqual(9, pokemon_1.moves[0].current_pp)
        self.assertEqual(62, pokemon_2.cur_hp)

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR burrowed its way under the ground!',
            'CHARMANDER used Tackle!',
            'BULBASAUR avoided the attack!',
            'Turn 2:',
            'BULBASAUR used Dig!',
            "It's super effective!",
            'CHARMANDER used Tackle!'
        ]
        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(2, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_dig_with_power_herb(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["dig"], "male", stats_actual=[100, 100, 100, 100, 100, 100], item="power-herb")
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 90
        battle.turn(["move", "dig"], ["move", "tackle"])

        self.assertEqual(0, pokemon_1.invulnerability_count)

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Dig!',
            'BULBASAUR became fully charged due to its Power Herb!',
            "It's super effective!",
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertEqual(62, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_dive(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["dive"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 90
        battle.turn(["move", "dive"], ["move", "tackle"])

        self.assertEqual(1, pokemon_1.invulnerability_count)
        self.assertEqual(100, pokemon_2.cur_hp)
        self.assertEqual(9, pokemon_1.moves[0].current_pp)

        battle.turn(["move", "dive"], ["move", "tackle"])

        self.assertEqual(0, pokemon_1.invulnerability_count)
        self.assertEqual(62, pokemon_2.cur_hp)
        self.assertEqual(9, pokemon_1.moves[0].current_pp)

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR hid underwater!',
            'CHARMANDER used Tackle!',
            'BULBASAUR avoided the attack!',
            'Turn 2:',
            'BULBASAUR used Dive!',
            "It's super effective!",
            'CHARMANDER used Tackle!'
        ]
        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(2, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_dive_with_power_herb(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["dive"], "male", stats_actual=[100, 100, 100, 100, 100, 100], item="power-herb")
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 90
        battle.turn(["move", "dive"], ["move", "tackle"])

        self.assertEqual(0, pokemon_1.invulnerability_count)

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Dive!',
            'BULBASAUR became fully charged due to its Power Herb!',
            "It's super effective!",
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertEqual(62, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move.paralyze')
    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_bounce(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision, mock_paralyze):
        pokemon_1 = Pokemon(1, 22, ["bounce"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 80
        battle.turn(["move", "bounce"], ["move", "tackle"])

        self.assertEqual(1, pokemon_1.invulnerability_count)
        self.assertEqual(100, pokemon_2.cur_hp)
        self.assertEqual(4, pokemon_1.moves[0].current_pp)

        battle.turn(["move", "bounce"], ["move", "tackle"])

        self.assertEqual(0, pokemon_1.invulnerability_count)
        self.assertEqual(80, pokemon_2.cur_hp)
        self.assertEqual(4, pokemon_1.moves[0].current_pp)

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR sprang up!',
            'CHARMANDER used Tackle!',
            'BULBASAUR avoided the attack!',
            'Turn 2:',
            'BULBASAUR used Bounce!',
            'CHARMANDER used Tackle!'
        ]
        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(2, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move.paralyze')
    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_bounce_with_power_herb(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision, mock_paralyze):
        pokemon_1 = Pokemon(1, 22, ["bounce"], "male", stats_actual=[100, 100, 100, 100, 100, 100], item="power-herb")
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 80
        battle.turn(["move", "bounce"], ["move", "tackle"])

        self.assertEqual(0, pokemon_1.invulnerability_count)

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Bounce!',
            'BULBASAUR became fully charged due to its Power Herb!',
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertEqual(80, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_shadow_force(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["shadow-force"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 90
        battle.turn(["move", "shadow-force"], ["move", "tackle"])

        self.assertEqual(1, pokemon_1.invulnerability_count)
        self.assertEqual(100, pokemon_2.cur_hp)
        self.assertEqual(4, pokemon_1.moves[0].current_pp)

        battle.turn(["move", "shadow-force"], ["move", "tackle"])

        self.assertEqual(0, pokemon_1.invulnerability_count)
        self.assertEqual(73, pokemon_2.cur_hp)
        self.assertEqual(4, pokemon_1.moves[0].current_pp)

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Shadow Force!',
            'BULBASAUR vanished instantly!',
            'CHARMANDER used Tackle!',
            'BULBASAUR avoided the attack!',
            'Turn 2:',
            'BULBASAUR used Shadow Force!',
            'CHARMANDER used Tackle!'
        ]
        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(2, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_shadow_force_with_power_herb(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["shadow-force"], "male", stats_actual=[100, 100, 100, 100, 100, 100], item="power-herb")
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 90
        battle.turn(["move", "shadow-force"], ["move", "tackle"])

        self.assertEqual(0, pokemon_1.invulnerability_count)

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Shadow Force!',
            'BULBASAUR became fully charged due to its Power Herb!',
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertEqual(73, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_shadow_force_on_protect(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["shadow-force"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["splash", "protect"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 90
        battle.turn(["move", "shadow-force"], ["move", "splash"])
        battle.turn(["move", "shadow-force"], ["move", "protect"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Shadow Force!',
            'BULBASAUR vanished instantly!',
            'CHARMANDER used Splash!',
            'But nothing happened!',
            'Turn 2:',
            'CHARMANDER used Protect!',
            'BULBASAUR used Shadow Force!'
        ]

        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertEqual(73, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(2, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_rollout(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["rollout"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 90
        battle.turn(["move", "rollout"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Rollout!',
            "It's super effective!",
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(84, pokemon_2.cur_hp)
        self.assertEqual(19, pokemon_1.moves[0].current_pp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_rollout_on_defense_curl(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["rollout"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["defense-curl"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 90
        battle.turn(["move", "rollout"], ["move", "defense-curl"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER used Defense Curl!',
            "CHARMANDER's Defense rose!",
            'BULBASAUR used Rollout!',
            "It's super effective!"
        ]
        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertEqual(79, pokemon_2.cur_hp)
        self.assertEqual(19, pokemon_1.moves[0].current_pp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_rollout_scale_damage_then_reset(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["rollout"], "male", stats_actual=[500, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[500, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 90

        battle.turn(["move", "rollout"], ["move", "tackle"])
        expected_hp = 500 - 16
        self.assertEqual(expected_hp, pokemon_2.cur_hp)
        self.assertEqual(1, pokemon_1.move_in_a_row)
        self.assertEqual(19, pokemon_1.moves[0].current_pp)

        battle.turn(["move", "rollout"], ["move", "tackle"])
        expected_hp -= 29
        self.assertEqual(expected_hp, pokemon_2.cur_hp)
        self.assertEqual(2, pokemon_1.move_in_a_row)
        self.assertEqual(19, pokemon_1.moves[0].current_pp)

        battle.turn(["move", "rollout"], ["move", "tackle"])
        expected_hp -= 55
        self.assertEqual(expected_hp, pokemon_2.cur_hp)
        self.assertEqual(3, pokemon_1.move_in_a_row)
        self.assertEqual(19, pokemon_1.moves[0].current_pp)

        battle.turn(["move", "rollout"], ["move", "tackle"])
        expected_hp -= 107
        self.assertEqual(expected_hp, pokemon_2.cur_hp)
        self.assertEqual(4, pokemon_1.move_in_a_row)
        self.assertEqual(19, pokemon_1.moves[0].current_pp)

        battle.turn(["move", "rollout"], ["move", "tackle"])
        expected_hp -= 211
        self.assertEqual(expected_hp, pokemon_2.cur_hp)
        self.assertEqual(0, pokemon_1.move_in_a_row)
        self.assertEqual(19, pokemon_1.moves[0].current_pp)

        battle.turn(["move", "rollout"], ["move", "tackle"])
        expected_hp -= 16
        self.assertEqual(expected_hp, pokemon_2.cur_hp)
        self.assertEqual(1, pokemon_1.move_in_a_row)
        self.assertEqual(18, pokemon_1.moves[0].current_pp)

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Rollout!',
            "It's super effective!",
            'CHARMANDER used Tackle!',
            'Turn 2:',
            'BULBASAUR used Rollout!',
            "It's super effective!",
            'CHARMANDER used Tackle!',
            'Turn 3:',
            'BULBASAUR used Rollout!',
            "It's super effective!",
            'CHARMANDER used Tackle!',
            'Turn 4:',
            'BULBASAUR used Rollout!',
            "It's super effective!",
            'CHARMANDER used Tackle!',
            'Turn 5:',
            'BULBASAUR used Rollout!',
            "It's super effective!",
            'CHARMANDER used Tackle!',
            'Turn 6:',
            'BULBASAUR used Rollout!',
            "It's super effective!",
            'CHARMANDER used Tackle!'
        ]

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(6, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_rollout_defense_curl_bonus_once(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["rollout"], "male", stats_actual=[500, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle", "defense-curl"], "male", stats_actual=[500, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 90

        battle.turn(["move", "rollout"], ["move", "tackle"])
        expected_hp = 500 - 16
        self.assertEqual(expected_hp, pokemon_2.cur_hp)
        self.assertEqual(1, pokemon_1.move_in_a_row)
        self.assertEqual(19, pokemon_1.moves[0].current_pp)

        battle.turn(["move", "rollout"], ["move", "defense-curl"])
        expected_hp -= 29
        self.assertEqual(expected_hp, pokemon_2.cur_hp)
        self.assertEqual(2, pokemon_1.move_in_a_row)
        self.assertEqual(19, pokemon_1.moves[0].current_pp)

        battle.turn(["move", "rollout"], ["move", "tackle"])
        expected_hp -= 73
        self.assertEqual(expected_hp, pokemon_2.cur_hp)
        self.assertEqual(3, pokemon_1.move_in_a_row)
        self.assertEqual(19, pokemon_1.moves[0].current_pp)

        battle.turn(["move", "rollout"], ["move", "tackle"])
        expected_hp -= 142
        self.assertEqual(expected_hp, pokemon_2.cur_hp)
        self.assertEqual(4, pokemon_1.move_in_a_row)
        self.assertEqual(19, pokemon_1.moves[0].current_pp)

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Rollout!',
            "It's super effective!",
            'CHARMANDER used Tackle!',
            'Turn 2:',
            'BULBASAUR used Rollout!',
            "It's super effective!",
            'CHARMANDER used Defense Curl!',
            "CHARMANDER's Defense rose!",
            'Turn 3:',
            'BULBASAUR used Rollout!',
            "It's super effective!",
            'CHARMANDER used Tackle!',
            'Turn 4:',
            'BULBASAUR used Rollout!',
            "It's super effective!",
            'CHARMANDER used Tackle!'
        ]

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(4, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_ice_ball(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["ice-ball"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 90

        battle.turn(["move", "ice-ball"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Ice Ball!',
            "It's not very effective...",
            'CHARMANDER used Tackle!'
        ]
        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertEqual(96, pokemon_2.cur_hp)
        self.assertEqual(19, pokemon_1.moves[0].current_pp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_ice_ball_on_defense_curl(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["ice-ball"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["defense-curl"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 90
        battle.turn(["move", "ice-ball"], ["move", "defense-curl"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'CHARMANDER used Defense Curl!',
            "CHARMANDER's Defense rose!",
            'BULBASAUR used Ice Ball!',
            "It's not very effective..."
        ]
        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertEqual(95, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_fury_cutter(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["fury-cutter"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 95
        battle.turn(["move", "fury-cutter"], ["move", "tackle"])

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Fury Cutter!',
            "It's not very effective...",
            'CHARMANDER used Tackle!'
        ]

        self.assertEqual(1, pokemon_1.move_in_a_row)
        self.assertEqual("fury-cutter", pokemon_1.last_move.name)
        self.assertEqual(95, pokemon_2.cur_hp)

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(1, battle.turn_count)
        self.assertIsNone(battle.winner)
        self.assertEqual(expected_battle_text, battle.get_all_text())

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_fury_cutter_damage_scale(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["fury-cutter"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 95

        battle.turn(["move", "fury-cutter"], ["move", "tackle"])

        self.assertEqual(1, pokemon_1.move_in_a_row)
        self.assertEqual("fury-cutter", pokemon_1.last_move.name)
        self.assertEqual(19, pokemon_1.moves[0].current_pp)
        self.assertEqual(95, pokemon_2.cur_hp)

        battle.turn(["move", "fury-cutter"], ["move", "tackle"])

        self.assertEqual(2, pokemon_1.move_in_a_row)
        self.assertEqual("fury-cutter", pokemon_1.last_move.name)
        self.assertEqual(18, pokemon_1.moves[0].current_pp)
        self.assertEqual(86, pokemon_2.cur_hp)

        battle.turn(["move", "fury-cutter"], ["move", "tackle"])

        self.assertEqual(3, pokemon_1.move_in_a_row)
        self.assertEqual("fury-cutter", pokemon_1.last_move.name)
        self.assertEqual(17, pokemon_1.moves[0].current_pp)
        self.assertEqual(68, pokemon_2.cur_hp)

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Fury Cutter!',
            "It's not very effective...",
            'CHARMANDER used Tackle!',
            'Turn 2:',
            'BULBASAUR used Fury Cutter!',
            "It's not very effective...",
            'CHARMANDER used Tackle!',
            'Turn 3:',
            'BULBASAUR used Fury Cutter!',
            "It's not very effective...",
            'CHARMANDER used Tackle!'
        ]
        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(3, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_fury_cutter_then_rollout(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["fury-cutter", "rollout"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0
        mock_move_precision.return_value = 90

        battle.turn(["move", "fury-cutter"], ["move", "tackle"])

        self.assertEqual(1, pokemon_1.move_in_a_row)
        self.assertEqual("fury-cutter", pokemon_1.last_move.name)
        self.assertEqual(19, pokemon_1.moves[0].current_pp)
        self.assertEqual(95, pokemon_2.cur_hp)

        battle.turn(["move", "fury-cutter"], ["move", "tackle"])

        self.assertEqual(2, pokemon_1.move_in_a_row)
        self.assertEqual("fury-cutter", pokemon_1.last_move.name)
        self.assertEqual(18, pokemon_1.moves[0].current_pp)
        self.assertEqual(86, pokemon_2.cur_hp)

        battle.turn(["move", "rollout"], ["move", "tackle"])

        self.assertEqual(1, pokemon_1.move_in_a_row)
        self.assertEqual("rollout", pokemon_1.last_move.name)
        self.assertEqual(19, pokemon_1.moves[1].current_pp)
        self.assertEqual(70, pokemon_2.cur_hp)

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Fury Cutter!',
            "It's not very effective...",
            'CHARMANDER used Tackle!',
            'Turn 2:',
            'BULBASAUR used Fury Cutter!',
            "It's not very effective...",
            'CHARMANDER used Tackle!',
            'Turn 3:',
            'BULBASAUR used Rollout!',
            "It's super effective!",
            'CHARMANDER used Tackle!'
        ]
        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(3, battle.turn_count)
        self.assertIsNone(battle.winner)

    @patch('poke_battle_sim.util.process_move.get_move_precision')
    @patch('poke_battle_sim.util.process_move._calculate_random_multiplier_damage')
    @patch('poke_battle_sim.util.process_move._calculate_is_critical')
    def test_fury_cutter_damage_reset_on_miss(self, mock_calculate_crit, mock_calculate_multiplier, mock_move_precision):
        pokemon_1 = Pokemon(1, 22, ["fury-cutter"], "male", stats_actual=[100, 100, 100, 100, 100, 100])
        trainer_1 = Trainer('Ash', [pokemon_1])

        pokemon_2 = Pokemon(4, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 1])
        trainer_2 = Trainer('Misty', [pokemon_2])

        battle = Battle(trainer_1, trainer_2)
        battle.start()

        mock_calculate_crit.return_value = False
        mock_calculate_multiplier.return_value = 1.0

        mock_move_precision.return_value = 95
        battle.turn(["move", "fury-cutter"], ["move", "tackle"])

        self.assertEqual(1, pokemon_1.move_in_a_row)
        self.assertEqual("fury-cutter", pokemon_1.last_move.name)
        self.assertEqual(19, pokemon_1.moves[0].current_pp)
        self.assertEqual(95, pokemon_2.cur_hp)

        mock_move_precision.return_value = 96
        battle.turn(["move", "fury-cutter"], ["move", "tackle"])

        self.assertEqual(1, pokemon_1.move_in_a_row)
        self.assertEqual("fury-cutter", pokemon_1.last_move.name)
        self.assertEqual(18, pokemon_1.moves[0].current_pp)
        self.assertEqual(95, pokemon_2.cur_hp)

        mock_move_precision.return_value = 95
        battle.turn(["move", "fury-cutter"], ["move", "tackle"])

        self.assertEqual(1, pokemon_1.move_in_a_row)
        self.assertEqual("fury-cutter", pokemon_1.last_move.name)
        self.assertEqual(17, pokemon_1.moves[0].current_pp)
        self.assertEqual(90, pokemon_2.cur_hp)

        expected_battle_text = [
            'Ash sent out BULBASAUR!',
            'Misty sent out CHARMANDER!',
            'Turn 1:',
            'BULBASAUR used Fury Cutter!',
            "It's not very effective...",
            'CHARMANDER used Tackle!',
            'Turn 2:',
            'BULBASAUR used Fury Cutter!',
            "BULBASAUR's attack missed!",
            'CHARMANDER used Tackle!',
            'Turn 3:',
            'BULBASAUR used Fury Cutter!',
            "It's not very effective...",
            'CHARMANDER used Tackle!'
        ]
        self.assertEqual(expected_battle_text, battle.get_all_text())

        self.assertTrue(battle.battle_started)
        self.assertEqual(trainer_1, battle.t1)
        self.assertEqual(trainer_2, battle.t2)
        self.assertEqual(3, battle.turn_count)
        self.assertIsNone(battle.winner)


if __name__ == '__main__':
    unittest.main()

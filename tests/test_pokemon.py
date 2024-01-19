import unittest

from poke_battle_sim import Pokemon


class TestPokemon(unittest.TestCase):

    def test_initialize_pokemon_with_id(self):
        pokemon = Pokemon(25, 22, ['tackle'], 'male', stats_actual=[100, 100, 100, 100, 100, 100])

        self.assertEqual(25, pokemon.id)
        self.assertEqual('pikachu', pokemon.name)
        self.assertEqual('PIKACHU', pokemon.nickname)
        self.assertEqual('male', pokemon.gender)
        self.assertEqual(22, pokemon.level)
        self.assertEqual(('electric', ''), pokemon.types)
        self.assertEqual(100, pokemon.cur_hp)
        self.assertEqual(100, pokemon.max_hp)
        self.assertEqual([100, 100, 100, 100, 100, 100], pokemon.stats_actual)
        self.assertIsNone(pokemon.trainer)

    def test_initialize_pokemon_with_name(self):
        pokemon = Pokemon("PiKaChU", 22, ['tackle'], 'male', stats_actual=[100, 100, 100, 100, 100, 100])

        self.assertEqual(25, pokemon.id)
        self.assertEqual('pikachu', pokemon.name)
        self.assertEqual('PIKACHU', pokemon.nickname)
        self.assertEqual('male', pokemon.gender)
        self.assertEqual(22, pokemon.level)
        self.assertEqual(('electric', ''), pokemon.types)
        self.assertEqual(100, pokemon.cur_hp)
        self.assertEqual(100, pokemon.max_hp)
        self.assertEqual([100, 100, 100, 100, 100, 100], pokemon.stats_actual)
        self.assertIsNone(pokemon.trainer)

    def test_initialize_pokemon_with_none_moveset(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, None, 'male', stats_actual=[100, 100, 100, 100, 100, 100])
        self.assertEqual("Attempted to create Pokemon with no moveset", str(context.exception))

    def test_initialize_pokemon_without_moves(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, [], 'male', stats_actual=[100, 100, 100, 100, 100, 100])
        self.assertEqual("Attempted to create Pokemon with no moveset", str(context.exception))

    def test_initialize_pokemon_with_too_much_moves(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['pound', 'karate-chop', 'double-slap', 'comet-punch', 'mega-punch'], 'male', stats_actual=[100, 100, 100, 100, 100, 100])
        self.assertEqual("Attempted to create Pokemon with too much moves", str(context.exception))

    def test_initialize_pokemon_with_duplicate_move(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle', 'tackle'], 'male', stats_actual=[100, 100, 100, 100, 100, 100])
        self.assertEqual("Attempted to create Pokemon with invalid moveset", str(context.exception))

    def test_initialize_pokemon_with_bad_id(self):
        with self.assertRaises(Exception) as context:
            Pokemon(10400, 22, ['tackle'], 'male', stats_actual=[100, 100, 100, 100, 100, 100])
        self.assertEqual("Attempted to create Pokemon with invalid name or id", str(context.exception))

    def test_initialize_pokemon_with_bad_name(self):
        with self.assertRaises(Exception) as context:
            Pokemon('a_non_existing_pokemon_name', 22, ['tackle'], 'male', stats_actual=[100, 100, 100, 100, 100, 100])
        self.assertEqual("Attempted to create Pokemon with invalid name or id", str(context.exception))

    def test_initialize_pokemon_with_bad_gender(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle'], 'neutral', stats_actual=[100, 100, 100, 100, 100, 100])
        self.assertEqual("Attempted to create Pokemon with invalid gender", str(context.exception))

    def test_initialize_pokemon_with_no_stats(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle'], 'male', stats_actual=[100, 100, 100, 100, 100])
        self.assertEqual("Attempted to create Pokemon with invalid stats", str(context.exception))

    def test_initialize_pokemon_with_insuffisent_stats_actual(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle'], 'male', stats_actual=[100, 100, 100, 100, 100])
        self.assertEqual("Attempted to create Pokemon with invalid stats", str(context.exception))

    def test_initialize_pokemon_with_too_low_stat(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle'], 'male', stats_actual=[0, 100, 100, 100, 100, 100])
        self.assertEqual("Attempted to create Pokemon with invalid stats", str(context.exception))

    def test_initialize_pokemon_with_one_max_hp(self):
        pokemon = Pokemon(25, 22, ['tackle'], 'male', stats_actual=[1, 100, 100, 100, 100, 100])

        self.assertEqual(25, pokemon.id)
        self.assertEqual('pikachu', pokemon.name)
        self.assertEqual('PIKACHU', pokemon.nickname)
        self.assertEqual('male', pokemon.gender)
        self.assertEqual(22, pokemon.level)
        self.assertEqual(('electric', ''), pokemon.types)
        self.assertEqual(1, pokemon.cur_hp)
        self.assertEqual(1, pokemon.max_hp)
        self.assertEqual([1, 100, 100, 100, 100, 100], pokemon.stats_actual)
        self.assertIsNone(pokemon.trainer)

    def test_initialize_shedinja(self):
        pokemon = Pokemon(292, 22, ['tackle'], 'male', ivs=[16, 16, 16, 16, 16, 16], evs=[0, 0, 0, 0, 0, 0], nature="quirky")

        self.assertEqual(292, pokemon.id)
        self.assertEqual('shedinja', pokemon.name)
        self.assertEqual('SHEDINJA', pokemon.nickname)
        self.assertEqual('male', pokemon.gender)
        self.assertEqual(22, pokemon.level)
        self.assertEqual(('bug', 'ghost'), pokemon.types)
        self.assertEqual(1, pokemon.cur_hp)
        self.assertEqual(1, pokemon.max_hp)
        self.assertEqual([1, 48, 28, 21, 18, 26], pokemon.stats_actual)
        self.assertIsNone(pokemon.trainer)

    def test_initialize_pokemon_with_cur_hp(self):
        pokemon = Pokemon(25, 22, ['tackle'], 'male', stats_actual=[150, 100, 100, 100, 100, 100], cur_hp=100)

        self.assertEqual(25, pokemon.id)
        self.assertEqual('pikachu', pokemon.name)
        self.assertEqual('PIKACHU', pokemon.nickname)
        self.assertEqual('male', pokemon.gender)
        self.assertEqual(22, pokemon.level)
        self.assertEqual(('electric', ''), pokemon.types)
        self.assertEqual(100, pokemon.cur_hp)
        self.assertEqual(150, pokemon.max_hp)
        self.assertEqual([150, 100, 100, 100, 100, 100], pokemon.stats_actual)
        self.assertIsNone(pokemon.trainer)

    def test_initialize_pokemon_with_too_much_cur_hp(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle'], 'male', stats_actual=[100, 100, 100, 100, 100, 100], cur_hp=150)
        self.assertEqual("Attempted to create Pokemon with invalid hp value", str(context.exception))

    def test_initialize_pokemon_with_ev_iv_nature(self):
        pokemon = Pokemon(25, 22, ['tackle'], 'male', ivs=[16, 16, 16, 16, 16, 16], evs=[0, 0, 0, 0, 0, 0], nature="quirky")

        self.assertEqual(25, pokemon.id)
        self.assertEqual('pikachu', pokemon.name)
        self.assertEqual('PIKACHU', pokemon.nickname)
        self.assertEqual('male', pokemon.gender)
        self.assertEqual(22, pokemon.level)
        self.assertEqual(('electric', ''), pokemon.types)
        self.assertEqual(28, pokemon.cur_hp)
        self.assertEqual(28, pokemon.max_hp)
        self.assertEqual([28, 32, 26, 30, 27, 48], pokemon.stats_actual)
        self.assertEqual([16, 16, 16, 16, 16, 16], pokemon.ivs)
        self.assertEqual([0, 0, 0, 0, 0, 0], pokemon.evs)
        self.assertEqual('quirky', pokemon.nature)
        self.assertEqual((4, 4), pokemon.nature_effect)
        self.assertIsNone(pokemon.trainer)

    def test_initialize_pokemon_with_iv_only(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle'], 'male', ivs=[16, 16, 16, 16, 16, 16], nature="quirky")
        self.assertEqual("Attempted to create Pokemon with invalid evs or ivs", str(context.exception))

    def test_initialize_pokemon_with_ev_only(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle'], 'male', evs=[50, 50, 50, 50, 50, 50], nature="quirky")
        self.assertEqual("Attempted to create Pokemon with invalid evs or ivs", str(context.exception))

    def test_initialize_pokemon_without_nature(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle'], 'male', ivs=[16, 16, 16, 16, 16, 16], evs=[50, 50, 50, 50, 50, 50])
        self.assertEqual("Attempted to create Pokemon without providing its nature", str(context.exception))

    def test_initialize_pokemon_with_invalid_nature(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle'], 'male', ivs=[16, 16, 16, 16, 16, 16], evs=[50, 50, 50, 50, 50, 50], nature="a_nature_that_does_not_exist")
        self.assertEqual("Attempted to create Pokemon with invalid nature", str(context.exception))

    def test_initialize_pokemon_with_too_much_iv(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle'], 'male', ivs=[16, 32, 16, 16, 16, 16], evs=[50, 50, 50, 50, 50, 50], nature="quirky")
        self.assertEqual("Attempted to create Pokemon with invalid ivs", str(context.exception))

    def test_initialize_pokemon_with_too_much_ev(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle'], 'male', ivs=[16, 16, 16, 16, 16, 16], evs=[10, 253, 10, 10, 10, 10], nature="quirky")
        self.assertEqual("Attempted to create Pokemon with invalid evs", str(context.exception))

    def test_initialize_pokemon_with_too_much_total_ev(self):
        with self.assertRaises(Exception) as context:
            Pokemon(25, 22, ['tackle'], 'male', ivs=[16, 16, 16, 16, 16, 16], evs=[248, 252, 11, 0, 0, 0], nature="quirky")
        self.assertEqual("Attempted to create Pokemon with invalid evs", str(context.exception))

    def test_initialize_pokemon_with_held_item(self):
        pokemon = Pokemon(25, 22, ['tackle'], 'male', stats_actual=[100, 100, 100, 100, 100, 100], item="oran-berry")

        self.assertEqual(25, pokemon.id)
        self.assertEqual('pikachu', pokemon.name)
        self.assertEqual('PIKACHU', pokemon.nickname)
        self.assertEqual('male', pokemon.gender)
        self.assertEqual('oran-berry', pokemon.o_item)
        self.assertEqual(22, pokemon.level)
        self.assertEqual(('electric', ''), pokemon.types)
        self.assertEqual(100, pokemon.cur_hp)
        self.assertEqual(100, pokemon.max_hp)
        self.assertEqual([100, 100, 100, 100, 100, 100], pokemon.stats_actual)
        self.assertIsNone(pokemon.trainer)

    def test_initialize_pokemon_with_none_held_item(self):
        pokemon = Pokemon(25, 22, ['tackle'], 'male', stats_actual=[100, 100, 100, 100, 100, 100], item=None)

        self.assertEqual(25, pokemon.id)
        self.assertEqual('pikachu', pokemon.name)
        self.assertEqual('PIKACHU', pokemon.nickname)
        self.assertEqual('male', pokemon.gender)
        self.assertIsNone(pokemon.o_item)
        self.assertEqual(22, pokemon.level)
        self.assertEqual(('electric', ''), pokemon.types)
        self.assertEqual(100, pokemon.cur_hp)
        self.assertEqual(100, pokemon.max_hp)
        self.assertEqual([100, 100, 100, 100, 100, 100], pokemon.stats_actual)
        self.assertIsNone(pokemon.trainer)

    def test_can_switch_out_test_use_on_unstarted_trainer(self):
        pokemon = Pokemon(25, 22, ["tackle"], "male", stats_actual=[100, 100, 100, 100, 100, 100])

        with self.assertRaises(Exception) as context:
            pokemon.can_switch_out()
        self.assertEqual("Pokemon must be in battle", str(context.exception))


if __name__ == '__main__':
    unittest.main()

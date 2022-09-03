from __future__ import annotations
import pokemon as pk
import battlefield as bf
import battle as bt
from poke_sim import PokeSim
from move import Move
import random

STATUS = 1
PHYSICAL = 2
SPECIAL = 3

BURNED = 1
FROZEN = 2
PARALYZED = 3
POISONED = 4
ASLEEP = 5
BADLY_POISONED = 5

CONFUSED = 0
FLINCHED = 1
LEECH_SEED = 2

BINDING_COUNT = 3
BIND = 1
WRAP = 2
FIRE_SPIN = 3
CLAMP = 4

NIGHTMARE = 4
CURSE = 5

# STAT_ORDERING_FORMAT
HP = 0
ATK = 1
DEF = 2
SP_ATK = 3
SP_DEF = 4
SPD = 5
STAT_NUM = 6
ACC = 6
EVA = 7

STAT_TO_NAME = {
    0: 'Health',
    1: 'Attack',
    2: 'Defense',
    3: 'Sp. Atk',
    4: 'Sp. Def',
    5: 'Speed',
    6: 'accuracy',
    7: 'evasion'
}

METRONOME_CHECK = ['assist', 'chatter', 'copycat', 'counter', 'covet', 'destiny-bond', 'detect', 'endure', 'feint',
                   'focus-punch', 'follow-me', 'helping-hand', 'me-first', 'mimic', 'mirror-coat', 'mirror-move',
                   'protect', 'sketch', 'sleep-talk', 'snatch', 'struggle', 'switcheroo', 'thief', 'trick']

PROTECT_TARGETS = [8, 9, 10, 11]

def process_move(attacker: pk.Pokemon, defender: pk.Pokemon, battlefield: bf.Battlefield, battle: bt.Battle, move_data: Move, is_first: bool):
    if not _process_pp(attacker, battle, move_data):
        return
    if _pre_process_status(attacker, defender, battlefield, battle, move_data):
        return
    battle._add_text(attacker.nickname + ' used ' + _cap_move_name(move_data.name) + '!')
    attacker.last_move = move_data
    if not _calculate_hit_or_miss(attacker, defender, battlefield, move_data):
        if defender.evasion_stage > 0:
            battle._add_text(defender.nickname + ' avoided the attack!')
        else:
            _missed(attacker, battle)
        return

    attacker.last_successful_move = move_data
    if _protect_check(defender, battle, move_data):
        return
    _process_effect(attacker, defender, battlefield, battle, move_data, is_first)
    battle._faint_check()

def _calculate_type_ef(defender: pokemon.Pokemon, move_data: list):
    if move_data.type == 'typeless':
        return 1
    t_mult = PokeSim.get_type_effectiveness(move_data.type, defender.types[0])
    if defender.types[1]:
        t_mult *= PokeSim.get_type_effectiveness(move_data.type, defender.types[1])
    return t_mult

def _calculate_damage(attacker: pokemon.Pokemon, defender: pokemon.Pokemon, battlefield: bf.Battlefield, battle: bt.Battle,
                      move_data: Move, crit_chance: int = None, inv_bypass: bool = False, skip_fc: bool = False) -> int:
    if move_data.category == STATUS:
        return
    if not defender.is_alive:
        _missed(attacker, battle)
        return
    if not inv_bypass and _invulnerability_check(attacker, defender, battlefield, battle, move_data):
        return
    if not move_data.power:
        return
    t_mult = _calculate_type_ef(defender, move_data)
    if t_mult == 0:
        battle._add_text("It doesn't affect " + defender.nickname)
        return

    cc = crit_chance + attacker.crit_stage if crit_chance else attacker.crit_stage
    if _calculate_crit(cc):
        crit_mult = 2
        battle._add_text("A critical hit!")
    else:
        crit_mult = 1

    if t_mult < 1:
        battle._add_text("It's not very effective...")
    elif t_mult > 1:
        battle._add_text("It's super effective!")

    attacker.calculate_stats_effective()
    defender.calculate_stats_effective()

    if move_data.category == PHYSICAL:
        if crit_mult == 1:
            ad_ratio = attacker.stats_effective[ATK] / defender.stats_effective[DEF]
            if _get_trainer(defender, battle).reflect:
                ad_ratio /= 2
        else:
            atk_ig = max(attacker.stats_actual[ATK], attacker.stats_effective[ATK])
            def_ig = min(defender.stats_actual[DEF], defender.stats_effective[DEF])
            ad_ratio = atk_ig / def_ig
    else:
        if crit_mult == 1:
            ad_ratio = attacker.stats_effective[SP_ATK] / defender.stats_effective[SP_DEF]
            if _get_trainer(defender, battle).light_screen:
                ad_ratio /= 2
        else:
            sp_atk_ig = max(attacker.stats_actual[SP_ATK], attacker.stats_effective[SP_ATK])
            sp_def_ig = min(defender.stats_actual[SP_DEF], defender.stats_effective[SP_DEF])
            ad_ratio = sp_atk_ig / sp_def_ig
    if attacker.nv_status == BURNED:
        burn = 0.5
    else:
        burn = 1

    screen = 1
    targets = 1
    weather_mult = 1
    ff = 1
    if move_data.type == attacker.types[0] or move_data.type == attacker.types[1]:
        stab = 1.5
    else:
        stab = 1
    random_mult = random.randrange(85, 101) / 100

    eb = 1
    tl = 1
    srf = 1
    berry_mult = 1
    item_mult = 1
    first = 1

    damage = (2 * attacker.level / 5 + 2) * move_data.power * ad_ratio / 50 * burn * screen * targets * weather_mult * ff + 2
    damage *= crit_mult * item_mult * first * random_mult * stab * t_mult * srf * eb * tl * berry_mult
    damage = int(damage)
    damage_done = defender.take_damage(damage, move_data)
    if not skip_fc:
        battle._faint_check()
    return damage_done

def _calculate_hit_or_miss(attacker: pokemon.Pokemon, defender: pokemon.Pokemon, battlefield: bf.Battlefield, move_data: Move):
    d_eva_stage = defender.evasion_stage
    if attacker.foresight_target and attacker.foresight_target is defender:
         if defender.evasion_stage > 0:
             d_eva_stage = 0
    stage = attacker.accuracy_stage - d_eva_stage
    stage_mult = max(3, 3 + stage) / max(3, 3 - stage)

    item_mult = 1
    ability_mult = 1
    ma = move_data.acc
    if not ma:
        return True
    if defender.mr_count and defender.mr_target and attacker is defender.mr_target:
        return True
    if ma == -1:
        if move_data.ef_id == 20:
            return random.randrange(1, 101) <= attacker.level - defender.level + 30

    hit_threshold = ma * stage_mult * battlefield.acc_modifier * item_mult * ability_mult
    return random.randrange(1, 101) <= hit_threshold


def _process_effect(attacker: pokemon.Pokemon, defender: pokemon.Pokemon, battlefield: bf.Battlefield, battle: bt.Battle, move_data: Move, is_first: bool):
    if move_data.ef_chance:
        ef_pr = move_data.ef_chance
    else:
        ef_pr = 100
    if random.randrange(1, 101) > ef_pr:
        return True

    ef_id = move_data.ef_id

    if ef_id & 1:
        recipient = defender
    else:
        recipient = attacker

    crit_chance = None
    inv_bypass = False

    if ef_id == 0 or ef_id == 1:
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        return
    elif ef_id == 2 or ef_id == 3:
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if not recipient.is_alive:
            return
        _give_stat_change(recipient, battle, move_data.ef_stat, move_data.ef_amount)
    elif ef_id == 4 or ef_id == 5:
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if recipient.is_alive:
            _give_nv_status(move_data.ef_stat, recipient, battle)
        return
    elif ef_id == 6 or ef_id == 7:
        if not recipient.is_alive:
            _failed(battle)
            return
        if move_data.ef_stat == FLINCHED:
            _flinch(recipient, is_first)
        else:
            _confuse(recipient, battle)
    elif ef_id == 8:
        crit_chance = move_data.ef_amount
    elif ef_id == 10:
        if not defender.is_alive:
            _missed(attacker, battle)
        num_hits = _generate_2_to_5()
        nh = num_hits
        while nh and defender.is_alive:
            _calculate_damage(attacker, defender, battlefield, battle, move_data, skip_fc=True)
            nh -= 1
        battle._add_text("Hit " + str(num_hits) + " time(s)!")
        return
    elif ef_id == 11:
        if not defender.is_alive:
            _missed(attacker, battle)
        _calculate_damage(attacker, defender, battlefield, battle, move_data, skip_fc=True)
        if defender.is_alive:
            _calculate_damage(attacker, defender, battlefield, battle, move_data, skip_fc=True)
        else:
            battle._add_text("Hit 1 time(s)!")
            return
        battle._add_text("Hit 2 time(s)!")
        return
    elif ef_id == 13:
        if recipient.is_alive:
            _give_nv_status(move_data.ef_stat, recipient, battle, True)
        else:
            _failed(battle)
        return
    elif ef_id == 14:
        if not defender.is_alive:
            return
        if move_data.ef_stat == CONFUSED:
            _confuse(defender, battle, True)
    elif ef_id == 16 or ef_id == 17:
        if ef_id == 17 and defender.mist_count:
            battle._add_text(defender.nickname + '\'s protected by mist.')
            return
        _give_stat_change(recipient, battle, move_data.ef_stat, move_data.ef_amount)
    elif ef_id == 19:
        if defender.minimized:
            move_data.power *= 2
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if random.randrange(10) < 3:
            _flinch(defender, is_first)
    elif ef_id == 20:
        if not defender.is_alive:
            _missed(attacker, battle)
        if _calculate_type_ef(defender, move_data) != 0:
            defender.take_damage(65535, move_data)
            if not defender.is_alive:
                battle._add_text('It\'s a one-hit KO!')
        else:
            battle._add_text('It doesn\'t affect ' + defender.nickname)
        return
    elif ef_id == 21:
        if not move_data.ef_stat:
            move_data.ef_stat = 1
            attacker.next_moves.put(move_data)
            battle._add_text(attacker.nickname + ' whipped up a whirlwind!')
            return
        crit_chance = move_data.ef_amount
    elif ef_id == 22:
        if defender.in_air:
            inv_bypass = True
            move_data.power *= 2
    elif ef_id == 23:
        if not move_data.ef_stat:
            move_data.ef_stat = 1
            attacker.next_moves.put(move_data)
            attacker.in_air = True
            attacker.is_invulnerable = True
            battle._pop_text()
            battle._add_text(attacker.nickname + ' flew up high!')
            return
        attacker.in_air = False
        attacker.is_invulnerable = False
    elif ef_id == 24:
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if defender.is_alive and not defender.substitute and not defender.v_status[BINDING_COUNT]:
            defender.v_status[BINDING_COUNT] = _generate_2_to_5()
            defender.binding_poke = attacker
            if move_data.ef_stat == BIND:
                defender.binding_type = 'Bind'
                battle._add_text(defender.nickname + ' was squeezed by ' + attacker.nickname + '!')
            elif move_data.ef_stat == WRAP:
                defender.binding_type = 'Wrap'
                defender.v_status[WRAP] = _generate_2_to_5()
                battle._add_text(defender.nickname + ' was wrapped by ' + attacker.nickname + '!')
            elif move_data.ef_stat == FIRE_SPIN:
                defender.binding_type = 'Fire Spin'
                battle._add_text(defender.nickname + ' was trapped in the vortex!')
            elif move_data.ef_stat == CLAMP:
                defender.binding_type = 'Clamp'
                battle._add_text(attacker.nickname + ' clamped ' + defender.nickname + '!')
        return
    elif ef_id == 25:
        if not defender.is_alive:
            return
        dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data) // 2
        if dmg and dmg == 0 and _calculate_type_ef(defender, move_data) == 0:
            dmg = defender.max_hp // 2
        if not dmg:
            return
        battle._add_text(attacker.nickname + ' kept going and crashed!')
        attacker.take_damage(dmg)
        return
    elif ef_id == 26:
        if defender.in_ground:
            move_data.power *= 2
            inv_bypass = True
    elif ef_id == 27 or ef_id == 29:
        dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if dmg and dmg > 0:
            recoil = dmg // 4 if ef_id == 27 else dmg // 3
            attacker.take_damage(recoil)
            battle._add_text(attacker.nickname + ' is hit with recoil!')
        return
    elif ef_id == 28:
        if not move_data.ef_stat:
            num_turns = random.randrange(1,3)
            move_data.ef_stat = num_turns
            attacker.next_moves.put(move_data)
        else:
            move_data.ef_stat -= 1
            if move_data.ef_stat == 0:
                _calculate_damage(attacker, defender, battlefield, battle, move_data)
                _confuse(attacker, battle)
                return
            else:
                attacker.next_moves.put(move_data)
    elif ef_id == 30:
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if not defender.is_alive:
            return
        if random.randrange(1,6) < 2:
            _poison(defender, battle)
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if defender.is_alive and random.randrange(5) < 1:
            _poison(defender, battle)
        return
    elif ef_id == 31:
        if defender.is_alive and _calculate_type_ef(defender, move_data) != 0:
            defender.take_damage(move_data.ef_amount, move_data)
        else:
            _missed(attacker, battle)
        return
    elif ef_id == 32:
        has_disabled = not all([not move.disabled for move in defender.moves])
        if not defender.last_move or not defender.last_move.cur_pp or has_disabled:
            _failed(battle)
        else:
            disabled_move = defender.last_move
            disabled_move.disabled = random.randrange(4, 8)
            battle._add_text(_get_trainer(defender, battle).name + '\'s ' + defender.nickname + '\'s ' + disabled_move.name + ' was disabled!')
    elif ef_id == 33:
        if attacker.mist_count:
            _failed(battle)
        else:
            battle._add_text(_get_trainer(attacker, battle).name + '\'s team became shrouded in mist!')
            attacker.mist_count = 5
    elif ef_id == 34:
        attacker.recharging = True
    elif ef_id == 35:
        if defender.weight < 100:
            move_data.power = 20
        elif defender.weight < 250:
            move_data.power = 40
        elif defender.weight < 500:
            move_data.power = 60
        elif defender.weight < 1000:
            move_data.power = 80
        elif defender.weight < 2000:
            move_data.power = 100
        else:
            move_data.power = 120
    elif ef_id == 36:
        if defender.is_alive and attacker.last_move_hit_by and attacker.last_move_hit_by.category == PHYSICAL:
            if attacker.last_damage_taken and _calculate_type_ef(defender, move_data):
                defender.take_damage(attacker.last_damage_taken * 2, move_data)
        else:
            _failed(battle)
        return
    elif ef_id == 37:
        if _calculate_type_ef(defender, move_data):
            if defender.is_alive:
                defender.take_damage(attacker.level, move_data)
            else:
                _missed(attacker, battle)
        return
    elif ef_id == 38:
        dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if dmg:
            heal_amount = dmg // 2 if dmg != 1 else 1
            attacker.heal(heal_amount)
            battle._add_text(defender.nickname + ' had it\'s energy drained!')
        return
    elif ef_id == 39:
        if defender.is_alive and not defender.substitute and not defender.v_status[LEECH_SEED]:
            defender.v_status[LEECH_SEED] = 1
            battle._add_text(defender.nickname + ' was seeded!')
    elif ef_id == 40:
        if not move_data.ef_stat:
            battle._pop_text()
            battle._add_text(attacker.nickname + ' absorbed light!')
            move_data.ef_stat = 1
            attacker.next_moves.put(move_data)
            return
    elif ef_id == 41:
        if defender.is_alive and random.randrange(10) < 3:
            _paralyze(defender, battle)
    elif ef_id == 42:
        if not move_data.ef_stat:
            move_data.ef_stat = 1
            attacker.next_moves.put(move_data)
            attacker.in_ground = True
            attacker.is_invulnerable = True
            battle._pop_text()
            battle._add_text(attacker.nickname + ' burrowed its way under the ground!')
            return
        attacker.in_ground = False
        attacker.is_invulnerable = False
    elif ef_id == 43:
        if not attacker.rage:
            attacker.rage = True
            for move in attacker.moves:
                if move.name != 'rage':
                    move.disabled = True
    elif ef_id == 44:
        if attacker.copied or not defender.is_alive or attacker.is_move(defender.last_move.md):
            _failed(battle)
            return
        attacker.copied = Move(defender.last_move.md)
        attacker.copied.max_pp = min(5, attacker.copied.max_pp)
        attacker.copied.cur_pp = attacker.copied.max_pp
        battle._add_text(attacker.nickname + ' learned ' + _cap_move_name(attacker.copied.name))
    elif ef_id == 45:
        # ability check
        _give_stat_change(defender, battle, DEF, -2)
    elif ef_id == 46:
        attacker.heal(attacker.max_hp // 2)
        battle._add_text(attacker.nickname + ' recovered health!')
    elif ef_id == 47:
        attacker.minimized = True
        _give_stat_change(attacker, battle, EVA, 1)
    elif ef_id == 48:
        for move in attacker.moves:
            if move.name == 'rollout' or move.name == 'ice-ball' and move.power == move.o_power:
                move.power *= 2
        _give_stat_change(attacker, battle, DEF, 1)
    elif ef_id == 49:
        t = _get_trainer(attacker, battle)
        if move_data.ef_stat == 1:
            if t.light_screen:
                _failed(battle)
                return
            t.light_screen = 5
            battle._add_text('Light Screen raised ' + t.name + '\'s team\'s Special Defense!')
        elif move_data.ef_stat == 2:
            if t.reflect:
                _failed(battle)
                return
            t.reflect = 5
            battle._add_text('Light Screen raised ' + t.name + '\'s team\'s Defense!')
    elif ef_id == 50:
        attacker.reset_stages()
        defender.reset_stages()
        battle._add_text('All stat changes were eliminated!')
    elif ef_id == 51:
        attacker.crit_stage += 2
        if attacker.crit_stage > 4:
            attacker.crit_stage = 4
        battle._add_text(attacker.nickname + ' is getting pumped!')
    elif ef_id == 52:
        if not move_data.ef_stat:
            attacker.trapped = True
            move_data.ef_stat = 1
            attacker.bide_count = 2 if is_first else 3
            attacker.next_moves.put(move_data)
            attacker.bide_dmg = 0
            battle._add_text(attacker.nickname + ' is storing energy!')
        else:
            battle._pop_text()
            battle._add_text(attacker.nickname + ' unleashed energy!')
            if defender.is_alive:
                defender.take_damage(2 * attacker.bide_dmg, move_data)
            else:
                _missed(attacker, battle)
            attacker.bide_dmg = 0
        return
    elif ef_id == 53:
        move_names = [move.name for move in attacker.moves]
        rand_move = PokeSim.get_rand_move()
        # counter check for loop
        while rand_move in move_names or rand_move in METRONOME_CHECK:
            rand_move = PokeSim.get_rand_move()
        rand_move = Move(rand_move)
        battle._add_text(attacker.nickname + ' used ' + _cap_move_name(rand_move.name) + '!')
        _process_effect(attacker, defender, battlefield, battle, rand_move, is_first)
        return
    elif ef_id == 54:
        if defender.is_alive and defender.last_move:
            battle._add_text(attacker.nickname + ' used ' + _cap_move_name(defender.last_move.name) + '!')
            _process_effect(attacker, defender, battlefield, battle, defender.last_move, is_first)
        else:
            _failed(battle)
        return
    elif ef_id == 55:
        attacker.take_damage(attacker.cur_hp)
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        return
    elif ef_id == 56:
        if not move_data.ef_stat:
            battle._pop_text()
            battle._add_text(attacker.nickname + ' tucked in its head!')
            _give_stat_change(attacker, battle, DEF, 1)
            move_data.ef_stat = 1
            attacker.next_moves.put(move_data)
            return
    elif ef_id == 57:
        if not defender.is_alive:
            _missed(attacker, battle)
        elif defender.nv_status == ASLEEP:
            dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
            if dmg:
                heal_amount = dmg // 2 if dmg != 1 else 1
                attacker.heal(heal_amount)
            battle._add_text(defender.nickname + '\'s dream was eaten!')
        else:
            _failed(battle)
        return
    elif ef_id == 58:
        if not move_data.ef_stat:
            move_data.ef_stat = 1
            defender.next_moves.put(move_data)
            battle._pop_text()
            battle._add_text(attacker.nickname + ' became clocked in a harsh light!')
        else:
            _calculate_damage(attacker, defender, battlefield, battle, move_data, crit_chance=1)
            if random.randrange(10) < 3:
                _flinch(defender, is_first)
        return
    elif ef_id == 59:
        if defender.is_alive and not defender.transformed and not attacker.transformed:
            attacker.transform(defender)
            battle._add_text(attacker.nickname + ' transformed into ' + defender.name + '!')
        else:
            _failed(battle)
        return
    elif ef_id == 60:
        dmg = attacker.level * (random.randrange(0, 11) * 10 + 50) // 100
        if defender.is_alive:
            defender.take_damage(dmg if dmg != 0 else 1, move_data)
        else:
            _missed(attacker, battle)
        return
    elif ef_id == 61:
        battle._add_text('But nothing happened!')
        return
    elif ef_id == 62:
        if not defender.is_alive:
            _failed(battle)
            return
        attacker.take_damage(attacker.cur_hp)
        old_def = defender.stats_actual[DEF]
        defender.stats_actual[DEF] //= 2
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        defender.stats_actual[DEF] = old_def
        return
    elif ef_id == 63:
        attacker.nv_status = ASLEEP
        attacker.nv_counter = 3
        battle._add_text(attacker.nickname + ' went to sleep!')
        attacker.heal(attacker.max_hp)
        battle._add_text(attacker.nickname + ' regained health!')
    elif ef_id == 64:
        move_types = [move.type for move in attacker.moves if move.type not in attacker.types]
        if not len(move_types):
            _failed(battle)
            return
        attacker.types = (move_types[random.randrange(len(move_types))], None)
    elif ef_id == 65:
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if defender.is_alive and random.randrange(5) < 1:
            _give_nv_status(random.randrange(1, 4), defender, battle)
        return
    elif ef_id == 66:
        if not defender.is_alive or _calculate_type_ef(defender, move_data) == 0:
            _failed(battle)
            return
        else:
            dmg = defender.max_hp // 2
            defender.take_damage(dmg if dmg > 0 else 1, move_data)
        return
    elif ef_id == 67:
        if attacker.substitute:
            _failed(battle)
            return
        if attacker.cur_hp - attacker.max_hp // 4 < 0:
            battle._add_text('But it does not have enough HP left to make a substitute!')
            return
        attacker.substitute = attacker.take_damage(attacker.max_hp // 4) + 1
        battle._add_text(attacker.nickname + ' made a substitute!')
    elif ef_id == 68:
        battle._pop_text()
        battle._add_text(attacker.nickname + ' has no moves left!')
        battle._add_text(attacker.nickname + ' used Struggle!')
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        struggle_dmg = attacker.max_hp // 4
        attacker.take_damage(struggle_dmg if struggle_dmg > 0 else 1)
        battle._add_text(attacker.nickname + ' is hit with recoil!')
    elif ef_id == 69:
        if attacker.transformed or not move_data in attacker.o_moves or not defender.is_alive or \
                not defender.last_move or attacker.is_move(defender.last_move.name):
            _failed(battle)
            return
        attacker.moves[move_data.pos] = Move(defender.last_move.md)
    elif ef_id == 70:
        if not defender.is_alive:
            _missed(attacker, battle)
        num_hits = 0
        while num_hits < 3 and defender.is_alive:
            _calculate_damage(attacker, defender, battlefield, battle, move_data, skip_fc=True)
            move_data.power += 10
            num_hits += 1
        battle._add_text('Hit' + str(num_hits) +  'time(s)!')
        return
    elif ef_id == 71:
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if defender.item and not attacker.item:
            battle._add_text(attacker.nickname + ' stole ' + defender.nickname + '\'s ' + defender.item + '!')
            attacker.item = defender.item
            defender.item = None
        return
    elif ef_id == 72:
        if defender.is_alive and not defender.is_invulnerable:
            defender.perma_trapped = True
            battle._add_text(defender.nickname + ' can no longer escape!')
        else:
            _failed(battle)
    elif ef_id == 73:
        if defender.is_alive:
            attacker.mr_count = 2
            attacker.mr_target = defender
            battle._add_text(attacker.nickname + ' took aim at ' + defender.nickname + '!')
        else:
            _failed(battle)
    elif ef_id == 74:
        if defender.is_alive and defender.nv_status == ASLEEP and not defender.substitute:
            defender.v_status[NIGHTMARE] = 1
            battle._add_text(defender.nickname + ' began having a nightmare!')
        else:
            _failed(battle)
    elif ef_id == 75:
        if attacker.nv_status == FROZEN:
            battle._add_text(attacker.nickname + ' thawed out!')
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if defender.is_alive and random.randrange(10) < 1:
            _burn(defender, battle)
        return
    elif ef_id == 76:
        if defender.is_alive and attacker.nv_status == ASLEEP:
            _calculate_damage(attacker, defender, battlefield, battle, move_data)
            if random.randrange(10) < 3:
                _flinch(defender, is_first)
        else:
            _failed(battle)
        return
    elif ef_id == 77:
        if 'ghost' not in attacker.types:
            if attacker.stat_stages[ATK] == 6 and attacker.stat_stages[DEF] == 6 and attacker.stat_stages[SPD] == -6:
                _failed(battle)
                return
            if attacker.stat_stages[ATK] < 6:
                _give_stat_change(attacker, battle, ATK, 1)
            if attacker.stat_stages[DEF] < 6:
                _give_stat_change(attacker, battle, DEF, 1)
            if attacker.stat_stages[SPD] > -6:
                _give_stat_change(attacker, battle, SPD, -1)
        else:
            if not defender.is_alive or defender.v_status[CURSE] or defender.substitute:
                _failed(battle)
                return
            attacker.take_damage(attacker.max_hp // 2)
            defender.v_status[CURSE] = 1
            battle._add_text(attacker.nickname + ' cut its own HP and laid a curse on ' + defender.nickname + '!')
    elif ef_id == 78:
        hp_ratio = int((float(attacker.cur_hp) / attacker.max_hp) * 10000)
        if hp_ratio >= 6719:
            move_data.power = 20
        elif hp_ratio >= 3438:
            move_data.power = 40
        elif hp_ratio >= 2031:
            move_data.power = 80
        elif hp_ratio >= 938:
            move_data.power = 100
        elif hp_ratio >= 313:
            move_data.power = 150
        else:
            move_data.power = 200
    elif ef_id == 79:
        if not attacker.last_move_hit_by:
            _failed(battle)
            return
        last_move_type = attacker.last_move_hit_by.type
        types = PokeSim.get_all_types()
        poss_types = []
        for type in types:
            if PokeSim.get_type_effectiveness(last_move_type, type) < 1:
                poss_types.append(type)
        poss_types = [type for type in poss_types if type not in attacker.types]
        if len(poss_types):
            new_type = poss_types[random.randrange(len(poss_types))]
            attacker.types = (new_type, None)
            battle._add_text(attacker.nickname + ' transformed into the ' + new_type.upper() + ' type!')
        else:
            _failed(battle)
    elif ef_id == 80:
        if defender.is_alive and defender.last_move and defender.last_move.cur_pp:
            if defender.last_move.cur_pp < 4:
                amt_reduced = defender.last_move.cur_pp
            else:
                amt_reduced = 4
            defender.last_move.cur_pp -= amt_reduced
            battle._add_text('It reduced the pp of ' + defender.nickname + '\'s ' + _cap_move_name(defender.last_move.name) + ' by ' + str(amt_reduced) + '!')
        else:
            _failed(battle)
    elif ef_id == 81:
        if attacker.substitute:
            _failed(battle)
        p_chance = min(8, 2 ** attacker.protect_count)
        if random.randrange(p_chance) < 1:
            attacker.is_invulnerable = True
            attacker.protect = True
            attacker.protect_count += 1
        else:
            _failed(battle)
    elif ef_id == 82:
        if attacker.max_hp // 2 > attacker.cur_hp or attacker.stat_stages[ATK] == 6:
            _failed(battle)
            return
        battle._add_text(attacker.nickname + ' cut its own HP and maximized its Attack!')
        attacker.stat_stages[ATK] = 6
    elif ef_id == 83:
        enemy = _get_trainer(defender, battle)
        if enemy.spikes < 3:
            enemy.spikes += 1
            battle._add_text('Spikes were scattered all around the feet of ' + enemy.name + '\'s team!')
        else:
            _failed(battle)
    elif ef_id == 84:
        if defender.is_alive and not attacker.foresight_target:
            attacker.foresight_target = defender
            battle._add_text(attacker.nickname + ' identified ' + defender.nickname + '!')
        else:
            _failed(battle)

    _calculate_damage(attacker, defender, battlefield, battle, move_data, crit_chance, inv_bypass)

def _calculate_crit(crit_chance: int = None):
    if not crit_chance:
        return random.randrange(16) < 1
    elif crit_chance == 1:
        return random.randrange(9) < 1
    elif crit_chance == 2:
        return random.randrange(5) < 1
    elif crit_chance == 3:
        return random.randrange(4) < 1
    elif crit_chance == 4:
        return random.randrange(3) < 1
    else:
        return random.randrange(1000) < crit_chance

def _invulnerability_check(attacker: pokemon.Pokemon, defender: pokemon.Pokemon, battlefield: bf.Battlefield, battle: bt.Battle, move_data: Move) -> bool:
    if defender.is_invulnerable:
        if defender.in_air or defender.in_ground:
            _missed(attacker, battle)
        return True
    return False

def _pre_process_status(attacker: pokemon.Pokemon, defender: pokemon.Pokemon, battlefield: bf.Battlefield, battle: bt.Battle, move_data: Move) -> bool:
    if attacker.nv_status == FROZEN:
        if random.randrange(5) < 4:
            battle._add_text(attacker.nickname + ' is frozen solid!')
            return True
        attacker.nv_status = 0
        battle._add_text(attacker.nickname + ' thawed out!')
    if attacker.nv_status == ASLEEP:
        if not attacker.nv_counter:
            attacker.nv_status = 0
        attacker.nv_counter -= 1
        if attacker.nv_counter:
            battle._add_text(attacker.nickname + ' is fast asleep!')
            if move_data.name == 'snore' or move_data.name == 'sleep-talk':
                return False
            return True
        battle._add_text(attacker.nickname + ' woke up!')
    if attacker.v_status[FLINCHED]:
        attacker.v_status[FLINCHED] = 0
        battle._add_text(attacker.nickname + ' flinched and couldn\'t move')
        return True
    if attacker.nv_status == PARALYZED:
        if random.randrange(4) < 1:
            battle._add_text(attacker.nickname + ' is paralyzed! It can\'t move!')
            return True
    if attacker.v_status[CONFUSED]:
        attacker.v_status[CONFUSED] -= 1
        if attacker.v_status[CONFUSED]:
            battle._add_text(attacker.nickname + ' is confused!')
            if random.randrange(2) < 1:
                battle._add_text('It hurt itself in its confusion!')
                self_attack = Move([0, 'self-attack', 1, 'typeless', 40, 1, 999, 0, 10, 2, 1, '', '', ''])
                _calculate_damage(attacker, attacker, battlefield, battle, self_attack, crit_chance=0)
                return True
    return False

def _process_pp(attacker: pk.Pokemon, battle: bt.Battle, move: Move) -> bool:
    if move.cur_pp == 0:
        raise Exception
    is_disabled = move.disabled
    attacker.reduce_disabled_count()
    if is_disabled:
        battle._add_text(move.name + ' is disabled!')
        return False
    move.cur_pp -= 1
    if move.cur_pp == 0 and attacker.copied and move.name == attacker.copied.name:
        self.copied = None
    return True

def _generate_2_to_5() -> int:
    n = random.randrange(8)
    if n < 3:
        num_hits = 2
    elif n < 6:
        num_hits = 3
    elif n < 7:
        num_hits = 4
    else:
        num_hits = 5
    return num_hits

def _confuse(recipient: pk.Pokemon, battle: bt.Battle, forced: bool = False):
    if recipient.substitute:
        if forced:
            _failed(battle)
        return
    if forced and recipient.v_status[CONFUSED]:
        battle._add_text(recipient.nickname + ' is already confused!')
        return
    recipient.v_status[CONFUSED] = _generate_2_to_5()
    battle._add_text(recipient.nickname + ' became confused!')


def _flinch(recipient: pk.Pokemon, is_first: bool):
    if recipient.substitute:
        return
    if is_first and recipient.is_alive and not recipient.v_status[FLINCHED]:
        recipient.v_status[FLINCHED] = 1


def _give_stat_change(recipient: pokemon.Pokemon, battle: bt.Battle, stat: int, amount: int, forced: bool = False):
    if not recipient.is_alive:
        if forced:
            _failed(battle)
        return
    if recipient.substitute and amount < 0:
        if forced:
            _failed(battle)
        return
    battle._add_text(_stat_text(recipient, stat, amount))
    if stat == 6:
        recipient.accuracy_stage = _fit_stat_bounds(recipient.accuracy_stage + amount)
    elif stat == 7:
        recipient.evasion_stage = _fit_stat_bounds(recipient.evasion_stage + amount)
    else:
        recipient.stat_stages[stat] = _fit_stat_bounds(recipient.stat_stages[stat] + amount)
    return

def _fit_stat_bounds(stage: int):
    if stage >= 0:
        return min(6, stage)
    else:
        return max(-6, stage)

def _stat_text(recipient: pk.Pokemon, stat: int, amount: int) -> str:
    if stat == ACC:
        cur_stage = recipient.accuracy_stage
    elif stat == EVA:
        cur_stage = recipient.evasion_stage
    else:
        cur_stage = recipient.stat_stages[stat]
    if not amount:
        return
    base = recipient.nickname + '\'s ' + STAT_TO_NAME[stat]
    if amount > 0:
        if cur_stage >= 6:
            base += ' won\'t go any higher!'
        elif amount == 1:
            base += ' rose!'
        elif amount == 2:
            base += ' rose sharply!'
        else:
            base += ' rose drastically!'
    else:
        if cur_stage <= -6:
            base += ' won\'t go any lower!'
        elif amount == -1:
            base += ' fell!'
        elif amount == -2:
            base += ' fell harshly!'
        else:
            base += ' fell severely!'
    return base

def _give_nv_status(status: int, recipient: pk.Pokemon, battle: bt.Battle, forced: bool = False):
    if status == BURNED:
        _burn(recipient, battle, forced)
    elif status == FROZEN:
        _freeze(recipient, battle, forced)
    elif status == PARALYZED:
        _paralyze(recipient, battle, forced)
    elif status == POISONED:
        _poison(recipient, battle, forced)
    elif status == ASLEEP:
        _sleep(recipient, battle, forced)
    elif status == BADLY_POISONED:
        _badly_poison(recipient, battle, forced)

def _burn(recipient: pk.Pokemon, battle: bt.Battle, forced: bool = False):
    if recipient.substitute:
        if forced:
            _failed(battle)
        return
    if 'fire' in recipient.types:
        if forced:
            _failed(battle)
        return
    if forced and recipient.nv_status == BURNED:
        battle._add_text(recipient.nickname + ' is already burned!')
    elif not recipient.nv_status:
        recipient.nv_status = BURNED
        recipient.nv_counter = 0
        battle._add_text(recipient.nickname + ' was burned!')

def _freeze(recipient: pk.Pokemon, battle: bt.Battle, forced: bool = False):
    if recipient.substitute:
        if forced:
            _failed(battle)
        return
    if 'ice' in recipient.types:
        if forced:
            _failed(battle)
        return
    if forced and recipient.nv_status == FROZEN:
        battle._add_text(recipient.nickname + ' is already frozen!')
    elif not recipient.nv_status:
        recipient.nv_status = FROZEN
        recipient.nv_counter = 0
        battle._add_text(recipient.nickname + ' was frozen solid!')

def _paralyze(recipient: pk.Pokemon, battle: bt.Battle, forced: bool = False):
    if recipient.substitute:
        if forced:
            _failed(battle)
        return
    if forced and recipient.nv_status == PARALYZED:
        battle._add_text(recipient.nickname + ' is already paralyzed!')
    elif not recipient.nv_status:
        recipient.nv_status = PARALYZED
        recipient.nv_counter = 0
        battle._add_text(recipient.nickname + ' is paralyzed! It may be unable to move!')

def _poison(recipient: pk.Pokemon, battle: bt.Battle, forced: bool = False):
    if recipient.substitute:
        if forced:
            _failed(battle)
        return
    if forced and recipient.nv_status == POISONED:
        battle._add_text(recipient.nickname + ' is already poisoned!')
    elif not recipient.nv_status:
        recipient.nv_status = POISONED
        recipient.nv_counter = 0
        battle._add_text(recipient.nickname + ' was poisoned!')

def _sleep(recipient: pk.Pokemon, battle: bt.Battle, forced: bool = False):
    if recipient.substitute:
        if forced:
            _failed(battle)
        return
    if forced and recipient.nv_status == ASLEEP:
        battle._add_text(recipient.nickname + ' is already asleep!')
    elif not recipient.nv_status:
        recipient.nv_status = ASLEEP
        recipient.nv_counter = random.randrange(2, 6)
        battle._add_text(recipient.nickname + ' fell asleep!')
    
def _badly_poison(recipient: pk.Pokemon, battle: bt.Battle, forced: bool = False):
    if recipient.substitute:
        if forced:
            _failed(battle)
        return
    if forced and recipient.nv_status == BADLY_POISONED:
        battle._add_text(recipient.nickname + ' is already badly poisoned!')
    elif not recipient.nv_status:
        recipient.nv_status = BADLY_POISONED
        recipient,nv_counter = 1
        battle._add_text(recipient.nickname + ' was badly poisoned!')

def _protect_check(defender: pokemon.Pokemon, battle: bt.Battle, move_data: Move):
    if defender.is_alive and defender.protect and move_data.target in PROTECT_TARGETS:
        battle._add_text(defender.nickname + ' protected itself!')
        return True

def _get_trainer(poke: pk.Pokemon, battle: bt.Battle) -> tr.Trainer:
    if battle.t1.current_poke == poke:
        return battle.t1
    else:
        return battle.t2

def _cap_move_name(move_name: str) -> str:
    move_name = move_name.replace('-', ' ')
    words = move_name.split()
    words = [word.capitalize() for word in words]
    return ' '.join(words)

def _failed(battle: bt.Battle):
    battle._add_text('But, it failed!')

def _missed(attacker: pk.Pokemon, battle: bt.Battle):
    battle._add_text(attacker.nickname + '\'s attack missed!')

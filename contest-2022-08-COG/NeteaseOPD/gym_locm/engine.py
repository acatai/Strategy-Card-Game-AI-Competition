import sys
import copy
import time

import numpy as np

from typing import List, Optional, Tuple
from enum import Enum, IntEnum

from gym.utils import seeding

from gym_locm.exceptions import *
from gym_locm.card import *
from gym_locm.util import has_enough_mana


CARDS_IN_DECK = 30
CARDS_IN_CONSTRUCTED = 120
CONSTRUCTED_MAX_COPY = 2
EMPTY_DECK_DAMAGE = 10
PLAYER_TURNLIMIT = 50

CARD_TYPES_DICT = {0: Creature, 1: GreenItem, 2: RedItem, 3: BlueItem}


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class Phase(IntEnum):
    DRAFT = 0
    BATTLE = 1
    ENDED = 2


class PlayerOrder(IntEnum):
    FIRST = 0
    SECOND = 1

    def opposing(self):
        return PlayerOrder((self + 1) % 2)


class Lane(IntEnum):
    LEFT = 0
    RIGHT = 1


class ActionType(Enum):
    PICK = 0
    SUMMON = 1
    ATTACK = 2
    USE = 3
    PASS = 4


class Location(IntEnum):
    PLAYER_HAND = 0
    ENEMY_HAND = 1

    PLAYER_BOARD = 10
    PLAYER_LEFT_LANE = 10
    PLAYER_RIGHT_LANE = 11

    ENEMY_BOARD = 20
    ENEMY_LEFT_LANE = 20
    ENEMY_RIGHT_LANE = 21


class Player:
    def __init__(self, player_id, k=CARDS_IN_CONSTRUCTED):
        self.id = player_id

        self.health = 30
        self.base_mana = 0
        self.bonus_mana = 0
        self.mana = 0
        self.bonus_draw = 0

        self.health_lost_this_turn = 0

        self.last_drawn = 0

        # Count chosen card copy in constructed phase, e.g. [0,1,1,2,0,0,...]
        if k:
            self.chosen_counter = [0] * k
        else:
            self.chosen_counter = None

        self.deck = []
        self.hand = []
        self.lanes = ([], [])

        self.actions = []

    def draw(self, amount: int = 1):
        for i in range(amount):
            if len(self.deck) == 0:
                raise EmptyDeckError(amount - i)

            if len(self.hand) >= 8:
                raise FullHandError()

            self.hand.append(self.deck.pop())

    def damage(self, amount: int) -> int:
        self.health -= amount

        if amount <= 0:
            return amount
        self.health_lost_this_turn += amount

        return amount

    def damage_player_with_empty_deck(self) -> None:
        self.health -= EMPTY_DECK_DAMAGE

    def clone(self):
        cloned_player = Player.empty_copy()

        cloned_player.id = self.id
        cloned_player.health = self.health
        cloned_player.base_mana = self.base_mana
        cloned_player.bonus_mana = self.bonus_mana
        cloned_player.mana = self.mana
        cloned_player.bonus_draw = self.bonus_draw

        cloned_player.health_lost_this_turn = self.health_lost_this_turn

        cloned_player.deck = [card.make_copy(card.instance_id)
                              for card in self.deck]
        cloned_player.chosen_counter = copy.deepcopy(self.chosen_counter)
        cloned_player.hand = [card.make_copy(card.instance_id)
                              for card in self.hand]
        cloned_player.lanes = tuple([[card.make_copy(card.instance_id)
                                      for card in lane]
                                     for lane in self.lanes])

        cloned_player.actions = list(self.actions)

        return cloned_player

    def otk_clone(self, is_cur=True):
        cloned_player = Player.empty_copy()

        cloned_player.id = self.id
        cloned_player.health = self.health
        cloned_player.base_mana = self.base_mana
        cloned_player.bonus_mana = self.bonus_mana
        cloned_player.mana = self.mana
        cloned_player.bonus_draw = self.bonus_draw

        cloned_player.health_lost_this_turn = self.health_lost_this_turn

        cloned_player.deck = self.deck  # [None] * len(self.deck)  # 保证不会碰deck，只取长度

        if is_cur:
            cloned_player.hand = [card.make_copy(card.instance_id)
                                  for card in self.hand]
        else:
            cloned_player.hand = self.hand  # 保证不会碰，只取长度

        cloned_player.lanes = tuple([card.make_copy(card.instance_id)
                                    for card in lane]
                                    for lane in self.lanes)

        cloned_player.actions = []

        return cloned_player

    @staticmethod
    def empty_copy():

        new_copy = EmptyPlayer()
        new_copy.__class__ = Player

        return new_copy


class Action:
    def __init__(self, action_type, origin=None, target=None):
        self.type = action_type
        self.origin = origin
        self.target = target

    def __eq__(self, other):
        return other is not None and \
               self.type == other.type and \
               self.origin == other.origin and \
               self.target == other.target

    def __repr__(self):
        return f"{self.type} {self.origin} {self.target}"

    def to_native(self):
        if self.type == ActionType.PASS:
            return "PASS"
        elif self.type == ActionType.SUMMON:
            return f"SUMMON {self.origin} {int(self.target)}"
        elif self.type == ActionType.ATTACK:
            target = self.target if self.target is not None else -1
            return f"ATTACK {self.origin} {target}"
        elif self.type == ActionType.USE:
            target = self.target if self.target is not None else -1
            return f"USE {self.origin} {target}"
        elif self.type == ActionType.PICK:
            return f"CHOOSE {self.origin}"

        else:
            raise ActionError("unknow action: " + f"{self.type} {self.origin} {self.target}")


class ActionResult:
    def __init__(
        self,
        attacking_player_health_change: int,
        defending_player_health_change: int,
        card_draw: int,
    ) -> None:
        self.attacking_player_health_change = attacking_player_health_change
        self.defending_player_health_change = defending_player_health_change
        self.card_draw = card_draw

class SummonResult(ActionResult):
    def __init__(self: int, attacking_player_health_change: int, defending_player_health_change: int, card_draw: int, summoned_creatures) -> None:
        super().__init__(attacking_player_health_change, defending_player_health_change, card_draw)
        self.summoned_creatures = summoned_creatures

class UseResult(ActionResult):
    def __init__(self, attacking_player_health_change: int, defending_player_health_change: int, card_draw: int, item, targets=[]) -> None:
        super().__init__(attacking_player_health_change, defending_player_health_change, card_draw)
        self.item = item
        self.targets = targets

class AttackResult(ActionResult):
    def __init__(self, attacking_player_health_change: int, defending_player_health_change: int, card_draw: int, attacker) -> None:
        super().__init__(attacking_player_health_change, defending_player_health_change, card_draw)
        self.attacker = attacker


class State:
    def __init__(self, seed=None, items=True, k=CARDS_IN_CONSTRUCTED, n=CARDS_IN_DECK, skip_draft=False,
        empty_phase: Optional[Phase] = None, check: bool = True):
        """
        skip_draft: skip cards generation
        empty_phase: init an empty state with phase
        check: check action
        """
        # assert k <= len(_cards)

        self.instance_counter = 0
        # self.summon_counter = 0

        self.items = items
        self.k, self.n = k, n
        self.check = check

        self.phase = empty_phase if empty_phase is not None else Phase.DRAFT
        self.turn = 1
        self.was_last_action_invalid = False
        _k = k if self.phase == Phase.DRAFT else None
        self.players = (Player(PlayerOrder.FIRST, k=_k), Player(PlayerOrder.SECOND, k=_k))
        self._current_player = PlayerOrder.FIRST
        self.__available_actions = None
        self.__available_attack_opp = None
        self.__action_mask = None

        self.winner = None

        if True:
            self.np_random = None
            self._draft_cards = None

    @property
    def current_player(self) -> Player:
        return self.players[self._current_player]

    @property
    def opposing_player(self) -> Player:
        return self.players[(int(self._current_player) + 1) % 2]

    @property
    def available_attack_opp(self) -> Tuple[List[Action], int]:
        if self.__available_attack_opp is not None:
            return self.__available_attack_opp

        attack_opp = []
        attack_opp_damage = 0
        if self.phase == Phase.BATTLE:

            c_lanes = self.current_player.lanes
            o_lanes = self.opposing_player.lanes

            for lane in Lane:
                opp_has_guard = False

                for enemy_creature in o_lanes[lane]:
                    if enemy_creature.has_ability('G'):
                        opp_has_guard = True
                        break

                if not opp_has_guard:
                    for friendly_creature in filter(Creature.able_to_attack,
                                                    c_lanes[lane]):
                        origin = friendly_creature.instance_id

                        attack_opp.append(Action(ActionType.ATTACK, origin, None))
                        attack_opp_damage += friendly_creature.attack

        self.__available_attack_opp = (attack_opp, attack_opp_damage)

        return self.__available_attack_opp

    @property
    def available_actions(self) -> Tuple[Action]:
        if self.__available_actions is not None:
            return self.__available_actions

        if self.phase == Phase.DRAFT:
            available_actions = []
            for i, card_copy_count in enumerate(self.current_player.chosen_counter):
                if card_copy_count < CONSTRUCTED_MAX_COPY:
                    available_actions.append(Action(ActionType.PICK, i))

            self.__available_actions = tuple(available_actions)

        elif self.phase == Phase.ENDED:
            self.__available_actions = ()
        else:
            summon, attack, use = [], [], []

            c_hand = self.current_player.hand
            c_lanes = self.current_player.lanes
            o_lanes = self.opposing_player.lanes

            for card in filter(has_enough_mana(self.current_player.mana), c_hand):
                origin = card.instance_id

                if isinstance(card, Creature):
                    for lane in Lane:
                        if len(c_lanes[lane]) < 3:
                            summon.append(Action(ActionType.SUMMON, origin, lane))

                elif isinstance(card, GreenItem):
                    for lane in Lane:
                        for friendly_creature in c_lanes[lane]:
                            target = friendly_creature.instance_id

                            use.append(Action(ActionType.USE, origin, target))

                elif isinstance(card, RedItem):
                    for lane in Lane:
                        for enemy_creature in o_lanes[lane]:
                            target = enemy_creature.instance_id

                            use.append(Action(ActionType.USE, origin, target))

                elif isinstance(card, BlueItem):
                    for lane in Lane:
                        for enemy_creature in o_lanes[lane]:
                            target = enemy_creature.instance_id

                            use.append(Action(ActionType.USE, origin, target))

                    use.append(Action(ActionType.USE, origin, None))

            for lane in Lane:
                guard_creatures = []

                for enemy_creature in o_lanes[lane]:
                    if enemy_creature.has_ability('G'):
                        guard_creatures.append(enemy_creature)

                if not guard_creatures:
                    valid_targets = o_lanes[lane] + [None]
                else:
                    valid_targets = guard_creatures

                for friendly_creature in filter(Creature.able_to_attack,
                                                c_lanes[lane]):
                    origin = friendly_creature.instance_id

                    for valid_target in valid_targets:
                        if valid_target is not None:
                            valid_target = valid_target.instance_id

                        attack.append(Action(ActionType.ATTACK, origin, valid_target))

            available_actions = [Action(ActionType.PASS)] + summon + use + attack

            self.__available_actions = tuple(available_actions)

        return self.__available_actions

    @property
    def action_mask(self):
        if self.__action_mask is not None:
            return self.__action_mask

        if self.phase == Phase.DRAFT:
            self.__action_mask = [
                True if card_copy_count < CONSTRUCTED_MAX_COPY else False
                for card_copy_count in self.current_player.chosen_counter
            ]
            return self.__action_mask

        elif self.phase == Phase.ENDED:
            return [False] * (145 if self.items else 41)

        action_mask = [False] * 145

        # pass is always allowed
        action_mask[0] = True

        # shortcuts
        cp, op = self.current_player, self.opposing_player
        cp_has_enough_mana = has_enough_mana(cp.mana)
        left_lane_not_full = len(cp.lanes[0]) < 3
        right_lane_not_full = len(cp.lanes[1]) < 3

        def validate_creature(index):
            if left_lane_not_full:
                action_mask[1 + index * 2] = True

            if right_lane_not_full:
                action_mask[1 + index * 2 + 1] = True

        def validate_green_item(index):
            for i in range(len(cp.lanes[0])):
                action_mask[17 + index * 13 + 1 + i] = True

            for i in range(len(cp.lanes[1])):
                action_mask[17 + index * 13 + 4 + i] = True

        def validate_red_item(index):
            for i in range(len(op.lanes[0])):
                action_mask[17 + index * 13 + 7 + i] = True

            for i in range(len(op.lanes[1])):
                action_mask[17 + index * 13 + 10 + i] = True

        def validate_blue_item(index):
            validate_red_item(index)

            action_mask[17 + index * 13] = True

        check_playability = {
            Creature: validate_creature,
            GreenItem: validate_green_item,
            RedItem: validate_red_item,
            BlueItem: validate_blue_item
        }

        """
        NOTE:
        0 PASS

        (+8*2=16)1~16 SUMMON (hand validate_creature)
        card0lane0, card0lane1, card1lane0, card1lane1, ...
        
        (+8*13=104)17~120 USE (hand validate_*_item)
        card0_opp, card0_curLane0creat0, card0_curLane0creat1, card0_curLane0creat2, card0_oppLane0creat0, ...
        
        (+3*4*2=24)121~144 ATTACK
        curLane0creat0_opp, curLane0creat0_oppLane0creat0, curLane0creat0_oppLane0creat1, curLane0creat0_oppLane0creat2, curLane0creat1_oppLane0creat0, ...
        curLane1creat0_opp, ...
        """
        # for each card in hand, check valid actions
        for i, card in enumerate(cp.hand):
            if cp_has_enough_mana(card):
                check_playability[type(card)](i)

        # for each card in the board, check valid actions
        for offset, lane_id in zip((0, 3), (0, 1)):
            for i, creature in enumerate(cp.lanes[lane_id]):
                i += offset

                if creature.able_to_attack():
                    guards = []

                    for j, enemy_creature in enumerate(op.lanes[lane_id]):
                        if enemy_creature.has_ability('G'):
                            guards.append(j)

                    if guards:
                        for j in guards:
                            action_mask[121 + i * 4 + 1 + j] = True
                    else:
                        action_mask[121 + i * 4] = True

                        for j in range(len(op.lanes[lane_id])):
                            action_mask[121 + i * 4 + 1 + j] = True

        if not self.items:
            action_mask = action_mask[:17] + action_mask[-24:]

        self.__action_mask = action_mask

        return self.__action_mask

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)

        return [seed]

    def act(self, action: Action):
        self.was_last_action_invalid = False

        if self.phase == Phase.DRAFT:
            self._act_on_draft(action)

            self._next_turn()

            if self.phase == Phase.DRAFT:  # did not finish constructions
                # self._new_draft_turn()
                pass
            elif self.phase == Phase.BATTLE:
                self._prepare_for_battle()

                self._new_battle_turn()

        elif self.phase == Phase.BATTLE:
            self._act_on_battle(action)

            if action.type == ActionType.PASS:
                self._next_turn()

                self._new_battle_turn()

        self.__available_actions = None
        self.__available_attack_opp = None
        self.__action_mask = None

    def _next_instance_id(self):
        self.instance_counter += 1

        return self.instance_counter

    def _prepare_for_battle(self):
        """Prepare all game components for a battle phase"""
        for player in self.players:
            player.hand = []
            player.lanes = ([], [])

            self.np_random.shuffle(player.deck)

        d1, d2 = [], []

        for card1, card2 in zip(*(p.deck for p in self.players)):
            d1.append(card1.make_copy(self._next_instance_id()))
            d2.append(card2.make_copy(self._next_instance_id()))

        self.players[0].deck = list(reversed(d1))
        self.players[1].deck = list(reversed(d2))

        for player in self.players:
            player.draw(4)
            player.base_mana = 0

        second_player = self.players[PlayerOrder.SECOND]
        second_player.draw()
        second_player.bonus_mana = 1

    def _next_turn(self) -> bool:
        if self.phase == Phase.DRAFT:
            if len(self.current_player.deck) < self.n:  # let one finish construction
                self.turn += 1
                return False
            else:
                if self._current_player == PlayerOrder.FIRST:
                    self._current_player = PlayerOrder.SECOND
                    self.turn = 1
                    return False
                else:
                    self._current_player = PlayerOrder.FIRST
                    self.phase = Phase.BATTLE
                    self.turn = 1
                    return True

        else:
            if self._current_player == PlayerOrder.FIRST:
                self._current_player = PlayerOrder.SECOND

                return False
            else:
                self._current_player = PlayerOrder.FIRST
                self.turn += 1

                return True

    def _new_draft_turn(self):
        """Initialize a draft turn"""
        # current_draft_choices = self._draft_cards[self.turn - 1]

        # for player in self.players:
        #     player.hand = current_draft_choices
        pass

    def _new_battle_turn(self):
        """Initialize a battle turn"""
        current_player = self.current_player

        for creature in current_player.lanes[Lane.LEFT]:
            creature.can_attack = True
            creature.has_attacked_this_turn = False

        for creature in current_player.lanes[Lane.RIGHT]:
            creature.can_attack = True
            creature.has_attacked_this_turn = False

        if current_player.base_mana > 0 and current_player.mana == 0:
            current_player.bonus_mana = 0

        if current_player.base_mana < 12:
            current_player.base_mana += 1

        current_player.mana = current_player.base_mana \
            + current_player.bonus_mana

        amount_to_draw = 1 + current_player.bonus_draw
        amount_to_draw += current_player.health_lost_this_turn // 5

        if self.turn > PLAYER_TURNLIMIT:
            current_player.damage_player_with_empty_deck()

        try:
            current_player.draw(amount_to_draw)
        except FullHandError:
            pass
        except EmptyDeckError as e:
            for _ in range(e.remaining_draws):
                current_player.damage_player_with_empty_deck()

        current_player.bonus_draw = 0
        current_player.health_lost_this_turn = 0
        current_player.last_drawn = amount_to_draw

    def _find_card_in(self, instance_id: int, cards: List[Card]) -> Card:
        for card in cards:
            if card.instance_id == instance_id:
                return card

        raise InvalidCardError(instance_id)

    def _find_card(self, instance_id: int) -> Card:
        c, o = self.current_player, self.opposing_player

        location_mapping = {
            Location.PLAYER_HAND: c.hand,
            Location.ENEMY_HAND: o.hand,
            Location.PLAYER_LEFT_LANE: c.lanes[0],
            Location.PLAYER_RIGHT_LANE: c.lanes[1],
            Location.ENEMY_LEFT_LANE: o.lanes[0],
            Location.ENEMY_RIGHT_LANE: o.lanes[1]
        }

        for location, cards in location_mapping.items():
            for card in cards:
                if card.instance_id == instance_id:
                    return card

        raise InvalidCardError(instance_id)

    def _act_on_draft(self, action: Action):
        """Execute the action intended by the player in this draft turn"""
        chosen_index = action.origin if action.origin is not None else 0
        card = self.current_player.hand[chosen_index]

        if self.current_player.chosen_counter[chosen_index] >= CONSTRUCTED_MAX_COPY:
            raise MalformedActionError("Invalid chosen index")
        self.current_player.chosen_counter[chosen_index] += 1

        self.current_player.deck.append(card)

    def _act_on_battle(self, action: Action):
        """Execute the actions intended by the player in this battle turn"""
        try:
            origin, target = action.origin, action.target

            if action.type == ActionType.PASS:
                pass
            else:
                if action.type == ActionType.SUMMON:
                    if isinstance(action.origin, int):
                        origin = self._find_card_in(
                            origin,
                            cards=self.current_player.hand,
                        )
                    if isinstance(action.target, int):
                        target = Lane(target)

                    result = self._do_summon(origin, target)
                elif action.type == ActionType.ATTACK:
                    if isinstance(action.origin, int):
                        origin = self._find_card_in(
                            origin,
                            cards=self.current_player.lanes[0]
                            + self.current_player.lanes[1],
                        )
                    if isinstance(action.target, int):
                        target = self._find_card_in(
                            target,
                            cards=self.opposing_player.lanes[0]
                            + self.opposing_player.lanes[1],
                        )

                    result = self._do_attack(origin, target)
                elif action.type == ActionType.USE:
                    if isinstance(action.origin, int):
                        origin = self._find_card_in(
                            origin,
                            cards=self.current_player.hand,
                        )
                    if isinstance(action.target, int):
                        target_player = (
                            self.current_player
                            if isinstance(origin, GreenItem)
                            else self.opposing_player
                        )
                        try:
                            target = self._find_card_in(
                                target,
                                cards=target_player.lanes[0],
                            )
                            is_left_target = True
                        except:
                            target = self._find_card_in(
                                target,
                                cards=target_player.lanes[1],
                            )
                            is_left_target = False
                    else:
                        is_left_target = None

                    result = self._do_use(origin, target, is_left_target=is_left_target)
                else:
                    raise MalformedActionError("Invalid action type")

                self.current_player.bonus_draw += result.card_draw
                self.current_player.damage(-result.attacking_player_health_change)
                self.opposing_player.damage(-result.defending_player_health_change)

            action.resolved_origin = origin
            action.resolved_target = target

            self.current_player.actions.append(action)
        except (NotEnoughManaError, MalformedActionError,
                FullLaneError, InvalidCardError):
            self.was_last_action_invalid = True

        for player in self.players:
            new_lanes = ([], [])
            for old_lane, new_lane in zip(player.lanes, new_lanes):
                for creature in old_lane:
                    if not creature.is_dead:
                        new_lane.append(creature)
            player.lanes = new_lanes

        if self.players[PlayerOrder.FIRST].health <= 0:
            self.phase = Phase.ENDED
            self.winner = PlayerOrder.SECOND
        elif self.players[PlayerOrder.SECOND].health <= 0:
            self.phase = Phase.ENDED
            self.winner = PlayerOrder.FIRST

    def _do_summon(self, origin, target) -> SummonResult:
        current_player = self.current_player
        opposing_player = self.opposing_player

        if self.check:
            if origin.cost > current_player.mana:
                raise NotEnoughManaError()

            if not isinstance(origin, Creature):
                raise MalformedActionError("Card being summoned is not a "
                                        "creature")

            if not isinstance(target, Lane):
                raise MalformedActionError("Target is not a lane")

            if len(current_player.lanes[target]) >= 3:
                raise FullLaneError()

        try:
            current_player.hand.remove(origin)
        except ValueError:
            raise MalformedActionError("Card is not in player's hand")

        current_player.mana -= origin.cost
        origin.can_attack = False
        current_player.lanes[target].append(origin)

        count_summons = 1
        creatures = None  # useless

        if origin.area == Area.LANE1 and len(current_player.lanes[target]) < 3:
            origin_copy = origin.make_copy(self._next_instance_id())
            current_player.lanes[target].append(origin_copy)
            count_summons += 1
        elif origin.area == Area.LANE2 and len(current_player.lanes[1-target]) < 3:
            origin_copy = origin.make_copy(self._next_instance_id())
            current_player.lanes[1-target].append(origin_copy)
            count_summons += 1

        return SummonResult(
            count_summons * origin.player_hp,
            count_summons * origin.enemy_hp, 
            count_summons * origin.card_draw,
            creatures
        )

    def _do_attack(self, origin, target) -> AttackResult:
        current_player = self.current_player
        opposing_player = self.opposing_player

        if self.check:
            if not isinstance(origin, Creature):
                raise MalformedActionError("Attacking card is not a "
                                        "creature")

            if origin in current_player.lanes[Lane.LEFT]:
                origin_lane = Lane.LEFT
            elif origin in current_player.lanes[Lane.RIGHT]:
                origin_lane = Lane.RIGHT
            else:
                raise MalformedActionError("Attacking creature is not "
                                        "owned by player")

            guard_creatures = []

            for creature in opposing_player.lanes[origin_lane]:
                if creature.has_ability('G'):
                    guard_creatures.append(creature)

            if len(guard_creatures) > 0:
                valid_targets = guard_creatures
            else:
                valid_targets = [None] + opposing_player.lanes[origin_lane]

            if target not in valid_targets:
                raise MalformedActionError("Invalid target")

            if not origin.able_to_attack():
                raise MalformedActionError("Attacking creature cannot "
                                        "attack")

        result = AttackResult(0, 0, 0, None)

        if target is None:
            damage_dealt = origin.attack
            result.defending_player_health_change -= damage_dealt

        elif isinstance(target, Creature):
            target_defense = target.defense

            try:
                damage_dealt = target.damage(
                    origin.attack,
                    lethal=origin.has_ability('L'))
            except WardShieldError:
                damage_dealt = 0

            try:
                origin.damage(
                    target.attack,
                    lethal=target.has_ability('L'))
            except WardShieldError:
                pass

            excess_damage = damage_dealt - target_defense

            if 'B' in origin.keywords and excess_damage > 0:
                result.defending_player_health_change -= excess_damage
        else:
            raise MalformedActionError("Target is not a creature or "
                                       "a player")

        if 'D' in origin.keywords:
            result.attacking_player_health_change += damage_dealt

        origin.has_attacked_this_turn = True

        return result

    def _do_use(self, origin, target, is_left_target=None) -> UseResult:
        current_player = self.current_player
        opposing_player = self.opposing_player

        if self.check:
            if origin.cost > current_player.mana:
                raise NotEnoughManaError()

            if target is not None and \
                    not isinstance(target, Creature):
                error = "Target is not a creature or a player"
                raise MalformedActionError(error)

            if origin not in current_player.hand:
                raise MalformedActionError("Card is not in player's hand")

            if isinstance(origin, GreenItem) or isinstance(origin, RedItem) or isinstance(origin, BlueItem):
                pass
            else:
                error = "Card being used is not an item"
                raise MalformedActionError(error)

        if target is None:
            if isinstance(origin, BlueItem):
                result = UseResult(
                    origin.player_hp,
                    origin.defense + origin.enemy_hp,
                    0, None, None)
            else:
                raise MalformedActionError("Invalid target")

        else:
            target_player = current_player if isinstance(origin, GreenItem) else opposing_player

            if not isinstance(is_left_target, bool):
                is_left_target = target in target_player.lanes[Lane.LEFT]
                is_right_target = target in target_player.lanes[Lane.RIGHT]

                if not is_left_target and not is_right_target:
                    error = "Items should be used on legal player's creatures"
                    raise MalformedActionError(error)
                elif is_left_target and is_right_target:
                    error = "Item entity in two lanes at the same time"
                    raise MalformedActionError(error)

            # area effect
            if origin.area == Area.TARGET:
                result = self.resolve_use(origin, target)

            elif origin.area == Area.LANE1 or origin.area == Area.LANE2:
                count_usages = 0

                if origin.area != Area.LANE2:
                    effect_lane = Lane.LEFT if is_left_target else Lane.RIGHT
                    potential_targets = target_player.lanes[effect_lane]
                else:
                    potential_targets = target_player.lanes[Lane.LEFT] + target_player.lanes[Lane.RIGHT]

                for potential_target in potential_targets:
                    _ = self.resolve_use(origin, potential_target)
                    count_usages += 1

                result = UseResult(
                    count_usages * origin.player_hp,
                    count_usages * origin.enemy_hp,
                    count_usages * origin.card_draw,
                    None, None)

            else:
                raise MalformedActionError("Unexpected value: {}".format(origin.area))

        current_player.hand.remove(origin)
        current_player.mana -= origin.cost

        return result

    def resolve_use(self, origin, target) -> UseResult:
        if isinstance(origin, GreenItem):

            target.attack = max(0, target.attack + origin.attack)
            target.defense += origin.defense
            target.keywords = target.keywords.union(origin.keywords)

            if target.defense <= 0:
                target.is_dead = True

        elif isinstance(origin, RedItem) or isinstance(origin, BlueItem):

            target.attack = max(0, target.attack + origin.attack)
            target.keywords = target.keywords.difference(origin.keywords)

            try:
                target.damage(-origin.defense)
            except WardShieldError:
                pass

            if target.defense <= 0:
                target.is_dead = True

        return UseResult(origin.player_hp, origin.enemy_hp, origin.card_draw, None, None)

    def clone(self) -> 'State':
        cloned_state = State.empty_copy()

        cloned_state.np_random = np.random.RandomState()
        cloned_state.np_random.set_state(self.np_random.get_state())

        cloned_state.instance_counter = self.instance_counter
        # cloned_state.summon_counter = self.summon_counter
        cloned_state.items = self.items
        cloned_state.phase = self.phase
        cloned_state.turn = self.turn
        # cloned_state.was_last_action_invalid = self.was_last_action_invalid
        cloned_state.k = self.k
        cloned_state.n = self.n
        cloned_state._current_player = self._current_player
        cloned_state.__available_actions = self.__available_actions
        cloned_state.__available_attack_opp = self.__available_attack_opp
        cloned_state.__action_mask = self.__action_mask
        cloned_state.winner = self.winner
        cloned_state._draft_cards = self._draft_cards
        cloned_state.players = tuple([player.clone() for player in self.players])

        cloned_state.check = self.check

        return cloned_state

    def otk_clone(self) -> 'State':
        cloned_state = State.empty_copy()

        cloned_state.instance_counter = self.instance_counter
        cloned_state.items = self.items
        cloned_state.phase = self.phase
        cloned_state.turn = self.turn
        cloned_state.k = self.k
        cloned_state.n = self.n
        cloned_state._current_player = self._current_player
        cloned_state.__available_actions = self.__available_actions
        cloned_state.__available_attack_opp = self.__available_attack_opp
        cloned_state.winner = self.winner
        cloned_state.players = tuple(
            player.otk_clone(
                player.id == self._current_player
            ) for player in self.players
        )

        cloned_state.check = self.check

        return cloned_state

        # return pickle.loads(pickle.dumps(self, -1))

    def __str__(self) -> str:
        encoding = ""

        p, o = self.current_player, self.opposing_player

        for cp in p, o:
            draw = cp.last_drawn if cp == self.current_player else 1 + cp.bonus_draw

            encoding += f"{cp.health} {cp.mana} " \
                f"{len(cp.deck)} {draw}\n"

        op_hand = len(o.hand) if self.phase != Phase.DRAFT else 0
        last_actions = []

        for action in reversed(o.actions[:-1]):
            if action.type == ActionType.PASS:
                break

            last_actions.append(action)

        encoding += f"{op_hand} {len(last_actions)}\n"

        for a in reversed(last_actions):
            target_id = -1 if a.target is None else a.target

            encoding += f"{a.resolved_origin.id} {a.type.name} " \
                f"{a.origin} {target_id}\n"

        # cards = p.hand + \
        #     sorted(p.lanes[0] + p.lanes[1], key=attrgetter('summon_counter')) + \
        #     sorted(o.lanes[0] + o.lanes[1], key=attrgetter('summon_counter'))
        cards = p.hand + p.lanes[0] + p.lanes[1] + o.lanes[0] + o.lanes[1]

        encoding += f"{len(cards)}\n"

        for c in cards:
            if c in p.hand:
                c.location = 0
                c.lane = -1
            elif c in p.lanes[0] + p.lanes[1]:
                c.location = 1
                c.lane = 0 if c in p.lanes[0] else 1
            elif c in o.lanes[0] + o.lanes[1]:
                c.location = -1
                c.lane = 0 if c in o.lanes[0] else 1

            if isinstance(c.type, int):
                c.cardType = c.type
            elif c.type == 'creature':
                c.cardType = 0
            elif c.type == 'itemGreen':
                c.cardType = 1
            elif c.type == 'itemRed':
                c.cardType = 2
            elif c.type == 'itemBlue':
                c.cardType = 3

            abilities = list('------')

            for i, a in enumerate(list('BCDGLW')):
                if c.has_ability(a):
                    abilities[i] = a

            c.abilities = "".join(abilities)

            c.instance_id = -1 if c.instance_id is None else c.instance_id

        for i, c in enumerate(cards):
            encoding += f"{c.id} {c.instance_id} {c.location} {c.cardType} " \
                f"{c.cost} {c.attack} {c.defense} {c.abilities} " \
                f"{c.player_hp} {c.enemy_hp} {c.card_draw} {c.lane} \n"

        return encoding

    def visualize_state(self) -> str:
        encoding = ""

        p, o = self.current_player, self.opposing_player

        for player_name, cp in zip(("cur", "opp"), (p, o)):
            draw = cp.last_drawn if cp == self.current_player else 1 + cp.bonus_draw

            encoding += f"{player_name}: hp {cp.health}, mana {cp.mana}, " \
                f"deck {len(cp.deck)}, draw {draw}\n"

        op_hand = len(o.hand) if self.phase != Phase.DRAFT else 0
        last_actions = []

        for action in reversed(o.actions[:-1]):
            if action.type == ActionType.PASS:
                break

            last_actions.append(action)

        encoding += f"opp_hand {op_hand}, last_actions {len(last_actions)}\n"

        for a in reversed(last_actions):
            target_id = -1 if a.target is None else a.target

            encoding += f"{a.resolved_origin.id} {a.type.name} " \
                f"{a.origin} {target_id}\n"


        # encoding += f"{len(cards)}\n"
        def visualize_card(c):
            debug_msg = ""

            if c in p.hand:
                c.location = 0
                c.lane = -1
            elif c in p.lanes[0] + p.lanes[1]:
                c.location = 1
                c.lane = 0 if c in p.lanes[0] else 1
                debug_msg += "able_to_attack:{}, ".format(c.able_to_attack())
            elif c in o.lanes[0] + o.lanes[1]:
                c.location = -1
                c.lane = 0 if c in o.lanes[0] else 1

            if isinstance(c.type, str):
                c.cardTypeV = c.type
            elif c.type == 0:
                c.cardTypeV = 'creature'
            elif c.type == 1:
                c.cardTypeV = 'itemGreen'
            elif c.type == 2:
                c.cardTypeV = 'itemRed'
            elif c.type == 3:
                c.cardTypeV = 'itemBlue'

            abilities = list('------')

            for i, a in enumerate(list('BCDGLW')):
                if c.has_ability(a):
                    abilities[i] = a

            c.abilities = "".join(abilities)

            c.instance_id = -1 if c.instance_id is None else c.instance_id

            if debug_msg:
                debug_msg = "  / " + debug_msg
            c.debug_msg = debug_msg

            return f"card_id {c.id}, ins_id {c.instance_id}, {c.cardTypeV}, " \
                f"cost {c.cost}, atk {c.attack}, def {c.defense}, {c.abilities}, " \
                f"player_hp {c.player_hp}, enemy_hp {c.enemy_hp}, card_draw {c.card_draw}" \
                f" {c.debug_msg} \n"

        cards = {
            "\n* hand": p.hand, 
            "\n* lane_0\n  [cur]": p.lanes[0], 
            "  [opp] ": o.lanes[0],
            "\n* lane_1\n  [cur]": p.lanes[1],
            "  [opp]  ": o.lanes[1],
        }

        for key in cards:
            _cards = cards[key]
            encoding += f"{key}\n"
            for c in _cards:
                encoding += "  " + visualize_card(c)

        return encoding

    def can_play(self, card):
        p, op = self.current_player, self.opposing_player

        if card.cost > p.mana:
            return False

        if isinstance(card, Creature):
            return sum(map(len, p.lanes)) < 6
        elif isinstance(card, GreenItem):
            return sum(map(len, p.lanes)) > 0
        elif isinstance(card, RedItem):
            return sum(map(len, op.lanes)) > 0
        else:
            return True

    def is_draft(self):
        return self.phase == Phase.DRAFT

    def is_battle(self):
        return self.phase == Phase.BATTLE

    def is_ended(self):
        return self.phase == Phase.ENDED

    @staticmethod
    def empty_copy():

        new_copy = EmptyState()
        new_copy.__class__ = State

        return new_copy

    @staticmethod
    def from_native_input(
        game_input,
        phase,
        playing_first=True,
        last_state=None,
        turn=None,
    ):
        state = State(empty_phase=phase, check=False)

        game_input = iter(game_input)

        last_biggest_instance_id = 0  # for referee's Card lastID

        # ----------------------------------------------------------------
        # set player
        if playing_first:
            state._current_player = PlayerOrder.FIRST
        else:
            state._current_player = PlayerOrder.SECOND
        current_player = state.current_player
        opposing_player = state.opposing_player

        # ----------------------------------------------------------------
        # player states
        for i, player in enumerate((current_player, opposing_player)):
            health, mana, deck, draw = map(int, next(game_input).split())

            player.health = health
            player.mana = mana
            player.base_mana = mana
            player.bonus_draw = 0 if i == 0 else draw - 1
            # player.last_drawn

            player.hand = []
            # player.deck = [Card.mockup_card() for _ in range(deck)]  # TODO: 记牌
            player.deck = [None] * deck

        # state.phase = Phase.DRAFT if mana == 0 else Phase.BATTLE

        opp_hand_count, opp_last_actions_count = map(int, next(game_input).split())

        # opposing_player.hand = [Card.mockup_card() for _ in range(opp_hand_count)]
        opposing_player.hand = [None] * opp_hand_count

        opp_last_actions = []
        for _ in range(opp_last_actions_count):
            card_id, action_type_str, origin, target = next(game_input).split()
            if action_type_str == "PASS":
                break
            origin = int(origin)
            target = None if target == "-1" else int(target)
            opp_last_action = Action(ActionType[action_type_str], origin, target)
            opp_last_actions.append(opp_last_action)
            last_biggest_instance_id = max(last_biggest_instance_id, origin)

        opp_last_actions.append(Action(ActionType.PASS))
        # eprint("** opp_last_actions: {}".format(opp_last_actions))
        opposing_player.actions.extend(opp_last_actions)

        # ----------------------------------------------------------------
        # cards
        card_count = int(next(game_input))

        for _ in range(card_count):
            card_id, instance_id, location, card_type, \
            cost, attack, defense, keywords, player_hp, \
            opp_hp, card_draw, area, lane = next(game_input).split()

            instance_id = int(instance_id)

            card_type = int(card_type)

            card_class = CARD_TYPES_DICT[card_type]

            card = card_class(card_id, card_type, cost,
                              attack, defense, keywords,
                              player_hp, opp_hp, card_draw,
                              int(area),
                              instance_id=instance_id)

            location = int(location)
            lane = int(lane)

            if location == 0:
                current_player.hand.append(card)
            elif location == 1:  # player's lane
                # set Creature.can_attack as State._new_battle_turn
                card.can_attack = True
                card.has_attacked_this_turn = False
                current_player.lanes[lane].append(card)
                last_biggest_instance_id = max(last_biggest_instance_id, instance_id)

            elif location == -1:
                opposing_player.lanes[lane].append(card)
                last_biggest_instance_id = max(last_biggest_instance_id, instance_id)

        # ----------------------------------------------------------------
        # parse referee Card lastID
        last_instance_counter = state.n * 2  # battle phase init

        if last_state is not None:
            last_instance_counter = max(last_instance_counter, last_state.instance_counter)

        # update lastID
        #   1. SUMMON instance with Area.Lane* 
        #   2. SUMMON instance with Area.Lane* and Charge, then ATTACK to die
        last_instance_counter = max(last_instance_counter, last_biggest_instance_id)
        # eprint("** cur_instance_counter: {}".format(last_instance_counter))

        state.instance_counter = last_instance_counter

        if turn is not None:
            state.turn = turn

        return state


class EmptyState(State):
    def __init__(self):
        pass


class EmptyPlayer(Player):
    def __init__(self):
        pass


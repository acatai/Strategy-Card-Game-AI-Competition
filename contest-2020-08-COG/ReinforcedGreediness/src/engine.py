import sys
from collections import defaultdict
from operator import attrgetter

from typing import Tuple
from enum import Enum, IntEnum

from src.exceptions import *
from src.helpers import has_enough_mana


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
    PICK = "PICK"
    SUMMON = "SUMMON"
    ATTACK = "ATTACK"
    USE = "USE"
    PASS = "PASS"


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
    def __init__(self, player_id):
        self.id = player_id

        self.health = 30
        self.base_mana = 0
        self.bonus_mana = 0
        self.mana = 0
        self.next_rune = 25
        self.bonus_draw = 0

        self.last_drawn = 0

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

    def damage(self, amount: int):
        self.health -= amount

        runes_lost = 0

        while self.health <= self.next_rune and self.next_rune > 0:
            self.next_rune -= 5
            self.bonus_draw += 1

            runes_lost += 1

        return amount, runes_lost

    def clone(self):
        cloned_player = Player.empty_copy()

        cloned_player.id = self.id
        cloned_player.health = self.health
        cloned_player.base_mana = self.base_mana
        cloned_player.bonus_mana = self.bonus_mana
        cloned_player.mana = self.mana
        cloned_player.next_rune = self.next_rune
        cloned_player.bonus_draw = self.bonus_draw

        cloned_player.last_drawn = self.last_drawn

        cloned_player.deck = [card.make_copy(card.instance_id)
                              for card in self.deck]
        cloned_player.hand = [card.make_copy(card.instance_id)
                              for card in self.hand]
        cloned_player.lanes = tuple([[card.make_copy(card.instance_id)
                                      for card in lane]
                                     for lane in self.lanes])

        cloned_player.actions = list(self.actions)

        return cloned_player

    @staticmethod
    def empty_copy():
        class Empty(Player):
            def __init__(self):
                pass

        new_copy = Empty()
        new_copy.__class__ = Player

        return new_copy


class Card:
    def __init__(self, card_id, name, card_type, cost, attack, defense, keywords,
                 player_hp, enemy_hp, card_draw, text, instance_id=None):
        self.id = card_id
        self.instance_id = instance_id
        self.name = name
        self.type = card_type
        self.cost = cost
        self.attack = attack
        self.defense = defense
        self.keywords = set(list(keywords.replace("-", "")))
        self.player_hp = player_hp
        self.enemy_hp = enemy_hp
        self.card_draw = card_draw
        self.text = text

    def has_ability(self, keyword: str) -> bool:
        return keyword in self.keywords

    def make_copy(self, instance_id=None) -> 'Card':
        cloned_card = Card.empty_copy(self)

        cloned_card.id = self.id
        cloned_card.name = self.name
        cloned_card.type = self.type
        cloned_card.cost = self.cost
        cloned_card.attack = self.attack
        cloned_card.defense = self.defense
        cloned_card.keywords = set(self.keywords)
        cloned_card.player_hp = self.player_hp
        cloned_card.enemy_hp = self.enemy_hp
        cloned_card.card_draw = self.card_draw
        cloned_card.text = self.text

        if instance_id is not None:
            cloned_card.instance_id = instance_id
        else:
            cloned_card.instance_id = None

        return cloned_card

    def __eq__(self, other):
        return other is not None \
               and self.instance_id is not None \
               and other.instance_id is not None \
               and self.instance_id == other.instance_id

    def __repr__(self):
        if self.name:
            return f"({self.instance_id}: {self.name})"
        else:
            return f"({self.instance_id})"

    @staticmethod
    def empty_copy(card):
        class Empty(Card):
            def __init__(self):
                pass

        new_copy = Empty()
        new_copy.__class__ = type(card)

        return new_copy


class Creature(Card):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.is_dead = False
        self.can_attack = False
        self.has_attacked_this_turn = False
        self.summon_counter = None

    def remove_ability(self, ability: str):
        self.keywords.discard(ability)

    def add_ability(self, ability: str):
        self.keywords.add(ability)

    def able_to_attack(self) -> bool:
        return not self.has_attacked_this_turn and \
               (self.can_attack or self.has_ability('C'))

    def damage(self, amount: int = 1, lethal: bool = False) -> int:
        if amount <= 0:
            return 0

        if self.has_ability('W'):
            self.remove_ability('W')

            raise WardShieldError()

        self.defense -= amount

        if lethal or self.defense <= 0:
            self.is_dead = True

        return amount

    def make_copy(self, instance_id=None) -> 'Card':
        cloned_card = super().make_copy(instance_id)

        cloned_card.summon_counter = self.summon_counter
        cloned_card.is_dead = self.is_dead
        cloned_card.can_attack = self.can_attack
        cloned_card.has_attacked_this_turn = self.has_attacked_this_turn

        return cloned_card


class Item(Card):
    pass


class GreenItem(Item):
    pass


class RedItem(Item):
    pass


class BlueItem(Item):
    pass


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

    def __hash__(self):
        return hash((ord(self.type.value[0]), ord(self.type.value[1]),
                     self.origin, self.target))

    def to_native(self):
        if self.type == ActionType.PASS:
            return "PASS"
        elif self.type == ActionType.SUMMON:
            return f"SUMMON {self.origin} {int(self.target)}"
        else:
            target = self.target if self.target is not None else -1
            return f"{self.type.value} {self.origin} {target}"


class State:
    def __init__(self):
        self.instance_counter = 0
        self.summon_counter = 0

        self.phase = Phase.BATTLE
        self.turn = 1
        self.was_last_action_invalid = False
        self.players = (Player(PlayerOrder.FIRST), Player(PlayerOrder.SECOND))
        self._current_player = PlayerOrder.FIRST
        self.__available_actions = None

        self.history = []

        self.winner = None

    @property
    def current_player(self) -> Player:
        return self.players[self._current_player]

    @property
    def opposing_player(self) -> Player:
        return self.players[(int(self._current_player) + 1) % 2]

    @property
    def available_actions(self) -> Tuple[Action]:
        if self.__available_actions is not None:
            return self.__available_actions

        if self.phase == Phase.ENDED:
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

            available_actions = summon + attack + use

            self.__available_actions = tuple(available_actions)

        return self.__available_actions

    def act(self, action: Action):
        self.was_last_action_invalid = False

        if action.type == ActionType.PASS:
            self._next_turn()

            self._new_battle_turn()
        else:
            self._act_on_battle(action)

        self.__available_actions = None

    def undo(self):
        changes = self.history.pop()

        try:
            for target, damage in changes["damage_dealt"]:
                if isinstance(target, Player):
                    target.health += damage
                elif isinstance(target, Creature):
                    target.defense += damage
        except ValueError:
            pass

        try:
            for target, hand, lane in changes["placed"]:
                lane.remove(target)
                hand.append(target)

                target.summon_counter = None
                self.summon_counter -= 1
        except ValueError:
            pass

        try:
            for target, mana in changes["mana_spent"]:
                target.mana += mana
        except ValueError:
            pass

        try:
            for target, bonus_draw in changes["bonus_draw"]:
                target.bonus_draw -= bonus_draw
        except ValueError:
            pass

        try:
            for target, stat, change in changes["stat_change"]:
                if stat == "attack":
                    target.attack -= change
                elif stat == "defense":
                    target.defense -= change
                elif stat == "ability+":
                    target.keywords = target.keywords.difference(change)
                elif stat == "ability-":
                    target.keywords = target.keywords.union(change)
        except ValueError:
            pass

        try:
            for card, origin in changes["destroyed"]:
                origin.append(card)

                if isinstance(card, Creature):
                    card.is_dead = False
        except ValueError:
            pass

        try:
            for player, runes_lost in changes["runes_lost"]:
                player.next_rune += 5 * runes_lost
                player.bonus_draw -= 1 * runes_lost
        except ValueError:
            pass

        try:
            for creature in changes["attacked"]:
                creature.has_attacked_this_turn = False
        except ValueError:
            pass

    def undo_all(self):
        while self.history:
            self.undo()

    def _next_instance_id(self):
        self.instance_counter += 1

        return self.instance_counter

    def _next_turn(self) -> bool:
        if self._current_player == PlayerOrder.FIRST:
            self._current_player = PlayerOrder.SECOND

            return False
        else:
            self._current_player = PlayerOrder.FIRST
            self.turn += 1

            return True

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

        if self.turn > 50:
            current_player.deck = []

        try:
            current_player.draw(amount_to_draw)
        except FullHandError:
            pass
        except EmptyDeckError as e:
            for _ in range(e.remaining_draws):
                deck_burn = current_player.health - current_player.next_rune
                current_player.damage(deck_burn)

        current_player.bonus_draw = 0
        current_player.last_drawn = amount_to_draw

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

        self.current_player.deck.append(card)

    def _act_on_battle(self, action: Action):
        """Execute the actions intended by the player in this battle turn"""
        try:
            origin, target = action.origin, action.target

            if isinstance(action.origin, int):
                origin = self._find_card(origin)

            if action.type == ActionType.SUMMON:
                if isinstance(action.target, int):
                    target = Lane(target)

                changes = self._do_summon(origin, target)
            elif action.type == ActionType.ATTACK:
                if isinstance(action.target, int):
                    target = self._find_card(target)

                changes = self._do_attack(origin, target)
            elif action.type == ActionType.USE:
                if isinstance(action.target, int):
                    target = self._find_card(target)

                changes = self._do_use(origin, target)
            else:
                raise MalformedActionError("Invalid action type")

            action.resolved_origin = origin
            action.resolved_target = target

            self.current_player.actions.append(action)
        except (NotEnoughManaError, MalformedActionError,
                FullLaneError, InvalidCardError):
            self.was_last_action_invalid = True

            return

        for player in self.players:
            for lane in player.lanes:
                for creature in lane:
                    if creature.is_dead:
                        lane.remove(creature)

                        changes["destroyed"].append((creature, lane))

        if self.players[PlayerOrder.FIRST].health <= 0:
            self.phase = Phase.ENDED
            self.winner = PlayerOrder.SECOND
        elif self.players[PlayerOrder.SECOND].health <= 0:
            self.phase = Phase.ENDED
            self.winner = PlayerOrder.FIRST

        self.history.append(changes)

    def _do_summon(self, origin, target):
        changes = defaultdict(list)

        current_player = self.current_player
        opposing_player = self.opposing_player

        current_player.hand.remove(origin)

        origin.can_attack = False
        origin.summon_counter = self.summon_counter

        self.summon_counter += 1

        current_player.lanes[target].append(origin)
        changes["placed"].append((origin, current_player.hand, current_player.lanes[target]))

        current_player.bonus_draw += origin.card_draw
        changes["bonus_draw"].append((current_player, origin.card_draw))

        damage_received, runes_lost = current_player.damage(-origin.player_hp)
        changes["damage_dealt"].append((current_player, -origin.player_hp))
        changes["runes_lost"].append((current_player, runes_lost))

        damage_dealt, runes_lost = opposing_player.damage(-origin.enemy_hp)
        changes["damage_dealt"].append((opposing_player, -origin.enemy_hp))
        changes["runes_lost"].append((opposing_player, runes_lost))

        current_player.mana -= origin.cost
        changes["mana_spent"].append((current_player, origin.cost))

        return changes

    def _do_attack(self, origin, target):
        changes = defaultdict(list)

        current_player = self.current_player
        opposing_player = self.opposing_player

        if target is None:
            damage_dealt, runes_lost = opposing_player.damage(origin.attack)

            changes["damage_dealt"].append((opposing_player, damage_dealt))
            changes["runes_lost"].append((opposing_player, runes_lost))

        elif isinstance(target, Creature):
            target_defense = target.defense

            try:
                damage_dealt = target.damage(
                    origin.attack,
                    lethal=origin.has_ability('L'))

                changes["damage_dealt"].append((target, damage_dealt))
            except WardShieldError:
                damage_dealt = 0

                changes["stat_change"].append((target, "ability-", {'W'}))

            try:
                damage_received = origin.damage(
                    target.attack,
                    lethal=target.has_ability('L'))

                changes["damage_dealt"].append((origin, damage_received))
            except WardShieldError:
                changes["stat_change"].append((origin, "ability-", {'W'}))

            excess_damage = damage_dealt - target_defense

            if 'B' in origin.keywords and excess_damage > 0:
                _, runes_lost = opposing_player.damage(excess_damage)

                changes["damage_dealt"].append((opposing_player, excess_damage))
                changes["runes_lost"].append((opposing_player, runes_lost))
        else:
            raise MalformedActionError("Target is not a creature or "
                                       "a player")

        if 'D' in origin.keywords:
            current_player.health += damage_dealt

            changes["damage_dealt"].append((current_player, -damage_dealt))

        origin.has_attacked_this_turn = True
        changes["attacked"].append(origin)

        return changes

    def _do_use(self, origin, target):
        changes = defaultdict(list)

        current_player = self.current_player
        opposing_player = self.opposing_player

        current_player.hand.remove(origin)
        changes["destroyed"].append((origin, current_player.hand))

        if isinstance(origin, GreenItem):
            new_attack = max(0, target.attack + origin.attack)
            keyword_gain = origin.keywords.difference(target.keywords)

            changes["stat_change"].append((target, "attack", new_attack - target.attack))
            changes["stat_change"].append((target, "defense", origin.defense))
            changes["stat_change"].append((target, "ability+", keyword_gain))

            target.attack = new_attack
            target.defense += origin.defense
            target.keywords = target.keywords.union(origin.keywords)

            if target.defense <= 0:
                target.is_dead = True

            current_player.bonus_draw += origin.card_draw
            changes["bonus_draw"].append((current_player, origin.card_draw))

            _, runes_lost = current_player.damage(-origin.player_hp)
            changes["damage_dealt"].append((current_player, -origin.player_hp))
            changes["runes_lost"].append((current_player, runes_lost))

            _, runes_lost = opposing_player.damage(-origin.enemy_hp)
            changes["damage_dealt"].append((opposing_player, -origin.enemy_hp))
            changes["runes_lost"].append((opposing_player, runes_lost))

        elif isinstance(origin, RedItem):
            new_attack = max(0, target.attack + origin.attack)
            keyword_loss = origin.keywords.intersection(target.keywords)

            changes["stat_change"].append((target, "attack", new_attack - target.attack))
            changes["stat_change"].append((target, "ability-", keyword_loss))

            target.attack = new_attack
            target.keywords = target.keywords.difference(origin.keywords)

            try:
                damage_dealt = target.damage(-origin.defense)

                changes["damage_dealt"].append((target, damage_dealt))
            except WardShieldError:
                changes["stat_change"].append((target, "ability-", {'W'}))

            if target.defense <= 0:
                target.is_dead = True

            current_player.bonus_draw += origin.card_draw
            changes["bonus_draw"].append((current_player, origin.card_draw))

            _, runes_lost = current_player.damage(-origin.player_hp)
            changes["damage_dealt"].append((current_player, -origin.player_hp))
            changes["runes_lost"].append((current_player, runes_lost))

            _, runes_lost = opposing_player.damage(-origin.enemy_hp)
            changes["damage_dealt"].append((opposing_player, -origin.enemy_hp))
            changes["runes_lost"].append((opposing_player, runes_lost))

        elif isinstance(origin, BlueItem):
            if isinstance(target, Creature):
                new_attack = max(0, target.attack + origin.attack)
                keyword_loss = origin.keywords.intersection(target.keywords)

                changes["stat_change"].append((target, "attack", new_attack - target.attack))
                changes["stat_change"].append((target, "ability-", keyword_loss))

                target.attack = new_attack
                target.keywords = target.keywords.difference(origin.keywords)

                try:
                    damage_dealt = target.damage(-origin.defense)

                    changes["damage_dealt"].append((target, damage_dealt))
                except WardShieldError:
                    changes["stat_change"].append((target, "ability-", {'W'}))

                if target.defense <= 0:
                    target.is_dead = True

            elif target is None:
                damage_dealt, runes_lost = opposing_player.damage(-origin.defense)

                changes["damage_dealt"].append((opposing_player, damage_dealt))
                changes["runes_lost"].append((opposing_player, runes_lost))
            else:
                raise MalformedActionError("Invalid target")

            current_player.bonus_draw += origin.card_draw
            changes["bonus_draw"].append((current_player, origin.card_draw))

            _, runes_lost = current_player.damage(-origin.player_hp)
            changes["damage_dealt"].append((current_player, -origin.player_hp))
            changes["runes_lost"].append((current_player, runes_lost))

            _, runes_lost = opposing_player.damage(-origin.enemy_hp)
            changes["damage_dealt"].append((opposing_player, -origin.enemy_hp))
            changes["runes_lost"].append((opposing_player, runes_lost))

        else:
            error = "Card being used is not an item"
            raise MalformedActionError(error)

        current_player.mana -= origin.cost
        changes["mana_spent"].append((current_player, origin.cost))

        return changes

    def clone(self) -> 'State':
        cloned_state = State.empty_copy()

        cloned_state.history = self.history
        cloned_state.instance_counter = self.instance_counter
        cloned_state.summon_counter = self.summon_counter
        cloned_state.phase = self.phase
        cloned_state.turn = self.turn
        cloned_state._current_player = self._current_player
        cloned_state.__available_actions = self.__available_actions
        cloned_state.winner = self.winner
        cloned_state.players = tuple([player.clone() for player in self.players])

        return cloned_state

        # return pickle.loads(pickle.dumps(self, -1))

    @staticmethod
    def from_native_input(str_state):
        if isinstance(str_state, str):
            str_state = str_state.split("\n")

        state = State()

        state.instance_counter = 1000

        p, o = state.current_player, state.opposing_player

        player_info = map(int, str_state[0].split())
        opp_info = map(int, str_state[1].split())

        p.health, p.mana, player_deck, p.next_rune, _ = player_info
        o.health, o.mana, opp_deck, o.next_rune, o.bonus_draw = opp_info

        o.bonus_draw -= 1

        opp_hand, opp_actions = map(int, str_state[2].split())

        def empty_card():
            iid = state.instance_counter
            state.instance_counter += 1

            return Card(-1, "", 0, 99, 0, 0, "------", 0, 0, 0, "", iid)

        p.deck = [empty_card() for _ in range(player_deck)]
        o.deck = [empty_card() for _ in range(opp_deck)]
        p.hand = []
        o.hand = [empty_card() for _ in range(opp_hand)]

        state.phase = Phase.DRAFT if p.mana == 0 else Phase.BATTLE

        cards = str_state[4 + opp_actions:]

        def int_except(value):
            try:
                return int(value)
            except ValueError:
                return value

        summon_counter = 0

        type_class_dict = {0: Creature, 1: GreenItem, 2: RedItem, 3: BlueItem}

        for card in cards:
            number, instance_id, location, card_type, cost, attack, \
                defense, abilities, player_hp, enemy_hp, card_draw, lane \
                = map(int_except, card.split())

            type_class = type_class_dict[card_type]

            card = type_class(number, "", card_type, cost, attack, defense,
                              abilities, player_hp, enemy_hp, card_draw,
                              "", instance_id)

            if isinstance(card, Creature):
                card.summon_counter = summon_counter
                summon_counter += 1
                card.can_attack = True

            if location == 0:
                p.hand.append(card)
            elif location == 1:
                card.can_attack = True
                p.lanes[lane].append(card)
            elif location == -1:
                o.lanes[lane].append(card)

        return state

    def __str__(self) -> str:
        encoding = ""

        p, o = self.current_player, self.opposing_player

        for cp in p, o:
            draw = cp.last_drawn if cp == self.current_player else 1 + cp.bonus_draw

            encoding += f"{cp.health} {cp.base_mana + cp.bonus_mana} " \
                f"{len(cp.deck)} {cp.next_rune} {draw}\n"

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

        cards = sorted(p.hand, key=attrgetter('instance_id')) + \
            sorted(p.lanes[0] + p.lanes[1], key=attrgetter('summon_counter')) + \
            sorted(o.lanes[0] + o.lanes[1], key=attrgetter('summon_counter'))

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

    def __hash__(self):
        return id(self)

    @staticmethod
    def empty_copy():
        class Empty(State):
            def __init__(self):
                pass

        new_copy = Empty()
        new_copy.__class__ = State

        return new_copy

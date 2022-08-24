import sys
from abc import ABC, abstractmethod

import gym

from gym_locm.engine import (
    Creature,
    GreenItem,
    Player,
    RedItem,
    BlueItem,
    State,
    Phase,
    ActionType,
    Action,
    Lane,
    Area,
)
from gym_locm.exceptions import MalformedActionError

from config import (
    cost_bins,
    hand_attack_bins,
    hand_defense_bins,
    board_attack_bins,
    board_defense_bins,
    card_player_hp_bins,
    card_enemy_hp_bins,
    card_draw_bins,
    player_hp_bins,
    opp_hp_bins,
    health_lost_to_next_bonus_draw_bins,
    player_mana_bins,
    player_bonus_draw_bins,
    hand_cards_num_bins,
    lane_cards_num_bins,
)


class LOCMEnv(gym.Env, ABC):
    card_types = {Creature: 0, GreenItem: 1, RedItem: 2, BlueItem: 3}

    def __init__(self, seed=None, items=True, k=120, n=30, skip_draft=False):
        self._seed = seed
        self.episodes = 0
        self.items = items
        self.k, self.n = k, n

        self.print_to_stderr = False

        self.state = State.empty_copy()  # State(seed=seed, items=items, k=k, n=n, skip_draft=skip_draft)

    def seed(self, seed=None):
        """Sets a seed for random choices in the game."""
        self._seed = seed
        self.state.seed(seed)

    def reset(self):
        """
        Resets the environment.
        The game is put into its initial state
        """
        if self._seed is None:
            # recover random state from current state obj
            random_state = self.state.np_random

            # start a brand new game
            self.state = State(items=self.items)

            # apply random state
            self.state.np_random = random_state
        else:
            # start a brand new game with next seed
            self._seed += 1

            self.state = State(seed=self._seed, items=self.items)

        self.episodes += 1

    def print(self, msg=""):
        if self.print_to_stderr:
            print(msg, file=sys.stderr, flush=True)
        else:
            print(msg)

    def decode_action(self, action_number):
        """
        Decodes an action number from either phases into the
        corresponding action object, if possible. Raises
        MalformedActionError otherwise.
        """
        try:
            if self.state.phase == Phase.DRAFT:
                return self.decode_draft_action(self.state, action_number)
            elif self.state.phase == Phase.BATTLE:
                return self.decode_battle_action(self.state, action_number)
            else:
                return None
        except MalformedActionError:
            return None

    @staticmethod
    def decode_draft_action(state, action_number):
        """
        Decodes an action number (0-2) from draft phase into the
        corresponding action object, if possible. Raises
        MalformedActionError otherwise.
        """

        if action_number < 0 or action_number >= state.k:
            raise MalformedActionError("Invalid action number")

        return Action(ActionType.PICK, action_number)

    @staticmethod
    def decode_battle_action(state, action_number):
        """
        Decodes an action number (0-144) from battle phase into
        the corresponding action object, if possible. Raises
        MalformedActionError otherwise.
        """
        player = state.current_player
        opponent = state.opposing_player

        if not state.items and action_number > 16:
            action_number += 104

        try:
            if action_number == 0:
                return Action(ActionType.PASS)
            elif 1 <= action_number <= 16:
                action_number -= 1

                origin = int(action_number / 2)
                target = Lane(action_number % 2)

                origin = player.hand[origin].instance_id

                return Action(ActionType.SUMMON, origin, target)
            elif 17 <= action_number <= 120:
                action_number -= 17

                origin = int(action_number / 13)
                target = action_number % 13

                origin = player.hand[origin].instance_id

                if target == 0:
                    target = None
                else:
                    target -= 1

                    side = [player, opponent][int(target / 6)]
                    lane = int((target % 6) / 3)
                    index = target % 3

                    target = side.lanes[lane][index].instance_id

                return Action(ActionType.USE, origin, target)
            elif 121 <= action_number <= 144:
                action_number -= 121

                origin = action_number // 4
                target = action_number % 4

                lane = origin // 3

                origin = player.lanes[lane][origin % 3].instance_id

                if target == 0:
                    target = None
                else:
                    target -= 1

                    target = opponent.lanes[lane][target].instance_id

                return Action(ActionType.ATTACK, origin, target)
            else:
                raise MalformedActionError("Invalid action number")
        except IndexError:
            raise MalformedActionError("Invalid action number")

    @staticmethod
    def encode_card(card):
        """Encodes a card object into a numerical array."""
        card_type = [1.0 if isinstance(card, card_type) else 0.0
                     for card_type in LOCMEnv.card_types]
        cost = card.cost / 12

        attack = card.attack / (12+4)
        defense = card.defense / (12+4)

        keywords = list(map(int, map(card.keywords.__contains__, 'BCDGLW')))
        player_hp = card.player_hp / 3
        enemy_hp = card.enemy_hp / 3
        card_draw = card.card_draw / 4
        area = [0] * len(Area)  # 3
        area[card.area.value] = 1

        return card_type + [cost, attack, defense, player_hp,
                            enemy_hp, card_draw] + keywords + area

    @staticmethod
    def encode_card_on_hand(card):
        """Encodes a card object into a numerical array."""
        card_type = [
            1.0 if isinstance(card, card_type) else 0.0
            for card_type in LOCMEnv.card_types
        ]  # 4
        cost = _numerical_to_one_hot(card.cost, cost_bins)
        attack = _numerical_to_one_hot(card.attack, hand_attack_bins)
        defense = _numerical_to_one_hot(card.defense, hand_defense_bins)
        keywords = list(map(int, map(card.keywords.__contains__, "BCDGLW")))  # 6
        player_hp = _numerical_to_one_hot(card.player_hp, card_player_hp_bins)
        enemy_hp = _numerical_to_one_hot(card.enemy_hp, card_enemy_hp_bins)
        card_draw = _numerical_to_one_hot(card.card_draw, card_draw_bins)
        area = [0] * len(Area)  # 3
        area[card.area.value] = 1

        return (
            card_type
            + cost
            + attack
            + defense
            + keywords
            + player_hp
            + enemy_hp
            + card_draw
            + area
        )

    @staticmethod
    def encode_friendly_card_on_board(card: Creature):
        """Encodes a card object into a numerical array."""
        attack = _numerical_to_one_hot(card.attack, board_attack_bins)
        additional_attack = [max(0.0, card.attack - board_attack_bins[-1]) / 10.0]
        defense = _numerical_to_one_hot(card.defense, board_defense_bins)
        additional_defense = [max(0.0, card.defense - board_defense_bins[-1]) / 10.0]
        keywords = list(map(int, map(card.keywords.__contains__, "BCDGLW")))  # 6

        can_attack = [int(card.can_attack), int(card.has_attacked_this_turn)]

        return attack + additional_attack + defense + additional_defense + keywords + can_attack

    @staticmethod
    def encode_enemy_card_on_board(card: Creature):
        """Encodes a card object into a numerical array."""
        attack = _numerical_to_one_hot(card.attack, board_attack_bins)
        additional_attack = [max(0.0, card.attack - board_attack_bins[-1]) / 10.0]
        defense = _numerical_to_one_hot(card.defense, board_defense_bins)
        additional_defense = [max(0.0, card.defense - board_defense_bins[-1]) / 10.0]
        keywords = list(map(int, map(card.keywords.__contains__, "BCDGLW")))  # 6

        return attack + additional_attack + defense + additional_defense + keywords

    @staticmethod
    def encode_health_lost(player: Player):

        return _numerical_to_one_hot(
            player.health_lost_this_turn % 5, health_lost_to_next_bonus_draw_bins)

    @staticmethod
    def encode_player(player: Player, is_opp: bool):
        hp_bins = opp_hp_bins if is_opp else player_hp_bins
        health = _numerical_to_one_hot(player.health, hp_bins)
        additional_health = max(0.0, player.health - hp_bins[-1])
        additional_health = [additional_health / 30.0]

        mana = _numerical_to_one_hot(player.mana, player_mana_bins)
        bonus_draw = _numerical_to_one_hot(player.bonus_draw, player_bonus_draw_bins)
        hand_cards_num = _numerical_to_one_hot(len(player.hand), hand_cards_num_bins)
        left_lane_cards_num = _numerical_to_one_hot(len(player.lanes[0]), lane_cards_num_bins)
        right_lane_cards_num = _numerical_to_one_hot(len(player.lanes[1]), lane_cards_num_bins)
        deck_cards_num = [len(player.deck) / 30.0]

        return (
            health
            + additional_health
            + mana
            + bonus_draw
            + hand_cards_num
            + left_lane_cards_num
            + right_lane_cards_num
            + deck_cards_num
        )

    def encode_state(self):
        """Encodes a state object into a numerical matrix."""
        if self.state.phase == Phase.DRAFT:
            return self._encode_state_draft()
        elif self.state.phase == Phase.BATTLE:
            return self._encode_state_battle()
        elif self.state.phase == Phase.ENDED:
            return self._encode_state_battle()

    @abstractmethod
    def _encode_state_draft(self):
        """Encodes a state object in the draft phase."""
        pass

    @abstractmethod
    def _encode_state_battle(self):
        """Encodes a state object in the battle phase."""
        pass

    @property
    def turn(self):
        return self.state.turn

    @property
    def action_mask(self):
        return self.state.action_mask

    def action_masks(self):
        """
        Method implemented especially for SB3-Contrib's MaskablePPO support.
        More at https://sb3-contrib.readthedocs.io
        """
        return self.state.action_mask

    @property
    def available_actions(self):
        return self.state.available_actions

    @property
    def _draft_is_finished(self):
        return self.state.phase > Phase.DRAFT

    @property
    def _battle_is_finished(self):
        return self.state.phase > Phase.BATTLE



def _numerical_to_category(value, boundary_list):  # TODO: 优化效率
    """
    数值型 -> 类别型

    value: 数值型数据取值
    boundary_list: 分界点列表, 左闭右开[)

    例如:
    boundary_list = [1,2] 则 (-inf, 1): 0, [1,2): 1, [2, +inf): 2
    类别数为 len(boundary_list) + 1
    """
    for i in range(len(boundary_list)):
        if value < boundary_list[i]:
            return i
    if value >= boundary_list[-1]:
        return len(boundary_list)

def _numerical_to_one_hot(value, boundary_list):
    category = _numerical_to_category(value, boundary_list)
    one_hot = [0] * (len(boundary_list) + 1)
    one_hot[category] = 1
    return one_hot

def _numerical_bounding(value, lower=0.0, upper=1.0):
    return max(lower, min(upper, value))

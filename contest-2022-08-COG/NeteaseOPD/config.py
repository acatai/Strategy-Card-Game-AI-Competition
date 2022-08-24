# coding=utf-8
from collections import OrderedDict
from typing import Tuple, List, Optional, Dict

# =============================================================================
# LoCM
# =============================================================================

max_hand = 8
max_lane = 3
num_lane = 2

attack_range = 16  # 最大mana 12 + bonus mean 1 + std 2 * x
defense_range = 16

cost_bins = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
hand_attack_bins = list(range(-attack_range, attack_range+1))  # 考虑法术牌有负数
hand_defense_bins = list(range(-defense_range, defense_range+1))
board_attack_bins = list(range(1, attack_range+4))  # 考虑场上随从被增益
board_defense_bins = list(range(2, defense_range+4))
card_player_hp_bins = [1, 2, 3]
card_enemy_hp_bins = [-2, -1, 0]
card_draw_bins = [1, 2, 3, 4]

player_hp_bins = list(range(2, 16))
opp_hp_bins = list(range(2, 21))
health_lost_to_next_bonus_draw_bins = list(range(1, 5))
player_mana_bins = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
player_bonus_draw_bins = [1, 2, 3, 4, 5, 6, 7]
hand_cards_num_bins = [1, 2, 3, 4, 5, 6, 7, 8]
lane_cards_num_bins = [1, 2, 3]


class ConstructStateEncodeDims:
    """ """

    def __init__(self, k=120, n=30, max_copy=2) -> None:
        self.card_features = 19
        self.k, self.n, self.max_copy = k, n, max_copy

        # 根据算法需要
        self.get_state_encode_shape()

    def get_state_encode_shape(self):
        self.actions_shape = self.k

        state_encode_shape = dict(
            state=(self.k, self.card_features+self.max_copy+1),
            action_mask=(self.actions_shape,),
        )
        self.state_encode_shape = OrderedDict(sorted(list(state_encode_shape.items())))


class BattleStateEncodeDims:
    """
    对应 LOCMBattleEnv._encode_state_battle 修改
    """

    def __init__(self, config: Optional[Dict] = None) -> None:
        if config is None:
            config = {}
        self.perfect_training = config.get("perfect_training", False)

        self.card_encode_dims = (
            4
            + dims(cost_bins)
            + dims(hand_attack_bins)
            + dims(hand_defense_bins)
            + 6
            + dims(card_player_hp_bins)
            + dims(card_enemy_hp_bins)
            + dims(card_draw_bins)
            + 3
        )

        self.cur_lane_card_encode_dims = dims(board_attack_bins) + 1 + dims(board_defense_bins) + 1 + 6 + 2 + 2
        self.opp_lane_card_encode_dims = dims(board_attack_bins) + 1 + dims(board_defense_bins) + 1 + 6 + 2

        self.player_encode_dims = (
            dims(opp_hp_bins)
            + 1
            + dims(player_mana_bins)
            + dims(player_bonus_draw_bins)
            + dims(hand_cards_num_bins)
            + dims(lane_cards_num_bins) * 2
            + 1
        )

        # 根据算法需要
        self.get_state_encode_shape()

    def get_state_encode_shape(self):
        self.actions_shape = 145
        state_encode_shape = dict(
            players=(2 + self.player_encode_dims * 2,),
            hand=(max_hand, self.card_encode_dims),
            # hand_mask=(max_hand,),
            cur_lane=(max_lane * 2, self.cur_lane_card_encode_dims),
            # cur_lane_mask=(max_lane * 2,),
            opp_lane=(max_lane * 2, self.opp_lane_card_encode_dims),
            # opp_lane_mask=(max_lane * 2,),
            action_mask=(self.actions_shape,),
        )
        if self.perfect_training:
            state_encode_shape.update(dict(
                opp_hand=(max_hand, self.card_encode_dims),
                # opp_hand_mask=(max_hand,),
            ))

        self.state_encode_shape = OrderedDict(sorted(list(state_encode_shape.items())))


def dims(boundary_list):
    return len(boundary_list) + 1


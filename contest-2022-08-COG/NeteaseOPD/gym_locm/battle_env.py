import sys
import gym
import time
from gym.spaces import Space, Box, Dict, Discrete
from gym import spaces, logger
from collections import OrderedDict

import numpy as np

from config import max_hand, max_lane, BattleStateEncodeDims

from gym_locm.agents import parse_draft_agent, parse_battle_agent
from gym_locm.engine import PLAYER_TURNLIMIT, Phase, Action, PlayerOrder, ActionType, State
from gym_locm.base_env import LOCMEnv

from typing import Tuple, List, Optional

logger.set_level(50)


class LOCMBattleEnv(LOCMEnv):

    def __init__(self, config, inferring=False):
        """
        inferring: 是否推理阶段
        """
        self.inferring = inferring

        seed = config.get("seed", None)  # TODO gym env seed 统一 State seed
        items = config.get("items", True)
        k = config.get("k", 120)
        n = config.get("n", 30)
        skip_draft = config.get("skip_draft", False)  # 如不需要构筑阶段可跳过以降低时间开销
        return_action_mask = config.get("return_action_mask", False)
        self.reward_shaping = config.get("reward_shaping", False)
        draft_agent_names = config.get("draft_agents", ("pass", "pass"))

        self.perfect_training = config.get("perfect_training", False)

        # TODO: agents' init args
        self.draft_agents = []

        if not skip_draft:
            for draft_agent_name in draft_agent_names:
                draft_agent = parse_draft_agent(draft_agent_name)()
                self.draft_agents.append(draft_agent)

        super().__init__(seed=seed, items=items, k=k, n=n, skip_draft=skip_draft)

        if not self.items:
            raise NotImplementedError("not items not supported")

        # self.rewards = [0.0]

        for draft_agent in self.draft_agents:
            draft_agent.reset()
            draft_agent.seed(seed)

        self.return_action_mask = return_action_mask

        # ------------------------------------------------------------------------
        # spaces

        state_encode_dims = BattleStateEncodeDims(
            config={
                "perfect_training": self.perfect_training,
            }
        )
        # print("[DEBUG]", state_encode_dims.state_encode_shape)
        self.state_encode_dims = state_encode_dims

        self.observation_space, self.action_space = self.get_game_spaces(state_encode_dims)

        # ------------------------------------------------------------------------

        # play through draft
        self.draft_time = None
        if not skip_draft:
            self.draft_time = self._do_draft()

    @staticmethod
    def get_game_spaces(
        state_encode_dims: Optional[BattleStateEncodeDims] = None,
        config: Optional[Dict] = None
    ) -> Tuple[Space, Space]:
        if not state_encode_dims:
            state_encode_dims = BattleStateEncodeDims(config)

        _observation_space = OrderedDict()
        for feature_name in state_encode_dims.state_encode_shape:
            _observation_space[feature_name] = Box(
                -np.inf, np.inf, shape=state_encode_dims.state_encode_shape[feature_name]
            )

        observation_space = Dict(_observation_space)
        action_space = Discrete(state_encode_dims.actions_shape)

        return observation_space, action_space

    def _do_draft(self) -> float:
        start_time = time.time()

        first_player_id = self.state.current_player.id
        first_player_actions = []

        while self.state.phase == Phase.DRAFT:
            draft_agent = self.draft_agents[self.state.current_player.id]
            action = draft_agent.act(self.state)
            first_player_actions.append(action)
            self.state.act(action)

        return time.time() - start_time

    def _encode_state_draft(self):
        pass

    def _encode_state_battle(self):

        if not self.items:
            raise NotImplementedError("not items not supported")

        p0, p1 = self.state.current_player, self.state.opposing_player

        # ------------------------------------------------------------------------
        # players info
        turn_encode = [self.state.turn / PLAYER_TURNLIMIT]
        order_encode = [1 if self.state._current_player == PlayerOrder.FIRST else 0]
        players = turn_encode + order_encode + self.encode_health_lost(p1) + self.encode_player(p0, is_opp=False) + self.encode_player(p1, is_opp=True)

        # ------------------------------------------------------------------------
        # cards in hand
        hand = list(map(self.encode_card_on_hand, p0.hand))
        # hand padding, shape (max_hand, card_encode_dims)
        hand, hand_mask = fill_cards(
            hand, up_to=max_hand, features=self.state_encode_dims.card_encode_dims,
            mask=False
        )

        if self.perfect_training:
            opp_hand = list(map(self.encode_card_on_hand, p1.hand))
            opp_hand, opp_hand_mask = fill_cards(
                opp_hand, up_to=max_hand, features=self.state_encode_dims.card_encode_dims,
                mask=False
            )

        # ------------------------------------------------------------------------
        # cards in current player's lanes
        cur_lane = []
        # cur_lane_mask = []
        for lane_id in (0, 1):
            lane_emb = [0, 0]
            lane_emb[lane_id] = 1
            # convert all cards to features
            lane = list(map(self.encode_friendly_card_on_board, p0.lanes[lane_id]))
            for l in lane:
                l.extend(lane_emb)
            lane, lane_mask = fill_cards(
                lane, up_to=max_lane, features=self.state_encode_dims.cur_lane_card_encode_dims,
                mask=False
            )

            cur_lane.extend(lane)
            # cur_lane_mask.extend(lane_mask)

        # ------------------------------------------------------------------------
        # cards in opposing player's lanes
        opp_lane = []
        # opp_lane_mask = []
        for lane_id in (0, 1):
            lane_emb = [0, 0]
            lane_emb[lane_id] = 1
            # convert all cards to features
            lane = list(map(self.encode_enemy_card_on_board, p1.lanes[lane_id]))
            for l in lane:
                l.extend(lane_emb)
            lane, lane_mask = fill_cards(
                lane, up_to=max_lane, features=self.state_encode_dims.opp_lane_card_encode_dims,
                mask=False
            )

            opp_lane.extend(lane)
            # opp_lane_mask.extend(lane_mask)

        ret = {
            # state
            "players": np.array(players, np.float32),
            "hand": np.array(hand, np.float32),
            # "hand_mask": np.array(hand_mask, np.float32),
            "cur_lane": np.array(cur_lane, np.float32),
            # "cur_lane_mask": np.array(cur_lane_mask, np.float32),
            "opp_lane": np.array(opp_lane, np.float32),
            # "opp_lane_mask": np.array(opp_lane_mask, np.float32),
            # action mask
            "action_mask": np.array(self.state.action_mask, np.float32),
        }

        if self.perfect_training:
            ret.update({
                "opp_hand": np.array(opp_hand, np.float32),
                # "opp_hand_mask": np.array(opp_hand_mask, np.float32),
            })

        return ret


def fill_cards(card_list, up_to, features, mask=True):
    remaining_cards = up_to - len(card_list)
    if mask:
        _mask = [1.0] * len(card_list) + [0.0] * remaining_cards
    else:
        _mask = None

    return card_list + [[0] * features for _ in range(remaining_cards)], _mask

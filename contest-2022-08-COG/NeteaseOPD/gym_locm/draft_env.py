from typing import Union, Tuple, Optional

import time
import gym
from gym.spaces import Space, Box, Dict, Discrete
from gym import spaces, logger

from gym_locm.agents import parse_draft_agent, parse_battle_agent
from gym_locm.engine import *
from gym_locm.base_env import LOCMEnv

from config import ConstructStateEncodeDims

logger.set_level(50)


class LOCMDraftEnv(LOCMEnv):

    def __init__(self, config, inferring=False):
        """
        inferring: 是否推理阶段
        """
        self.inferring = inferring

        seed = config.get("seed", None)  # TODO gym env seed 统一 State seed
        items = config.get("items", True)
        k = config.get("k", 120)
        n = config.get("n", 30)
        self.k, self.n = k, n
        skip_draft = config.get("skip_draft", False)  # 如不需要构筑阶段可跳过以降低时间开销

        super().__init__(seed=seed, items=items, k=k, n=n, skip_draft=skip_draft)

        # init bookkeeping structures
        self.results = []
        self.__card_choices_encode = None  # same for two players

        battle_agent_names = config.get("battle_agents", ("pass", "pass"))
        self.battle_agents = [
            parse_battle_agent(battle_agent_names[0])(),
            parse_battle_agent(battle_agent_names[1])(),
        ]
        for battle_agent in self.battle_agents:
            battle_agent.seed(seed)

        self.evaluation_battles = config.get("evaluation_battles", 1)
        self.use_draft_history = config.get("use_draft_history", False)  # TODO
        self.use_mana_curve = config.get("use_mana_curve", False)  # TODO

        self.card_features = 19

        self.card_choices_shape = (k, self.card_features)
        self.card_chosen_shape = (k, CONSTRUCTED_MAX_COPY+1)
        self.state_shape = (k, self.card_features+CONSTRUCTED_MAX_COPY+1)

        state_encode_dims = ConstructStateEncodeDims()
        self.observation_space, self.action_space = self.get_game_spaces(state_encode_dims)

    @staticmethod
    def get_game_spaces(state_encode_dims: Optional[ConstructStateEncodeDims] = None) -> Tuple[Space, Space]:
        if not state_encode_dims:
            state_encode_dims = ConstructStateEncodeDims()

        observation_space = Dict({
            "state": gym.spaces.Box(
                -np.inf, np.inf,
                shape=state_encode_dims.state_encode_shape["state"],
                dtype=np.float32
            ),
            "action_mask": gym.spaces.Box(
                low=0.0, high=1.0,
                shape=state_encode_dims.state_encode_shape["action_mask"],
                dtype=np.float32
            ),
        })

        action_space = Discrete(state_encode_dims.actions_shape)

        return observation_space, action_space

    def _encode_state_draft(self):

        # chosen_cards = self.state.current_player.deck
        chosen_encode = np.full(self.card_chosen_shape, 0, dtype=np.float32)
        for i, card_copy_count in enumerate(self.state.current_player.chosen_counter):
            chosen_encode[i][card_copy_count] = 1

        encoded_state = np.concatenate(
            [
                copy.deepcopy(self.card_choices_encode),
                chosen_encode,
            ],
            axis=-1
        )
        assert encoded_state.shape == self.state_shape

        if self.state.phase == Phase.DRAFT:
            action_mask = self.state.action_mask
        else:
            action_mask = [False] * self.state.k

        assert len(action_mask) == self.k

        return {
            "state": encoded_state,
            # action mask
            "action_mask": np.array(action_mask, np.float32),
        }

    @property
    def card_choices_encode(self) -> np.ndarray:
        if self.__card_choices_encode is not None:
            return self.__card_choices_encode

        card_choices = self.state.current_player.hand

        encoding = []
        for i, card in enumerate(card_choices):
            encoding.append(self.encode_card(card))
        encoding = np.array(encoding, dtype=np.float32)

        assert encoding.shape == self.card_choices_shape

        self.__card_choices_encode = encoding

        return self.__card_choices_encode

    def _encode_state_battle(self):
        pass


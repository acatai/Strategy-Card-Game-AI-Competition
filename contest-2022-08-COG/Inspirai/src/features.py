import torch
import numpy as np

from src.envs_utils import *
from src import const


class VectorEncoder(torch.nn.Module):
    def __init__(self, name, input_size, output_size, max_len=None):
        super().__init__()
        self.name = name
        self.max_len = max_len
        self.input_size = input_size
        self.output_size = output_size
        self.encoder = torch.nn.Sequential(
            torch.nn.Linear(input_size, output_size),
            torch.nn.ReLU(),
            torch.nn.Linear(output_size, output_size),
            torch.nn.ReLU(),
        )

    def forward(self, x):
        return self.encoder(x)


def pad(vectors, max_len, dim):
    vectors = vectors[:max_len]
    return vectors + [[0] * dim] * (max_len - len(vectors))


def one_hot(value, v_range: 'list|tuple|range', other: bool = False):
    vector = [0] * (len(v_range) + int(other))
    vector[-1 if (value not in v_range and other) else v_range.index(value)] = 1
    return vector


def obs2state(obs, cache: dict):
    agent2id = cache[const.agent2id]

    # preparing
    status, obs, valid_action = obs

    agent2state = {}
    for agent, player in agent2id.items():
        step = cache[const.step][agent]

        players = [[
            player[k] for k in sorted(player.keys())
        ] for player in obs[const.players]]

        cards = [[
            # *one_hot(card['card_number'], range(144)),  # check: how many unique cards.
            *one_hot(card['location'], range(-1, 2)),
            *one_hot(card['card_type'], range(4)),
            card['cost'],
            card['attack'],
            card['defense'],
            *sum([one_hot(ability, ('-',), other=True) for ability in card['abilities']], []),
            card['my_health_change'],
            card['opponent_health_change'],
            card['card_draw'],
            *one_hot(card['area'], range(3)),
            *one_hot(card['lane'], range(-1, 2)),
        ] for card in obs[const.cards]]

        lanes = [[
            *one_hot(lane, range(2)),
            len(filter_cards(obs[const.cards], lane=lane, location=BOARD)),
            len(filter_cards(obs[const.cards], lane=lane, location=FOE)),
            sum([card['attack'] for card in filter_cards(obs[const.cards], lane=lane, location=BOARD)]),
            sum([card['attack'] for card in filter_cards(obs[const.cards], lane=lane, location=FOE)]),
            sum([card['defense'] for card in filter_cards(obs[const.cards], lane=lane, location=BOARD)]),
            sum([card['defense'] for card in filter_cards(obs[const.cards], lane=lane, location=FOE)]),
        ] for lane in range(2)]

        common = [[
            step,  # \in [0, \inf]
            obs['opponent_hand'],
            obs['opponent_actions'],
        ]]

        end = [[
            1,
        ]]

        # mask
        from src.actions import get_mask
        card_mask, target_mask = get_mask(obs, valid_action)

        agent2state[agent] = {
            const.players: players,
            const.cards: cards,
            const.lanes: lanes,
            const.common: common,
            const.end: end,

            const.card_mask: card_mask,
            const.target_mask: target_mask,
            # NOTE: `argmax` is worse than `sample`
            const.temperature: 1,
        }

        for name, encoder in encoders.items():
            agent2state[agent][name] = pad(agent2state[agent][name], encoder.max_len, encoder.input_size)

    # print(agent2state)
    return agent2state


# hyperparameter
feature_size = 256

# Encoder
encoders = {encoder.name: encoder for encoder in [
    # NOTE: this order is related to action postprocess !
    VectorEncoder(const.players, 4, feature_size, max_len=2),
    VectorEncoder(const.lanes, 8, feature_size, max_len=2),
    VectorEncoder(const.cards, 31, feature_size, max_len=20),
    VectorEncoder(const.common, 3, feature_size, max_len=1),
    VectorEncoder(const.end, 1, feature_size, max_len=1),
]}
entity_len = sum(encoder.max_len for encoder in encoders.values())

# target_idx
PLAYER_START = 0
LANE_START = 2
CARD_START = 4
COMMON_START = 24
END_START = 25

import numpy as np

from src.envs_utils import *
from src import const


def get_mask(obs, valid_action):
    from src.features import entity_len, END_START

    card_mask = np.zeros((entity_len,))
    target_mask = np.zeros((entity_len, entity_len))
    target_id2output_idx, lane_id2output_idx, _ = get_env_id_map_output_idx(obs)

    card_mask[END_START] = 1
    for card_id, (target_ids, lane_ids), in valid_action.items():
        card_idx = target_id2output_idx[card_id]
        card_mask[card_idx] = 1
        target_idxs = [target_id2output_idx[target_id] for target_id in target_ids] + [lane_id2output_idx[lane_id] for lane_id in lane_ids]
        target_mask[card_idx][target_idxs] = 1

    return card_mask, target_mask


def get_env_id_map_output_idx(obs):
    from src.features import PLAYER_START, LANE_START, CARD_START

    target_id2output_idx = {
        **{-1: PLAYER_START + 1},  # player
        **{card['instance_id']: CARD_START + i for i, card in enumerate(obs[const.cards])}  # card
    }
    lane_id2output_idx = {0: LANE_START, 1: LANE_START + 1}  # lane
    output_idx2env_id = {
        **{v: k for k, v in target_id2output_idx.items()},
        **{v: k for k, v in lane_id2output_idx.items()},
    }

    return target_id2output_idx, lane_id2output_idx, output_idx2env_id


def output2action(agent, output, cache: dict):
    from src.features import END_START, CARD_START

    obs = cache[const.last_obs][agent]
    status, obs, valid_action = obs
    post_output = {}

    target_id2output_idx, _, output_idx2env_id = get_env_id_map_output_idx(obs)

    post_output[const.card_valid] = np.asarray(1)
    card = output[const.card].item()
    target = output[const.target].item()
    if card != END_START:
        action = (output_idx2env_id[card], output_idx2env_id[target])
        post_output[const.target_valid] = np.asarray(1)
    else:
        action = None
        post_output[const.target_valid] = np.asarray(0)

    return action, post_output


import os
import sys
import time

import torch
import numpy as np

from src import const
from src import engine
from src import torch_utils
from src.network import Network
from src.features import obs2state
from src.actions import output2action

torch.set_num_threads(1)
# os.environ["OMP_NUM_THREADS"] = "1"  # export OMP_NUM_THREADS=1
# # os.environ["OPENBLAS_NUM_THREADS"] = "1" # export OPENBLAS_NUM_THREADS=1
# os.environ["MKL_NUM_THREADS"] = "1"  # export MKL_NUM_THREADS=1
# # os.environ["VECLIB_MAXIMUM_THREADS"] = "1" # export VECLIB_MAXIMUM_THREADS=1
# os.environ["NUMEXPR_NUM_THREADS"] = "1"  # export NUMEXPR_NUM_THREADS=1


# NOTE: dangerous code ! redirect all print(...) to sys.stderr
stdout = sys.stdout
sys.stdout = sys.stderr
init_time = time.time()


# load model
model_file = os.path.join(os.path.dirname(__file__), 'weights', 'checkpoint-1657608313476464135.npz')
network = Network()
network.requires_grad_(False)
npz_file = np.load(model_file)
weights = [npz_file[file] for file in npz_file]
for target_p, p in zip(network.parameters(), weights):
    target_p.copy_(torch.from_numpy(p))
network = network.eval()

# preparing
agent, player = '0', 0
sim_env = engine.State()
cache = {
    const.agent2id: {agent: player},
}

while True:
    obs = {'player_id': player}

    players = obs.setdefault('players', [])
    for i in range(2):
        player_health, player_mana, player_deck, player_draw = [int(j) for j in input().split()]
        players.append(dict(
            player_health=player_health,
            player_mana=player_mana,
            player_deck=player_deck,
            player_draw=player_draw,
        ))

    opponent_hand, opponent_actions = [int(i) for i in input().split()]
    obs.update(dict(
        opponent_hand=opponent_hand,
        opponent_actions=opponent_actions,
    ))

    card_number_and_action = obs.setdefault('card_number_and_action', [])
    for i in range(opponent_actions):
        card_number_and_action.append(input())

    cards = obs.setdefault('cards', [])
    for i in range(int(input())):
        inputs = input().split()
        cards.append(dict(
            card_number=int(inputs[0]),
            instance_id=int(inputs[1]),
            location=int(inputs[2]),
            card_type=int(inputs[3]),
            cost=int(inputs[4]),
            attack=int(inputs[5]),
            defense=int(inputs[6]),
            abilities=inputs[7],
            my_health_change=int(inputs[8]),
            opponent_health_change=int(inputs[9]),
            card_draw=int(inputs[10]),
            area=int(inputs[11]),
            lane=int(inputs[12]),
        ))

    start_time = time.time()

    if obs['players'][0]['player_mana'] == 0:
        from src import envs_utils
        action = envs_utils.draft_strategy_monster(obs)
    else:
        actions = []
        sim_env.update(obs)
        while True:
            valid_action = sim_env.get_action_mask()

            # early stop near time limit
            if time.time() - start_time >= 0.18:
                actions.extend(sim_env.post_process(valid_action)[1])
                print(f'early stop', flush=True)
                break

            if valid_action:
                obs = "STEP", obs, valid_action

                # predict
                cache.setdefault(const.step, {}).setdefault(agent, 0)
                cache.setdefault(const.last_obs, {}).setdefault(agent, obs)

                state = obs2state(obs, cache)[agent]
                state = torch_utils.unsqueeze({k: np.array(v, dtype=np.float32) for k, v in state.items()})

                cache[const.step][agent] += 1
                cache[const.last_obs][agent] = obs

                outputs = network.forward(torch_utils.to_tensor(state, cuda=False))
                outputs = torch_utils.squeeze({k: v.cpu().detach().numpy() for k, v in outputs.items()})
                action, _ = output2action(agent, outputs, cache)

                if action is not None:
                    obs, action = sim_env.step(*action)
                    actions.append(action)
                else:
                    break
            else:
                break
        action = ';'.join(actions) if actions else 'PASS'

    print(action, file=stdout, flush=True)
    print(f'Action time cost: {round((time.time() - start_time) * 1000, 1)} ms', flush=True)
    print(f'Total time cost: {round((time.time() - init_time) * 1000, 1)} ms', flush=True)


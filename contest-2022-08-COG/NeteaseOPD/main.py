"""
"""
import time

main_start_time = time.perf_counter()

import os
import sys
from typing import List
import argparse

os.environ["CUDA_VISIBLE_DEVICES"] = ""

parser = argparse.ArgumentParser()

parser.add_argument(
    "--debug-mode",
    action="store_true",
    help="",
)

# ONNX
parser.add_argument(
    "--draft-model-path",
    type=str,
    default=os.path.join(os.path.dirname(__file__), "models", "draft_model.onnx"),
    help="",
)
parser.add_argument(
    "--battle-model-path",
    type=str,
    default=os.path.join(os.path.dirname(__file__), "models", "battle_model.onnx"),
    help="",
)

# OTK
parser.add_argument(
    "--no-otk",
    action="store_true",
    help="",
)


def read_game_input():
    # read players info
    game_input = []
    game_input.append(input())
    first_input_time = time.perf_counter()
    game_input.append(input())

    # read cards in hand and actions from opponent
    opp_hand, opp_actions = [int(i) for i in input().split()]
    game_input.append(f"{opp_hand} {opp_actions}")

    # read all opponent actions
    for i in range(opp_actions):
        game_input.append(input())  # opp action #i

    # read card count
    card_count = int(input())
    game_input.append(str(card_count))

    # read cards
    for i in range(card_count):
        game_input.append(input())  # card #i

    return game_input, first_input_time


if __name__ == "__main__":

    draft_start_time = main_start_time

    # import in construct phase
    from gym_locm.custom_rl_agents import (
        Phase, State, Action, ActionType,
        CustomRLDraftONNXAgent, CustomRLBattleONNXAgent,
        BattleModelImprovementRules,
    )

    draft_agent, battle_agent, playing_first = None, None, None
    battle_turn = 0

    safe_battle_inference_time = 0.02
    safe_otk_search_time = 0.01

    args = parser.parse_args()

    while True:

        game_input, turn_start_time = read_game_input()
        # turn_start_time = time.perf_counter()

        if battle_turn == 0:  # construct phase

            if draft_agent is None:

                start_time = time.perf_counter()
                draft_agent = CustomRLDraftONNXAgent(args.draft_model_path)
                if args.debug_mode:
                    print(
                        "Draft agent load time: {:.3f}s, model path: {}".format(
                            time.perf_counter() - start_time,
                            args.draft_model_path,
                        ),
                        file=sys.stderr,
                        flush=True,
                    )

                start_time = time.perf_counter()
                battle_agent = CustomRLBattleONNXAgent(args.battle_model_path)
                if args.debug_mode:
                    print(
                        "Battle agent load time: {:.3f}s, model path: {}".format(
                            time.perf_counter() - start_time,
                            args.battle_model_path,
                        ),
                        file=sys.stderr,
                        flush=True,
                    )

            state = State.from_native_input(game_input, phase=Phase.DRAFT)

            actions: List[Action] = []

            for i in range(30):

                action_instance = draft_agent.act(state)
                state.act(action_instance)

                actions.append(action_instance)

            if args.debug_mode:
                print(
                    "Draft total time {:.3f}s".format(
                        time.perf_counter() - draft_start_time
                    ),
                    file=sys.stderr,
                    flush=True,
                )

            draft_agent = None  # release draft phase memory

            print(";".join(map(Action.to_native, actions)))

        else:  # battle phase

            turn_time_limit = 1.0 if battle_turn == 1 else 0.2

            if playing_first is None:

                playing_first = game_input[0].split()[2] == game_input[1].split()[2]

                start_time = time.perf_counter()

                # battle_agent = CustomRLBattleONNXAgent(args.battle_model_path)
                improvement_rules = BattleModelImprovementRules()

                if args.debug_mode:
                    print(
                        "Load time: {:.3f}s, playing first: {}".format(
                            time.perf_counter() - start_time,
                            playing_first,
                        ),
                        file=sys.stderr,
                        flush=True,
                    )

            state = State.from_native_input(
                game_input,
                phase=Phase.BATTLE,
                playing_first=playing_first,
                last_state=state,
                turn=battle_turn,
            )

            actions: List[Action] = []
            can_otk = False
            timeout = False
            model_pass = False
            win = False
            attack_opp_actions = None
            if not args.no_otk:
                init_state_for_otk = state.otk_clone()  # for otk search

            while True:

                if (
                    time.perf_counter() - turn_start_time + safe_battle_inference_time
                    >= turn_time_limit
                ):
                    timeout = True
                    model_pass = True
                    if args.debug_mode:
                        print(
                            "Battle model timeout, force PASS",
                            file=sys.stderr,
                            flush=True,
                        )
                    break

                can_otk, attack_opp_actions = improvement_rules.naive_otk(state)
                if can_otk:
                    actions.extend(attack_opp_actions)
                    win = True
                    if args.debug_mode:
                        print(
                            "All Attack OTK: {}".format(attack_opp_actions),
                            file=sys.stderr,
                            flush=True,
                        )
                    break

                if sum(state.action_mask) == 1:
                    action_instance = Action(ActionType.PASS)
                else:
                    _start = time.perf_counter()
                    action_instance = battle_agent.act(state=state)
                    if args.debug_mode:
                        print(
                            "* battle inference time: {:.2f} ms".format(
                                (time.perf_counter() - _start) * 1000
                            ),
                            file=sys.stderr,
                            flush=True,
                        )

                if args.debug_mode:
                    print(
                        f"Action: {action_instance}\n",
                        file=sys.stderr,
                        flush=True,
                    )

                if action_instance == Action(ActionType.PASS):
                    model_pass = True
                    break

                actions.append(action_instance)
                state.act(action_instance)
                if state.winner is not None:
                    win = True
                    break

            # rules after model
            if not win:

                # force all attack opp
                if model_pass:
                    if isinstance(attack_opp_actions, list):
                        actions_before_pass = attack_opp_actions
                    else:
                        actions_before_pass = improvement_rules.before_pass(state)
                    actions.extend(actions_before_pass)
                    if args.debug_mode and actions_before_pass:
                        print(
                            "Model PASS but force: {}".format(actions_before_pass),
                            file=sys.stderr,
                            flush=True,
                        )

                # search otk actions
                otk_search_time_limit = (
                    turn_time_limit
                    - (time.perf_counter() - turn_start_time)
                    - safe_otk_search_time
                )
                if not args.no_otk and otk_search_time_limit > 0:
                    (
                        can_otk,
                        otk_actions,
                        otk_time_out,
                        otk_time,
                        otk_num_seen,
                        otk_num_search,
                    ) = improvement_rules.otk(
                        init_state_for_otk,
                        time_limit=otk_search_time_limit,
                    )

                    if args.debug_mode:
                        print(
                            f"Turn otk search, time limit {otk_search_time_limit * 1000:.2f} ms. "
                            f"Search time: {otk_time * 1000:.2f} ms, timeout: {otk_time_out}, "
                            f"can otk: {can_otk}, "
                            f"seen states: {otk_num_seen}, searched states: {otk_num_search}\n",
                            file=sys.stderr,
                            flush=True,
                        )
                    if can_otk:
                        if args.debug_mode:
                            print(
                                f"OTK! Model remain opp {state.opposing_player.health} HP "
                                f"but can OTK with {otk_actions}.\n",
                                file=sys.stderr,
                                flush=True,
                            )
                        actions = otk_actions

                elif not args.no_otk:
                    if args.debug_mode:
                        time_remain = turn_time_limit - (
                            time.perf_counter() - turn_start_time
                        )
                        print(
                            f"No time to search OTK. Time remain: {time_remain * 1000:.2f} ms\n",
                            file=sys.stderr,
                            flush=True,
                        )

            if actions:
                print(";".join(map(Action.to_native, actions)))
            else:
                print("PASS")

        battle_turn += 1

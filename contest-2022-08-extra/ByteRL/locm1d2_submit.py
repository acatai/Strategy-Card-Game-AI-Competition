from engine import State, ActionType
from agent import ByterlAgent


def read_game_input():
    # read players info
    game_input = [input(), input()]

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

    return game_input


def _create_byterl_agent():
    agent = ByterlAgent()
    return agent

def to_native(actions):
    action_map = ["PICK", "SUMMON", "ATTACK", "USE", "PASS"]
    if actions is None or actions.type == ActionType.PASS:
        return "PASS"
    elif actions.type == ActionType.SUMMON:
        return f"SUMMON {actions.origin} {int(actions.target)}"
    else:
        target = actions.target if actions.target is not None else -1
        return f"{action_map[actions.type.value]} {actions.origin} {target}"

def create_agent():
    agent = ByterlAgent()
    return agent

def main():
    agent = None
    while True:
        # get the input for the turn
        game_input = read_game_input()
        # if mana is zero then it is draft phase
        is_draft_phase = int(game_input[0].split()[1]) == 0

        if agent is None:
            agent = create_agent()
            agent.reset()
        if is_draft_phase:
            state = State.from_native_input(game_input)
            action = agent.act(state)
            print("PICK", action.origin)
        else:
            state = State.from_native_input(game_input)
            actions = []
            while True:
                if any(state.action_mask):
                    action = agent.act(state)
                else:
                    action = None
                actions.append(to_native(action))
                if action is None or action.type == ActionType.PASS:
                    print(";".join(actions))
                    break
                else:
                    state.act(action)


if __name__ == '__main__':
    main()


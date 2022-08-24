import importlib
import traceback
from engine import State, ActionType
from agent import ByterlAgent


def import_module_or_data(import_path):
    try:
        maybe_module, maybe_data_name = import_path.rsplit(".", 1)
        ret = getattr(importlib.import_module(maybe_module), maybe_data_name)
        return ret
    except Exception as e:
        tb = traceback.format_exc()

    try:
        ret = importlib.import_module(import_path)
        return ret
    except Exception as e:
        tb = traceback.format_exc()

    raise ImportError('Cannot import module or data using {}'.format(import_path))


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
    return _create_byterl_agent()


class CardRecorder:
    def __init__(self) -> None:
        self.my_deck = []
        self.last_hands_instanceid = []

    def recorder_draft(self, cards, my_choose):
        self.my_deck.append(cards[my_choose])

    def recorder_battle(self, state):
        for card_hand in state.players[0].hand:
            if card_hand.instance_id not in self.last_hands_instanceid:
                for idx, card_deck in enumerate(self.my_deck):
                    if card_hand.id == card_deck.id:
                        self.my_deck.pop(idx)
                        break
        self.last_hands_instanceid = [card.instance_id for card in state.current_player.hand]

    def full_missing_cards(self, state):
        if state.current_player.hand:
            instance_id = max(card.instance_id for card in state.current_player.hand) + 1
        else:
            instance_id = 0
        d1 = []
        assert len(self.my_deck) == len(state.current_player.deck)
        for card in self.my_deck:
            d1.append(card.make_copy(instance_id))
            instance_id += 1
        state.current_player.deck = d1
        return state


def main():
    agent = None
    cardrecorder = CardRecorder()
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
            actions = []
            for _ in range(30):
                state._current_player = 0
                action = agent.act(state)
                cardrecorder.recorder_draft(state.current_player.hand, action.origin)
                state.act(action)
                actions.append(f"CHOOSE {action.origin}")
            print(" ; ".join(actions))
        else:
            state = State.from_native_input(game_input)
            cardrecorder.recorder_battle(state)
            state = cardrecorder.full_missing_cards(state)
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

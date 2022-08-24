from dataclasses import dataclass
from functools import partial

from src import const

MINION = 0
GREEN = 1
RED = 2
BLUE = 3

BOARD = 1
FOE = -1
HAND = 0
ENEMY_HAND = -2
ENEMY_DECK = -3

LEFT = 0
RIGHT = 1


def filter_cards(cards, **filters):
    result_cards = []
    for card in cards:
        if all(
                card[k] == v or (isinstance(v, set) and card[k] in v)
                for k, v in filters.items()
        ):
            result_cards.append(card)
    return result_cards


@dataclass(frozen=True)
class DraftConfig(object):
    area: float
    cost: float
    att_def_sum: float
    att_def_hm: float
    monster: float
    lethal: float
    ward: float
    guard: float
    breakthrough: float
    drain: float
    red_blue: float
    green: float
    green_ward: float
    monster_multi: float
    monster_no_att: float
    card_draw: float


def card_score_base(card: dict, config: DraftConfig) -> float:
    c = config

    card_lethal = int('L' in card['abilities'])
    card_ward = int('W' in card['abilities'])
    card_guard = int('G' in card['abilities'])
    card_breakthrough = int('B' in card['abilities'])
    card_drain = int('D' in card['abilities'])
    card_charge = int('C' in card['abilities'])

    score = 0.0
    area = c.area if card['area'] != 0 else 1.0
    score += c.cost * card['cost']
    score += c.att_def_sum * area * (abs(card['attack']) + abs(card['defense'])) / max(1, card['cost'])

    if abs(card['attack']) + abs(card['defense']) > 0:
        att_def_hm = abs(card['attack']) * abs(card['defense']) / (abs(card['attack']) + abs(card['defense']))
        score += c.att_def_hm * area * att_def_hm

    if card['card_type'] == MINION:
        monster_score = c.monster + card_lethal * c.lethal + card_ward * c.ward + \
                        card_guard * c.guard + card_breakthrough * c.breakthrough + card_drain * c.drain
        monster_score *= area
        score += monster_score
    elif card['card_type'] != GREEN:
        score += c.red_blue * (abs(card['attack']) + abs(card['defense'])) * area
    else:
        score += c.green + c.green_ward * card_ward * area

    if card['card_type'] == MINION and card_charge and card_lethal and card['attack'] > 0:
        score += c.monster_multi * area

    if card['card_type'] == MINION and card['attack'] == 0:
        score += c.monster_no_att

    score += c.card_draw * area * card['card_draw']

    return score


def draft_strategy(obs, config: DraftConfig, twice: bool, min_monster: int = 0) -> str:
    """ Draft cards according to draft config weights.

    Args:
        obs: card observation.
        config: weights used to evaluate card score.
        twice: whether draft high score card twice.
        min_monster: mininum monster number to draft.

    Returns:
        A string of draft commands.
    """
    card_score = partial(card_score_base, config=config)
    cards = [c for c in obs[const.cards]]
    cards = sorted(cards, key=card_score, reverse=True)
    selected = {}
    for c in cards:
        if min_monster <= 0:
            break
        if c['card_type'] == MINION:
            selected[c['card_number']] = (1 + twice)
            min_monster -= (1 + twice)
    for c in cards:
        if sum(selected.values()) >= 30:
            break
        if selected.get(c['card_number'], 0) >= 2:
            continue
        selected[c['card_number']] = selected.get(c['card_number'], 0) + (1 + twice)
    selected = sum([[k] * v for k, v in selected.items()], [])
    selected = ';'.join([f'CHOOSE {s}' for s in selected])
    return selected


def draft_strategy_baseline3(obs):
    # draft strategy from Baseline3
    baseline3 = DraftConfig(
        area=1.5,
        cost=-4.0,
        att_def_sum=1.0,
        att_def_hm=2.0,
        monster=4.0,
        lethal=4.0,
        ward=4.0,
        guard=2.0,
        breakthrough=1.0,
        drain=2.0,
        red_blue=1.0,
        green=2.0,
        green_ward=5.0,
        monster_multi=4.0,
        monster_no_att=-2.0,
        card_draw=1.0,
    )
    return draft_strategy(obs, baseline3, twice=False)


def draft_strategy_coacbo(obs):
    # draft strategy from Coac-BO
    coacbo = DraftConfig(
        area=-3.779216981947414,
        cost=-3.7998646581933975,
        att_def_sum=-4.450924576381176,
        att_def_hm=1.1914191568197516,
        monster=1.4308790882830391,
        lethal=-3.983350714836453,
        ward=2.1011340087179864,
        guard=2.156171607641912,
        breakthrough=-3.1048119973463457,
        drain=0.8286945260657275,
        red_blue=-0.23560153858421984,
        green=-0.8618647982692815,
        green_ward=1.1256445689216639,
        monster_multi=-2.6645675460661264,
        monster_no_att=-1.0590017361786237,
        card_draw=0.37833242963248814,
    )
    return draft_strategy(obs, coacbo, twice=True)


def draft_strategy_monster(obs):
    # draft strategy with minimum monster limit
    monster = DraftConfig(
        area=-3.779216981947414,
        cost=-3.7998646581933975,
        att_def_sum=-4.450924576381176,
        att_def_hm=1.1914191568197516,
        monster=1.4308790882830391,
        lethal=-3.983350714836453,
        ward=2.1011340087179864,
        guard=2.156171607641912,
        breakthrough=-3.1048119973463457,
        drain=0.8286945260657275,
        red_blue=-0.23560153858421984,
        green=-0.8618647982692815,
        green_ward=1.1256445689216639,
        monster_multi=-2.6645675460661264,
        monster_no_att=-1.0590017361786237,
        card_draw=0.37833242963248814,
    )
    return draft_strategy(obs, monster, twice=True, min_monster=8)

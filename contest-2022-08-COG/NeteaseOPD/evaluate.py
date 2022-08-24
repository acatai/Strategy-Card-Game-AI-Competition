import sys
import math
from collections import namedtuple

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.


class Card:
    def __init__(
        self,
        card_id,
        instance_id,
        location,
        type,
        cost,
        attack,
        defense,
        keywords,
        my_health,
        opponent_health,
        card_draw,
        area,
        lane,
    ):
        self.card_id = card_id
        self.instance_id = instance_id
        self.location = location
        self.type = type
        self.cost = cost
        self.attack = attack
        self.defense = defense
        self.keywords = keywords
        self.my_health = my_health
        self.opponent_health = opponent_health
        self.card_draw = card_draw
        self.area = area
        self.lane = lane
        self.text = ' '.join(list(map(str, [card_id, instance_id, type, cost, attack, defense, keywords, my_health, opponent_health, card_draw, area])))
        self.can_attack = False


class Deck:
    def __init__(self):
        self.card_list = []
        self.score_list = []
        # record
        self.type_distribution = [0] * 4  # [Creature, Green, Red, Blue]
        self.mana_distribution = [1] * 13
        self.abilities_distribution = [0] * 6  # [B, C ,D, G, L, W]
        self.power_distribution = [0] * 3  # [my_health, opp_health, card_draw]
        # weights
        self.w_creature_base = [0.5, 1.0]  # [health, attack]
        self.w_reditem_base = [1.0, 0.5]  # [health, attack]
        self.w_abilities = [0.0, 2.0, 1.0, 1.0, 0.0, 0.0]  # [B, C, D, G, L, W]
        self.w_power = [0.5, 1.0, 1.5]  # [my_health, opp_health, draw]
        self.w_type = [1.0, 1.0, 1.0, 0.0]  # [Creature, Green, Red, Blue]

        self.w_creature_area = [1.0, 4.0, 4.0]  # creature [target, lane1, lane2]
        self.w_item_area = [1.0, 4.0, 5.0]  # item [target, lane1, lane2]

    def add_card(self, card: Card):
        self.type_distribution[card.type] += 1
        self.mana_distribution[card.cost] += 1
        self.abilities_distribution = [x + y for x, y in zip(self.abilities_distribution, self.convert_keywords_to_list(card.keywords))]
        self.power_distribution[0] += (1 if card.my_health > 0 else 0)
        self.power_distribution[1] += (1 if card.opponent_health > 0 else 0)
        self.power_distribution[2] += (1 if card.card_draw > 0 else 0)
        self.card_list.append(card)
        self.score_list.append(self.evaluate(card))

    @staticmethod
    def convert_keywords_to_list(keywords: str) -> list:
        return [
            1 if 'B' in keywords else 0,
            1 if 'C' in keywords else 0,
            1 if 'D' in keywords else 0,
            1 if 'G' in keywords else 0,
            1 if 'L' in keywords else 0,
            1 if 'W' in keywords else 0
        ]

    @staticmethod
    def list_dot_multiply(list_a: list, list_b: list) -> list:
        assert len(list_a) == len(list_b)
        return [x * y for x, y in zip(list_a, list_b)]

    @staticmethod
    def create_mask(index: int, length: int) -> list:
        mask = [0] * length
        mask[index] = 1
        return mask

    def evaluate(self, card: Card) -> float:
        score = 0.0
        # health and attack
        if card.type == 2:
            score += self.w_reditem_base[0] * abs(card.defense) + self.w_reditem_base[1] * abs(card.attack)
        else:
            score += self.w_creature_base[0] * abs(card.defense) + self.w_creature_base[1] * abs(card.attack)
        # type
        w = self.w_type
        mask = self.create_mask(card.type, 4)
        score += sum(self.list_dot_multiply(self.list_dot_multiply(mask, [(30.0 - x) / 5.0 for x in self.type_distribution]), w))
        # mana
        w = [1] * 13
        mask = self.create_mask(card.cost, 13)
        score += sum(self.list_dot_multiply(self.list_dot_multiply(mask, [(12.0 - x) / 2.0 for x in self.mana_distribution]), w))
        # abilities
        w = self.w_abilities  # temp w for short
        keywords_list = self.convert_keywords_to_list(card.keywords)
        score += sum(self.list_dot_multiply(w, keywords_list))
        # power
        w = self.w_power
        power_list = [card.my_health, card.opponent_health, card.card_draw]
        score += sum(self.list_dot_multiply(w, power_list))
        # divide mana
        score /= (card.cost + 1)

        return score


MINION = 0
GREEN = 1
RED = 2
BLUE = 3

BOARD = 1
FOE = -1
HAND = 0

# game loop
turn = 0
n = -1
while True:
    health, mana, deck, draw = [int(j) for j in input().split()]
    opponent_health, opponent_mana, opponent_deck, opponent_draw = [
        int(j) for j in input().split()
    ]

    opponent_hand, opponent_actions = [int(i) for i in input().split()]
    opponent_actions_list = []
    for i in range(opponent_actions):
        opponent_actions_list.append(input())

    card_count = int(input())
    cards = []
    cards_lane = []
    for i in range(card_count):
        (
            card_id,
            instance_id,
            location,
            type,
            cost,
            attack,
            defense,
            keywords,
            my_health,
            opponent_health,
            card_draw,
            area,
            lane,
        ) = input().split()

        card_id = int(card_id)
        instance_id = int(instance_id)
        location = int(location)
        type = int(type)
        cost = int(cost)
        attack = int(attack)
        defense = int(defense)
        my_health = int(my_health)
        opponent_health = int(opponent_health)
        card_draw = int(card_draw)
        area = int(area)
        lane = int(lane)

        card = Card(
            card_id,
            instance_id,
            location,
            type,
            cost,
            attack,
            defense,
            keywords,
            my_health,
            opponent_health,
            card_draw,
            area,
            lane,
        )
        cards.append(card)
        if card.area > 0:
            cards_lane.append(card)
        else:
            cards_lane.append(None)

    for c in cards:
        if c.location == BOARD:
            c.can_attack = True
            # print('can attack with', c.instance_id, file=sys.stderr)
        else:
            c.can_attack = False
            # print('cant attack with', c.instance_id, file=sys.stderr)

    # Construct Phase
    if mana == 0:
        deck = Deck()
        pick_list = []
        count_chosen_times = [0] * 120
        # f = open('D:\\cog\\log\\draft.log', 'w', encoding='utf-8')

        # calculate score for all 120 cards
        for i in range(30):
            max_score = -1000000.0
            card_index = 0
            card = None
            # print('***************************************************************************************', file=f)
            for j, c in enumerate(cards_lane):
                if c:
                    score = deck.evaluate(c)
                    # print('card:', c.text, 'score:', score, file=f)
                    if c.type <= 2 and score > max_score and count_chosen_times[j] < 2 and c.cost <= 8:
                        max_score = score
                        card_index = j
                        card = c
            count_chosen_times[card_index] += 1
            pick_list.append("CHOOSE {}".format(card_index))
            deck.add_card(card)

        # f.close()

        print('mana_distribution:', deck.mana_distribution, file=sys.stderr)
        print('type_distribution', deck.type_distribution, file=sys.stderr)
        print('power_distribution', deck.power_distribution, file=sys.stderr)
        print('abilities_distribution', deck.abilities_distribution, file=sys.stderr)

        print(";".join(pick_list))

    # Battle Phase
    else:
        actions = []
        stop = False
        summoned_this_turn = []
        attacked_this_turn = []
        items_used_this_turn = []
        while stop is False:
            n += 1
            on_board = []
            foes = []
            stop = True
            for c in cards:
                if c.location == BOARD:
                    on_board.append(c)
                elif c.location == FOE:
                    foes.append(c)
            for c in cards:
                if c.location == HAND and c.cost <= mana and c.type == MINION:
                    actions.append("SUMMON " + str(c.instance_id) + " " + str(n % 2))
                    mana -= c.cost
                    c.location = BOARD
                    c.can_attack = "C" in c.keywords
                    summoned_this_turn.append(c)
                    on_board.append(c)
                    stop = False
                elif c.location == BOARD and c.can_attack:
                    targ = -1
                    for enemy in cards:
                        if enemy.location == FOE and enemy.lane == c.lane:
                            if "G" in enemy.keywords:
                                targ = enemy.instance_id
                                break
                    actions.append("ATTACK " + str(c.instance_id) + " " + str(targ))
                    attacked_this_turn.append(c)
                    c.can_attack = False
                    stop = False
                elif (
                    c.location == HAND
                    and c.cost <= mana
                    and c.type == GREEN
                    and len(on_board) > 0
                    # and not items_used_this_turn
                ):
                    actions.append(
                        "USE " + str(c.instance_id) + " " + str(on_board[0].instance_id)
                    )
                    items_used_this_turn.append(c)
                    mana -= c.cost
                    cards.remove(c)
                    stop = False
                elif (
                    c.location == HAND
                    and c.cost <= mana
                    and c.type == RED
                    and len(foes) > 0
                    # and not items_used_this_turn
                ):
                    actions.append(
                        "USE " + str(c.instance_id) + " " + str(foes[0].instance_id)
                    )
                    items_used_this_turn.append(c)
                    mana -= c.cost
                    cards.remove(c)
                    stop = False
                elif (
                    c.location == HAND
                    and c.cost <= mana
                    and c.type == BLUE
                    # and not items_used_this_turn
                ):
                    actions.append("USE " + str(c.instance_id) + " -1")
                    items_used_this_turn.append(c)
                    mana -= c.cost
                    cards.remove(c)
                    stop = False

        if actions:
            pass
            print(";".join(actions))
        else:
            print("PASS")
    turn += 1

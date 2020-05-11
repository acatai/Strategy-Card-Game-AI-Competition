import sys
import math
from collections import namedtuple
# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

class Card():
    def __init__(self, card_name, instance_id, location, type, cost, attack, defense, keywords, my_health, opponent_health, card_draw, lane):
        self.card_name = card_name
        self. instance_id =  instance_id
        self. location =  location
        self. type =  type
        self. cost =  cost
        self. attack =  attack
        self. defense =  defense
        self. keywords =  keywords
        self. my_health =  my_health
        self. opponent_health =  opponent_health
        self. card_draw =  card_draw
        self.lane = lane
        self.can_attack = False

MINION = 0
GREEN = 1
RED = 2
BLUE = 3

BOARD = 1
FOE = -1
HAND = 0


# game loop
turn = 0
n=-1
while True:
    health, mana, deck, rune, draw = [int(j) for j in input().split()]
    input()
    opponent_hand, opponent_actions = [int(i) for i in input().split()]
    for i in range(opponent_actions):
        card_number_and_action = input()
    card_count = int(input())
    
    cards = []
    for i in range(card_count):
        card_name, instance_id, location, type, cost, attack, defense, keywords, my_health, opponent_health, card_draw, lane = input().split()
        card_name = int(card_name)
        instance_id = int(instance_id)
        location = int(location)
        type = int(type)
        cost = int(cost)
        attack = int(attack)
        defense = int(defense)
        my_health = int(my_health)
        opponent_health = int(opponent_health)
        card_draw = int(card_draw)
        lane = int(lane)
        card = Card(card_name, instance_id, location, type, cost, attack, defense, keywords, my_health, opponent_health, card_draw, lane)
        cards.append(card)
    for c in cards:
        if c.location == BOARD:
            c.can_attack = True
            #print('can attack with', c.instance_id, file=sys.stderr)            
        else:
            c.can_attack = False
            #print('cant attack with', c.instance_id, file=sys.stderr)
    if mana == 0:
        pick = 0
        for n in (1,2):
          if 'G' in cards[n].keywords and cards[n].type == MINION:
            pick = n
            break
        print('PICK', pick)
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
            for c in cards:
                if c.location == BOARD:
                    on_board.append(c)
                elif c.location == FOE:
                    foes.append(c)
            for c in cards:
                if c.location == HAND and c.cost <= mana and c.type == MINION:
                    actions.append('SUMMON ' + str(c.instance_id) + ' ' + str(n%2))
                    mana -= c.cost
                    c.location = BOARD
                    c.can_attack = 'C' in c.keywords
                    summoned_this_turn.append(c)
                elif c.location == BOARD and c.can_attack:
                    targ = -1
                    for enemy in cards:
                        if enemy.location == FOE and enemy.lane == c.lane:
                            if 'G' in enemy.keywords:
                              targ = enemy.instance_id
                              break
                    actions.append('ATTACK ' + str(c.instance_id) + ' ' + str(targ))
                    attacked_this_turn.append(c)
                    c.can_attack = False
                elif c.location == HAND and c.cost <= mana and c.type == GREEN and len(on_board) > 0 and not items_used_this_turn:
                    actions.append('USE ' + str(c.instance_id) + ' ' + str(on_board[0].instance_id))
                    items_used_this_turn.append(c)
                    mana -= c.cost
                    cards.remove(c)
                elif c.location == HAND and c.cost <= mana and c.type == RED and len(foes) > 0 and not items_used_this_turn:
                    actions.append('USE ' + str(c.instance_id) + ' ' + str(foes[0].instance_id))
                    items_used_this_turn.append(c)
                    mana -= c.cost
                    cards.remove(c)
                elif c.location == HAND and c.cost <= mana and c.type == BLUE and not items_used_this_turn:
                    actions.append('USE ' + str(c.instance_id) + ' -1')
                    items_used_this_turn.append(c)
                    mana -= c.cost
                    cards.remove(c)
                else:
                    stop = True
        if actions:
            pass
            print(';'.join(actions))
        else:
            print("PASS")
    turn += 1
# ------------------------------------------------------------
# ------------------------------------------------------------
# UJIAgent1
# This is our first agent for the CEC2019 LOCM competition
# Authors: A. Barbosa, D. Villabrille, S. Ferreras, A. Juan, D. Delgado, R. Montoliu
# Institute of New Imaging Technologies. Jaume I University. Castellon. SPAIN
# Corresponging email: montoliu@uji.es
# ------------------------------------------------------------
# ------------------------------------------------------------
import random
import sys
import numpy as np


# ------------------------------------------------------------
# Player information
# ------------------------------------------------------------
class Player:
    def __init__(self, hp, mana, cards_remaining, rune, draw):
        self.hp = hp
        self.mana = mana
        self.cards_remaining = cards_remaining  # the number of cards in the player's deck
        self.rune = rune                        # the next remaining rune of a player
        self.draw = draw                        # the additional number of drawn cards


# ------------------------------------------------------------
# Card information
# ------------------------------------------------------------
class Card:
    def __init__(self, card_id, instance_id, location, card_type, cost, attack, defense, abilities, my_health_change, opponent_health_change, card_draw, lane):
        self.card_id = card_id
        self.instance_id = instance_id
        self.location = location
        self.card_type = card_type
        self.cost = cost
        self.attack = attack
        self.defense = defense
        self.abilities = abilities
        self.my_health_change = my_health_change
        self.opponent_health_change = opponent_health_change
        self.card_draw = card_draw
        self.lane = lane
        self.breakthrough = False
        self.charge = False
        self.drain = False
        self.guard = False
        self.lethal = False
        self.ward = False
        for c in abilities:
            if c == 'B': self.breakthrough = True
            if c == 'C': self.charge = True
            if c == 'D': self.drain = True
            if c == 'G': self.guard = True
            if c == 'L': self.lethal = True
            if c == 'W': self.ward = True


# ------------------------------------------------------------
# State information
# ------------------------------------------------------------
class State:
    def __init__(self, player1, player2, opponent_hand, l_opponent_actions, l_cards):
        self.player1 = player1
        self.player2 = player2
        self.opponent_hand = opponent_hand
        self.l_opponent_actions = l_opponent_actions
        self.l_cards = l_cards

        self.LOCATION_IN_HAND = 0
        self.LOCATION_PLAYER_SIDE = 1
        self.LOCATION_OPPONENT_SIDE = -1

        self.LANE_LEFT = 1
        self.LANE_RIGHT = 0

        self.TYPE_CREATURE = 0
        self.TYPE_GREEN = 1
        self.TYPE_RED = 2
        self.TYPE_BLUE = 3

        self.l_actions = []
        self.l_cards_on_player_hand = []         # list of cards on player hand
        self.l_cards_on_left_lane_player = []    # list of cards on the left side of the player board
        self.l_cards_on_left_lane_opponent = []  # list of cards on the left side of the opponent board
        self.l_cards_on_right_lane_player = []   # list of cards on the right side of the player board
        self.l_cards_on_right_lane_opponent = [] # list of cards on the right side of the opponent board

        self.l_turn = []
        self.l_cards_can_attack = []
        self.l_cards_on_player_board = []
        self.l_cards_on_opponent_board = []
        self.l_left_opponent_cards_guard = []
        self.l_right_opponent_cards_guard = []
        self.l_left_player_cards_guard = []
        self.l_right_player_cards_guard = []

        if not self.is_draft_phase():
            self.classify_cards()

            # DEBUG
            #print("l_cards_on_player_hand: " + str(len(self.l_cards_on_player_hand)), file=sys.stderr)
            #print("l_cards_on_player_board: " + str(len(self.l_cards_on_player_board)), file=sys.stderr)
            #print("l_cards_on_left_lane_player: " + str(len(self.l_cards_on_left_lane_player)), file=sys.stderr)
            #print("l_cards_on_left_lane_opponent: " + str(len(self.l_cards_on_left_lane_opponent)), file=sys.stderr)
            #print("l_cards_on_right_lane_player: " + str(len(self.l_cards_on_right_lane_player)), file=sys.stderr)
            #print("l_cards_on_right_lane_opponent: " + str(len(self.l_cards_on_right_lane_opponent)), file=sys.stderr)
            #print("l_left_player_cards_guard: " + str(len(self.l_left_player_cards_guard)), file=sys.stderr)
            #print("l_right_player_cards_guard: " + str(len(self.l_right_player_cards_guard)), file=sys.stderr)
            #print("l_actions: " + str(len(self.l_actions)), file=sys.stderr)
            #print(self.l_actions, file=sys.stderr)


    # ---------------------------------------
    # Classify each card in the corresponding list (only if cost <= player mana)
    # Can attack cards on the players lane (already summoned)
    # Can be summoned criatures on the hand
    # Can be used items on the hand
    def classify_cards(self):
        for c in self.l_cards:
            if c.location == self.LOCATION_IN_HAND:
                self.l_cards_on_player_hand.append(c)
            elif c.location == self.LOCATION_PLAYER_SIDE and c.lane == self.LANE_LEFT:
                self.l_cards_on_left_lane_player.append(c)
                self.l_cards_can_attack.append(c)
                self.l_cards_on_player_board.append(c)
                if c.guard:
                    self.l_left_player_cards_guard.append(c)
            elif c.location == self.LOCATION_OPPONENT_SIDE and c.lane == self.LANE_LEFT:
                self.l_cards_on_left_lane_opponent.append(c)
                self.l_cards_on_opponent_board.append(c)
                if c.guard:
                    self.l_left_opponent_cards_guard.append(c)
            elif c.location == self.LOCATION_PLAYER_SIDE and c.lane == self.LANE_RIGHT:
                self.l_cards_on_right_lane_player.append(c)
                self.l_cards_can_attack.append(c)
                self.l_cards_on_player_board.append(c)
                if c.guard:
                    self.l_right_player_cards_guard.append(c)
            elif c.location == self.LOCATION_OPPONENT_SIDE and c.lane == self.LANE_RIGHT:
                self.l_cards_on_right_lane_opponent.append(c)
                self.l_cards_on_opponent_board.append(c)
                if c.guard:
                    self.l_right_opponent_cards_guard.append(c)

    # ---------------------------------------
    # return true is the game is in the draft phase
    def is_draft_phase(self):
        return self.player1.mana == 0

    # ---------------------------------------
    #TODO hay que cambiar muchas cosas
    def get_turn(self):
        # for all cards on player hands
        l_turn = []
        self.l_cards_on_player_hand = self.summon()
        self.attack()
        if len(self.l_cards_on_player_hand) > 0:
            self.summon()
            self.attack()
        #for c in self.l_cards_on_right_lane_player:
        #    print(str(c.instance_id), file=sys.stderr)

    def summon(self):
        self.l_cards_on_player_hand.sort(key=lambda x: x.cost, reverse=True)
        l_cards_can_summon_after = []
        while len(self.l_cards_on_player_hand) > 0:
            c = self.l_cards_on_player_hand[0]
            if(self.card_is_not_usable(c, l_cards_can_summon_after)):
                continue
            else:
                if c.card_type == self.TYPE_CREATURE:
                    self.summon_card(c)

                elif c.card_type == self.TYPE_GREEN:
                    self.use_green_card(c)

                elif c.card_type == self.TYPE_RED:
                    self.use_red_card(c)

                else:
                    self.use_blue_card(c)

                self.player1.mana -= c.cost
                self.l_cards_on_player_hand.remove(c)

        return l_cards_can_summon_after

    def attack(self):
        if self.possible_win():
            for c in self.l_cards_can_attack:
                self.attack_order(c, -1)
        else:
            while len(self.l_cards_can_attack) > 0:
                c = self.l_cards_can_attack[0]
                self.l_cards_can_attack.remove(c)
                if c.attack == 0:
                    continue
                self.checking_lane_and_stats(c)


    def other_can_kill(self, my_card, enemy_card):
        if my_card.attack >= enemy_card.defense:
            return False
        if my_card.lane == self.LANE_LEFT:
            for c in self.l_cards_on_left_lane_player:
                if(c == my_card):
                    continue
                elif(c.attack >= enemy_card.defense):
                    return True
            return False
        else:
            for c in self.l_cards_on_right_lane_player:
                if(c == my_card):
                    continue
                elif(c.attack >= enemy_card.defense):
                    return True
            return False

    def possible_win(self):
        n = 0
        if len(self.l_left_opponent_cards_guard) == 0:
            for c in self.l_cards_can_attack:
                if c.lane == self.LANE_LEFT:
                    n += c.attack

        if len(self.l_right_opponent_cards_guard) == 0:
            for c in self.l_cards_can_attack:
                if c.lane == self.LANE_RIGHT:
                    n += c.attack
        if n >= self.player2.hp:
            return True
        return False

    def card_is_not_usable(self, c, l_cards_can_summon_after):
        if c.cost > self.player1.mana:
            self.l_cards_on_player_hand.remove(c)
            return True
        elif c.card_type == self.TYPE_CREATURE and len(self.l_cards_on_left_lane_player) >= 3 and len(self.l_cards_on_right_lane_player) >= 3:
            l_cards_can_summon_after.append(c)
            self.l_cards_on_player_hand.remove(c)
            return True
        elif c.card_type == self.TYPE_GREEN and len(self.l_cards_on_left_lane_player) == 0 and len(self.l_cards_on_right_lane_player) == 0:
            l_cards_can_summon_after.append(c)
            self.l_cards_on_player_hand.remove(c)
            return True
        elif c.card_type == self.TYPE_RED and len(self.l_cards_on_left_lane_opponent) == 0 and len(self.l_cards_on_right_lane_opponent) == 0:
            self.l_cards_on_player_hand.remove(c)
            return True
        return False

    def summon_card(self, c):
        if len(self.l_cards_on_left_lane_player) == 3:
            self.summon_card_order(c, self.LANE_RIGHT)
        elif len(self.l_cards_on_right_lane_player) == 3:
             self.summon_card_order(c, self.LANE_LEFT)
        elif c.guard:
            if len(self.l_left_player_cards_guard) < len(self.l_right_player_cards_guard):
                self.summon_card_order(c, self.LANE_LEFT)
            elif len(self.l_left_player_cards_guard) > len(self.l_right_player_cards_guard):
                self.summon_card_order(c, self.LANE_RIGHT)
            else:
                self.checking_where_summon(c)
        else:
            self.checking_where_summon(c)

    def use_green_card(self, c):
        r = random.randint(0,  len(self.l_cards_on_player_board) - 1)
        if c.guard:
            if self.l_cards_on_player_board[r].lane == self.LANE_LEFT and c not in self.l_left_player_cards_guard:
                self.l_left_player_cards_guard.append(c)
            elif self.l_cards_on_player_board[r].lane == self.LANE_RIGHT and c not in self.l_right_player_cards_guard:
                self.l_right_player_cards_guard.append(c)
        self.use_item_order(c, self.l_cards_on_player_board[r])

    def use_red_card(self, c):
        enemy_index = self.evaluate_enemy_cards()
        enemy_card = self.l_cards_on_opponent_board[enemy_index]
        self.use_item_order(c,enemy_card)
        #print("red_card_defense: " + str(c.defense), file=sys.stderr)
        enemy_card.defense += c.defense
        enemy_card.attack += c.attack
        if enemy_card.defense <= 0:
            self.delete_card(enemy_card)

    def use_blue_card(self, c):
        if (c.defense < 0) and (len(self.l_cards_on_opponent_board) > 0):
            r = random.randint(0, len(self.l_cards_on_opponent_board) - 1)
            self.use_item_order(c, self.l_cards_on_opponent_board[r])
            self.l_cards_on_opponent_board[r].defense -= c.defense
            if self.l_cards_on_opponent_board[r].defense <= 0:
                self.delete_card(self.l_cards_on_opponent_board[r])
        else:
            self.use_item_order(c, -1)

    def checking_lane_and_stats(self, c):
        if c.lane == self.LANE_LEFT:
            enemy_guards = self.l_left_opponent_cards_guard
            enemy_cards = self.l_cards_on_left_lane_opponent
        else:
            enemy_guards = self.l_right_opponent_cards_guard
            enemy_cards = self.l_cards_on_right_lane_opponent

        if len(enemy_guards) > 0:
            if not c.ward or not c.guard:
                r = random.randint(0, len(enemy_guards)-1)
                if(self.other_can_kill(c, enemy_guards[r])):
                    return
                self.attacking_card(c, enemy_guards[r])

        else:
            if not c.ward or not c.guard:
                if(len(enemy_cards) > 0):
                    r = random.randint(0, len(enemy_cards)-1)
                    if self.other_can_kill(c, enemy_cards[r]):
                        self.attack_order(c, -1)
                    else:
                        self.attacking_card(c, enemy_cards[r])
                else:
                    self.attack_order(c, -1)
            else:
                self.attack_order(c, -1)

    def attacking_card(self, my_card, enemy_card,):
        self.attack_order(my_card, enemy_card)
        if my_card.ward:
            enemy_card.ward = False
        elif my_card.lethal:
            enemy_card.defense = 0
        else:
            enemy_card.defense -= my_card.attack
        my_card.defense -= enemy_card.attack
        if enemy_card.defense <= 0:
            self.delete_card(enemy_card)
        if my_card.defense <= 0:
            self.delete_card(my_card)
        elif my_card.ward == False and enemy_card.lethal:
            self.delete_card(my_card)

    def delete_card(self, c):
        if c.location == self.LOCATION_OPPONENT_SIDE:
            if c.lane == self.LANE_LEFT:
                self.l_cards_on_left_lane_opponent.remove(c)
                if c in self.l_left_opponent_cards_guard:
                    self.l_left_opponent_cards_guard.remove(c)
            else:
                self.l_cards_on_right_lane_opponent.remove(c)
                if c in self.l_right_opponent_cards_guard:
                    self.l_right_opponent_cards_guard.remove(c)
            self.l_cards_on_opponent_board.remove(c)
        else:
            if c.lane == self.LANE_LEFT:
                self.l_cards_on_left_lane_player.remove(c)
                if c.guard:
                    self.l_left_player_cards_guard.remove(c)
            else:
                self.l_cards_on_right_lane_player.remove(c)
                if c.guard:
                    self.l_right_player_cards_guard.remove(c)

    def attack_order(self, my_card, target):
        if target == -1:
            self.l_turn.append("ATTACK " + str(my_card.instance_id) + " -1;")
        else:
            self.l_turn.append("ATTACK " + str(my_card.instance_id) + " " + str(target.instance_id) + ";")

    def use_item_order(self, c, target):
        if(target == -1):
            self.l_turn.append("USE " + str(c.instance_id) + " -1;")
        else:
            self.l_turn.append("USE " + str(c.instance_id) + " " + str(target.instance_id) + ";")

    def summon_card_order(self,c,lane):
        if(lane == self.LANE_RIGHT):
            self.l_turn.append("SUMMON " + str(c.instance_id) + " "+ str(self.LANE_RIGHT) + ";")
            self.l_cards_on_right_lane_player.append(c)
            c.lane = self.LANE_RIGHT
            if c.guard:
                self.l_right_player_cards_guard.append(c)
        else:
            self.l_turn.append("SUMMON " + str(c.instance_id) + " "+ str(self.LANE_LEFT) + ";")
            self.l_cards_on_left_lane_player.append(c)
            c.lane = self.LANE_LEFT
            if c.guard:
                self.l_left_player_cards_guard.append(c)
        if(c.charge):
            self.l_cards_can_attack.append(c)
        self.l_cards_on_player_board.append(c)

    def checking_where_summon(self, c):
        if len(self.l_cards_on_right_lane_opponent) > len(self.l_cards_on_left_lane_opponent):
            self.summon_card_order(c, self.LANE_RIGHT)
        elif len(self.l_cards_on_right_lane_opponent) < len(self.l_cards_on_left_lane_opponent):
            self.summon_card_order(c, self.LANE_LEFT)
        else:
            if len(self.l_cards_on_left_lane_player) <= len(self.l_cards_on_right_lane_player):
                self.summon_card_order(c, self.LANE_LEFT)
            else:
                self.summon_card_order(c, self.LANE_RIGHT)

    def evaluate_enemy_cards(self):
        maxScore = 0
        for i in range(0, len(self.l_cards_on_opponent_board)):
            c = self.l_cards_on_opponent_board[i]
            n = c.attack + c.defense
            for s in c.abilities:
                if s == 'B': n += 1
                if s == 'C': n += 1
                if s == 'D': n += 1
                if s == 'G': n += 1
                if s == 'L': n += 1
                if s == 'W': n += 1
            if n > maxScore:
                maxScore = n
                card = i
        return card

# ------------------------------------------------------------
# Agent
# ------------------------------------------------------------
class UJIAgent1():
    def __init__(self):
        self.state = None
        self.draft = Draft()
        self.LOCATION_IN_HAND = 0
        self.LOCATION_PLAYER_SIDE = 1
        self.LOCATION_OPPONENT_SIDE = -1

        self.LANE_LEFT = 1
        self.LANE_RIGHT = 0

        self.TYPE_CREATURE = 0
        self.TYPE_GREEN = 1
        self.TYPE_RED = 2
        self.TYPE_BLUE = 3
        self.turn = []

    # ------------------------------------------------------------
    # read the input and fill corresponfing classes
    # ------------------------------------------------------------
    def read_input(self):
        player_health1, player_mana1, player_deck1, player_rune1, player_draw1 = [int(j) for j in input().split()]
        player_health2, player_mana2, player_deck2, player_rune2, player_draw2 = [int(j) for j in input().split()]

        opponent_hand, opponent_actions = [int(i) for i in input().split()]
        l_opponent_actions = []
        for i in range(opponent_actions):
            card_number_and_action = input()
            l_opponent_actions.append(card_number_and_action)

        card_count = int(input())
        l_cards = []
        for i in range(card_count):
            card_number, instance_id, location, card_type, cost, attack, defense, abilities, my_health_change, opponent_health_change, card_draw, lane = input().split()
            one_card = Card(int(card_number), int(instance_id), int(location), int(card_type), int(cost), int(attack),
                        int(defense), abilities, (my_health_change), int(opponent_health_change), int(card_draw), int(lane))

            l_cards.append(one_card)

        player1 = Player(player_health1, player_mana1, player_deck1, player_rune1, player_draw1)
        player2 = Player(player_health2, player_mana2, player_deck2, player_rune2, player_draw2)
        self.state = State(player1, player2, opponent_hand, l_opponent_actions, l_cards)

    # ----------------------------------------------
    # Select best action to do depending on the phase
    # ----------------------------------------------
    def act(self):
        if self.state.is_draft_phase():
            best_card = self.draft.pick_card(self.state.l_cards)
            print("PICK " + str(best_card))

        else:
            self.turn = self.state.get_turn()
            self.ia_battle()
         
    # ----------------------------------------------
    # Randomly select the action
    # ----------------------------------------------
    def ia_battle(self):
        if len(self.state.l_turn) == 0:
            print("PASS")
        else:
            #TODO hay que construir la cadena con todas las acciones que se hayan elegido
            turn_string = ""
            for action in self.state.l_turn:
                turn_string += action
            #coin = random.randint(0, len(self.state.l_actions) - 1)
            print(turn_string)   

# ------------------------------------------------------------
# Draft class
# ------------------------------------------------------------
class Draft:
    def __init__(self):
        self.l_all_cards_picked = []
        self.picked_card_type = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.prefer_card_type = [5, 5, 3, 3, 3, 4, 4, 3, 0, 0]

        self.TYPE_CREATURE = 0
        self.TYPE_GREEN = 1
        self.TYPE_RED = 2
        self.TYPE_BLUE = 3

    def pick_card(self, cards):
        best_card = self.select_bestcard(cards)
        if cards[best_card].card_type == self.TYPE_CREATURE and cards[best_card].cost < 2:
            self.picked_card_type[0] += 1
        elif cards[best_card].card_type == self.TYPE_CREATURE and cards[best_card].cost < 3:
            self.picked_card_type[1] += 1
        elif cards[best_card].card_type == self.TYPE_CREATURE and cards[best_card].cost < 4:
            self.picked_card_type[2] += 1
        elif cards[best_card].card_type == self.TYPE_CREATURE and cards[best_card].cost < 5:
            self.picked_card_type[3] += 1
        elif cards[best_card].card_type == self.TYPE_CREATURE and cards[best_card].cost < 6:
            self.picked_card_type[4] += 1
        elif cards[best_card].card_type == self.TYPE_CREATURE and cards[best_card].cost < 7:
            self.picked_card_type[5] += 1
        elif cards[best_card].card_type == self.TYPE_CREATURE:
            self.picked_card_type[6] += 1
        elif cards[best_card].card_type == self.TYPE_RED:
            self.picked_card_type[7] += 1
        elif cards[best_card].card_type == self.TYPE_GREEN:
            self.picked_card_type[8] += 1
        else:
            self.picked_card_type[9] += 1

        self.l_all_cards_picked.append(cards[best_card])
        return best_card

    def select_bestcard(self, cards):
        n = 0

        l_percent = []
        for c in cards:
            p = 0
            if c.card_id == 151:
                p = 100
            elif c.card_type == self.TYPE_CREATURE and c.cost < 2:
                p = (self.prefer_card_type[0] - self.picked_card_type[0])
            elif c.card_type == self.TYPE_CREATURE and c.cost < 3:
                p = (self.prefer_card_type[1] - self.picked_card_type[1])
            elif c.card_type == self.TYPE_CREATURE and c.cost < 4:
                p = (self.prefer_card_type[2] - self.picked_card_type[2])
            elif c.card_type == self.TYPE_CREATURE and c.cost < 5:
                p = (self.prefer_card_type[3] - self.picked_card_type[3])
            elif c.card_type == self.TYPE_CREATURE and c.cost < 6:
                p = (self.prefer_card_type[4] - self.picked_card_type[4])
            elif c.card_type == self.TYPE_CREATURE and c.cost < 7:
                p = (self.prefer_card_type[5] - self.picked_card_type[5])
            elif c.card_type == self.TYPE_CREATURE:
                p = (self.prefer_card_type[6] - self.picked_card_type[6])
            elif c.card_type == self.TYPE_RED:
                p = (self.prefer_card_type[7] - self.picked_card_type[6])
            else:
                p = -100
            if c.card_type == 0 and c.guard:
                p += 6
            l_percent.append(p)

        if l_percent[0] >= l_percent[1] and l_percent[0] >= l_percent[2]:
            n = 0
        elif l_percent[1] >= l_percent[0] and l_percent[1] >= l_percent[2]:
            n = 1
        else:
            n = 2

        #print(str(l_percent[0]) + ", " + str(l_percent[1]) + ", " + str(l_percent[2]) + " = " + " = " + str(n), file=sys.stderr)
        return n


# ----------------------------------------------
# ----------------------------------------------
# ----------------------------------------------
# Always pick the first card
if __name__ == '__main__':
    agent = UJIAgent1()
    while True:
        agent.read_input()
        agent.act()

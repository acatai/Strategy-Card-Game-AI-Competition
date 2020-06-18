# ------------------------------------------------------------
# ------------------------------------------------------------
# UJIAgent3
# This is our agent for the COG019 LOCM competition
# Authors: R. Montoliu, D. Delgado, A. Barbosa, D. Villabrille, S. Ferreras, A. Juan
# Institute of New Imaging Technologies. Jaume I University. Castellon. SPAIN
# Corresponging email: montoliu@uji.es
# ------------------------------------------------------------
# ------------------------------------------------------------
import random
import copy
import sys
import time


# ------------------------------------------------------------
# Player information
# ------------------------------------------------------------
class PlayerAgent:
    def __init__(self, hp, mana, cards_remaining, rune, draw):
        self.hp = hp                            # Number of health points
        self.mana = mana                        # Current mana
        self.cards_remaining = cards_remaining  # The number of cards in the player's deck
        self.rune = rune                        # The next remaining rune of a player
        self.draw = draw                        # The additional number of drawn cards


# ------------------------------------------------------------
# Card information
# ------------------------------------------------------------
class CardAgent:
    def __init__(self, card_id, instance_id, location, card_type, cost,
                 attack, defense, abilities,
                 my_health_change, opponent_health_change, card_draw, lane):
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
        self.can_attack = False

        for c in abilities:
            if c == 'B':
                self.breakthrough = True
            elif c == 'C':
                self.charge = True
            elif c == 'D':
                self.drain = True
            elif c == 'G':
                self.guard = True
            elif c == 'L':
                self.lethal = True
            elif c == 'W':
                self.ward = True


# ------------------------------------------------------------
# State information
# ------------------------------------------------------------
class StateAgent:
    def __init__(self, player1, player2, l_cards):
        self.l_cards_draft = []              # List of card for draft
        self.l_cards_on_hand = []            # List of card on the player hand
        self.l_cards_on_player_left = []     # List of card on the player left side of th board
        self.l_cards_on_player_right = []    # List of card on the player right side of th board
        self.l_cards_on_opponent_left = []   # List of card on the opponent left side of th board
        self.l_cards_on_opponent_right = []  # List of card on the opponent right side of th board

        self.player1 = player1
        self.player2 = player2

        if self.player1.mana == 0:
            self.draft_phase = True
        else:
            self.draft_phase = False

        self.LEFT_LANE = 1
        self.RIGHT_LANE = 0
        self.HAND = 0
        self.PLAYER_SIDE = 1
        self.OPPONENT_SIDE = -1

        self.CARD_TYPE_CREATURE = 0
        self.CARD_TYPE_GREEN = 1
        self.CARD_TYPE_RED = 2
        self.CARD_TYPE_BLUE = 3

        self.classify_cards(l_cards)

    # ----------------------------------------
    # Print the state of the game in the file f
    # For instance, in codingame can be called state.print_state(f=sys.stderr)
    # ----------------------------------------
    def print_state(self, f):
        if self.is_draft():
            print("CARDS FOR DRAFT: ", file=f, end="")
            for card in self.l_cards_draft:
                print(str(card.card_id) + " ", file=f, end="")
        else:
            print("P1: " + str(self.player1.hp) + " " + str(self.player1.mana), file=f)
            print("P2: " + str(self.player2.hp) + " " + str(self.player2.mana), file=f)

            print("CARDS ON HAND: ", file=f, end="")
            for card in self.l_cards_on_hand:
                print(str(card.instance_id) + " ", file=f, end="")
            print("\n", file=f)

            print("CARDS ON P1 L: ", file=f, end="")
            for card in self.l_cards_on_player_left:
                print(str(card.instance_id) + " ", file=f, end="")
            print("\n", file=f)

            print("CARDS ON P1 R: ", file=f, end="")
            for card in self.l_cards_on_player_right:
                print(str(card.instance_id) + " ", file=f, end="")
            print("\n", file=f)

            print("CARDS ON P2 L: ", file=f, end="")
            for card in self.l_cards_on_opponent_left:
                print(str(card.instance_id) + " ", file=f, end="")
            print("\n", file=f)

            print("CARDS ON P2 L: ", file=f, end="")
            for card in self.l_cards_on_opponent_right:
                print(str(card.instance_id) + " ", file=f, end="")
            print("\n", file=f)

    # ----------------------------------------
    # Classify cards in the corresponing lists
    # ----------------------------------------
    def classify_cards(self, l_cards):
        if self.is_draft():                      # draft
            for card in l_cards:
                self.l_cards_draft.append(card)
        else:                                    # battle
            for card in l_cards:
                if card.location == self.HAND:
                    self.l_cards_on_hand.append(card)
                    card.can_attack = False

                elif card.location == self.PLAYER_SIDE:
                    card.can_attack = True
                    if card.lane == self.LEFT_LANE:
                        self.l_cards_on_player_left.append(card)
                    else:
                        self.l_cards_on_player_right.append(card)

                else:
                    if card.lane == self.LEFT_LANE:
                        self.l_cards_on_opponent_left.append(card)
                    else:
                        self.l_cards_on_opponent_right.append(card)

    # ----------------------------------------
    # Return a list with all the possible actions that can be played given a state of the game
    # Note that not all the actions in the list can be played.
    # It is the objective of the agent to learn which is the correct order to play the actions.
    # ----------------------------------------
    def get_list_all_possible_actions(self):
        l_actions = []
        l_has_charge = []
        l_card_can_be_summoned = []

        # SUMMON
        for card in self.l_cards_on_hand:
            if card.cost <= self.player1.mana:
                if card.card_type == self.CARD_TYPE_CREATURE:
                    # Summon in each lane
                    l_actions.append("SUMMON " + str(card.instance_id) + " " + str(self.LEFT_LANE))
                    l_actions.append("SUMMON " + str(card.instance_id) + " " + str(self.RIGHT_LANE))
                    l_card_can_be_summoned.append(card)

                    if card.charge:
                        l_has_charge.append(card)

        # USE
        for card in self.l_cards_on_hand:
            if card.cost <= self.player1.mana:
                if card.card_type == self.CARD_TYPE_RED:
                    # Use on any card on opponent's lanes
                    for opponent_card in self.l_cards_on_opponent_left:
                        l_actions.append("USE " + str(card.instance_id) + " " + str(opponent_card.instance_id))
                    for opponent_card in self.l_cards_on_opponent_right:
                        l_actions.append("USE " + str(card.instance_id) + " " + str(opponent_card.instance_id))

                elif card.card_type == self.CARD_TYPE_GREEN:
                    # Use on any card on player's lanes
                    for player_card in self.l_cards_on_player_left:
                        l_actions.append("USE " + str(card.instance_id) + " " + str(player_card.instance_id))
                    for player_card in self.l_cards_on_player_right:
                        l_actions.append("USE " + str(card.instance_id) + " " + str(player_card.instance_id))

                    # green items can be used on just summoned cards
                    for card_can_be_summoned in l_card_can_be_summoned:
                        if card.cost + card_can_be_summoned.cost <= self.player1.mana:
                            l_actions.append("USE " + str(card.instance_id) + " "
                                                    + str(card_can_be_summoned.instance_id))

                elif card.card_type == self.CARD_TYPE_BLUE:
                    # Use on player/opponent or on any opponent's card (if defense < 0)
                    l_actions.append("USE " + str(card.instance_id) + " -1")
                    if card.defense < 0:
                        for opponent_card in self.l_cards_on_opponent_left:
                            l_actions.append("USE " + str(card.instance_id) + " " + str(opponent_card.instance_id))
                        for opponent_card in self.l_cards_on_opponent_right:
                            l_actions.append("USE " + str(card.instance_id) + " " + str(opponent_card.instance_id))

        # ATTACK
        # Attack to any card on opponent's lane and directly to the opponent
        # Some hueristics:
        # 1. No attack if the card has 0 attack points
        # 2. if lethal, attack only to best card of the opponent (greather defense points)
        # 3. If lethal, is the best opponent card is less than 4 defense points, then only attack to the opponent
        # 4. Guard: always atack to the opponent

        # ATTACK LEFT
        for card in self.l_cards_on_player_left:
            if card.attack <= 0:
                continue

            if card.lethal:
                best_opponent_card = None
                best = 0
                for opponent_card in self.l_cards_on_opponent_left:
                    if opponent_card.defense > best:
                        best_opponent_card = opponent_card
                        best = opponent_card.defense
                if best >= 4:
                    l_actions.append("ATTACK " + str(card.instance_id) + " " + str(best_opponent_card.instance_id))
                else:
                    l_actions.append("ATTACK " + str(card.instance_id) + " -1")
                continue

            if card.guard:
                l_actions.append("ATTACK " + str(card.instance_id) + " -1")
                continue

            # normal cards
            l_actions.append("ATTACK " + str(card.instance_id) + " -1")
            for opponent_card in self.l_cards_on_opponent_left:
                l_actions.append("ATTACK " + str(card.instance_id) + " " + str(opponent_card.instance_id))

        # ATTACK RIGHT
        for card in self.l_cards_on_player_right:
            if card.attack <= 0:
                continue

            if card.lethal:
                best_opponent_card = None
                best = 0
                for opponent_card in self.l_cards_on_opponent_left:
                    if opponent_card.defense > best:
                        best_opponent_card = opponent_card
                        best = opponent_card.defense
                if best >= 4:
                    l_actions.append("ATTACK " + str(card.instance_id) + " " + str(best_opponent_card.instance_id))
                else:
                    l_actions.append("ATTACK " + str(card.instance_id) + " -1")
                continue

            if card.guard:
                l_actions.append("ATTACK " + str(card.instance_id) + " -1")
                continue

            # normal cards
            l_actions.append("ATTACK " + str(card.instance_id) + " -1")
            for opponent_card in self.l_cards_on_opponent_right:
                l_actions.append("ATTACK " + str(card.instance_id) + " " + str(opponent_card.instance_id))

        # CARDS with charge
        for card in l_has_charge:
            if card.attack <= 0:
                continue

            if card.lethal:
                best_opponent_card = None
                best = 0
                for opponent_card in self.l_cards_on_opponent_left:
                    if opponent_card.defense > best:
                        best_opponent_card = opponent_card
                        best = opponent_card.defense
                if best >= 4:
                    l_actions.append("ATTACK " + str(card.instance_id) + " " + str(best_opponent_card.instance_id))
                else:
                    l_actions.append("ATTACK " + str(card.instance_id) + " -1")
                continue

            # normal cards
            if card.guard:
                l_actions.append("ATTACK " + str(card.instance_id) + " -1")
                continue

            l_actions.append("ATTACK " + str(card.instance_id) + " -1")

            for opponent_card in self.l_cards_on_opponent_left:
                l_actions.append("ATTACK " + str(card.instance_id) + " " + str(opponent_card.instance_id))

            for opponent_card in self.l_cards_on_opponent_right:
                l_actions.append("ATTACK " + str(card.instance_id) + " " + str(opponent_card.instance_id))

        return l_actions

    # ----------------------------------------
    # Return true if it is a draft state
    # ----------------------------------------
    def is_draft(self):
        return self.draft_phase

    # ----------------------------------------
    # Evaluate a turn
    # Return the score and the actions played (no valid ones are not included)
    # ----------------------------------------
    def evaluate(self, l_actions):
        new_state = copy.deepcopy(self)
        l_clean_actions = []
        for action in l_actions:
            ok = new_state.perform_atomic_action(action)
            if ok:
                l_clean_actions.append(action)

        if self.player1.hp <= 0:
            score = -100
        elif self.player2.hp <= 0:
            score = 100
        else:
            hp_pl_t = self.player1.hp
            hp_pl_t1 = new_state.player1.hp
            hp_pl_t2 = hp_pl_t1 - new_state.get_possible_damage()

            hp_op_t = self.player2.hp
            hp_op_t1 = new_state.player2.hp

            alpha = hp_op_t - hp_op_t1
            beta = hp_pl_t - hp_pl_t2
            score = alpha - beta

        return score, l_clean_actions

    # --------------------------------
    # Get possible attacking damage that the player can do in the next turn
    # --------------------------------
    def get_possible_attacking_damage(self):
        attack_power_l = 0
        attack_power_r = 0

        l_guard_l = []
        l_guard_r = []

        for card in self.l_cards_on_opponent_left:
            if card.guard:
                l_guard_l.append(card)

        for card in self.l_cards_on_opponent_right:
            if card.guard:
                l_guard_r.append(card)

        if len(l_guard_l) == 0:
            for card in self.l_cards_on_player_left:
                attack_power_l += card.attack
        else:
            attack_power_l = self.estimate_max_attacking_power(self.l_cards_on_player_left, l_guard_l)

        if len(l_guard_r) == 0:
            for card in self.l_cards_on_player_right:
                attack_power_r += card.attack
        else:
            attack_power_r = self.estimate_max_attacking_power(self.l_cards_on_player_right, l_guard_r)

        return attack_power_l + attack_power_r

    # --------------------------------
    # Max damage that the player can receive
    # --------------------------------
    def get_possible_damage(self):
        attack_power_opponent_l = 0
        attack_power_opponent_r = 0

        l_guard_l = []
        l_guard_r = []

        for card in self.l_cards_on_player_left:
            if card.guard:
                l_guard_l.append(card)

        for card in self.l_cards_on_player_right:
            if card.guard:
                l_guard_r.append(card)

        if len(l_guard_l) == 0:
            for card in self.l_cards_on_opponent_left:
                attack_power_opponent_l += card.attack
        else:
            attack_power_opponent_l = self.estimate_max_attacking_power(self.l_cards_on_opponent_left, l_guard_l)

        if len(l_guard_r) == 0:
            for card in self.l_cards_on_opponent_right:
                attack_power_opponent_r += card.attack
        else:
            attack_power_opponent_r = self.estimate_max_attacking_power(self.l_cards_on_opponent_right, l_guard_r)

        return attack_power_opponent_l + attack_power_opponent_r

    # ----------------------------------------
    # Estimate maximium attacking power
    # ----------------------------------------
    def estimate_max_attacking_power(self, l_attacking_cards, l_defensive_cards_with_guard):
        n_attack = len(l_attacking_cards)
        n_defense = len(l_defensive_cards_with_guard)

        if n_attack <= n_defense:
            attacking_power = 0
        else:
            attacking_power = self.estimate_attacking_power(l_attacking_cards, l_defensive_cards_with_guard)

        return attacking_power

    # ----------------------------------------
    # Estimate attacking power
    # ----------------------------------------
    def estimate_attacking_power(self, l_attacking_cards, l_defensive_cards_with_guard):
        # 2 attacking cards and 1 defensive one with guard
        if len(l_attacking_cards) == 2 and len(l_defensive_cards_with_guard) == 1:
            if l_attacking_cards[0].lethal or l_defensive_cards_with_guard[0].defense <= l_attacking_cards[0].attack:
                return l_attacking_cards[1].attack
            elif l_attacking_cards[1].lethal or l_defensive_cards_with_guard[0].defense <= l_attacking_cards[1].attack:
                return l_attacking_cards[0].attack
            else:
                return 0

        # 3 attacking cards and 1 defensive one with guard
        if len(l_attacking_cards) == 3 and len(l_defensive_cards_with_guard) == 1:
            if l_attacking_cards[0].lethal or l_defensive_cards_with_guard[0].defense <= l_attacking_cards[0].attack:
                return l_attacking_cards[1].attack + l_attacking_cards[2].attack
            elif l_attacking_cards[1].lethal or l_defensive_cards_with_guard[0].defense <= l_attacking_cards[1].attack:
                return l_attacking_cards[0].attack + l_attacking_cards[2].attack
            elif l_attacking_cards[2].lethal or l_defensive_cards_with_guard[0].defense <= l_attacking_cards[2].attack:
                return l_attacking_cards[0].attack + l_attacking_cards[1].attack
            elif l_defensive_cards_with_guard[0].defense <= l_attacking_cards[0].attack + l_attacking_cards[1].attack:
                return l_attacking_cards[2].attack
            elif l_defensive_cards_with_guard[0].defense <= l_attacking_cards[0].attack + l_attacking_cards[2].attack:
                return l_attacking_cards[1].attack
            elif l_defensive_cards_with_guard[0].defense <= l_attacking_cards[1].attack + l_attacking_cards[2].attack:
                return l_attacking_cards[0].attack
            else:
                return 0

        # 3 attacking cards and 2 defensive ones with guard
        if len(l_attacking_cards) == 3 and len(l_defensive_cards_with_guard) == 2:
            # first 2 lethal possibilities
            if l_attacking_cards[0].lethal and l_attacking_cards[1].lethal:
                return l_attacking_cards[2].attack
            elif l_attacking_cards[0].lethal and l_attacking_cards[2].lethal:
                return l_attacking_cards[1].attack
            elif l_attacking_cards[1].lethal and l_attacking_cards[2].lethal:
                return l_attacking_cards[0].attack

            # now just one lethal
            elif l_attacking_cards[0].lethal:
                v1 = 0
                v2 = 0
                if l_defensive_cards_with_guard[1].defense <= l_attacking_cards[1].attack:
                    v1 = l_attacking_cards[2].attack
                elif l_defensive_cards_with_guard[1].defense <= l_attacking_cards[2].attack:
                    v1 = l_attacking_cards[1].attack

                if l_defensive_cards_with_guard[0].defense <= l_attacking_cards[1].attack:
                    v2 = l_attacking_cards[2].attack
                elif l_defensive_cards_with_guard[0].defense <= l_attacking_cards[2].attack:
                    v2 = l_attacking_cards[1].attack

                if v1 > v2:
                    return v1
                else:
                    return v2

            elif l_attacking_cards[1].lethal:
                v1 = 0
                v2 = 0
                if l_defensive_cards_with_guard[1].defense <= l_attacking_cards[0].attack:
                    v1 = l_attacking_cards[2].attack
                elif l_defensive_cards_with_guard[1].defense <= l_attacking_cards[2].attack:
                    v1 = l_attacking_cards[0].attack

                if l_defensive_cards_with_guard[0].defense <= l_attacking_cards[0].attack:
                    v2 = l_attacking_cards[2].attack
                elif l_defensive_cards_with_guard[0].defense <= l_attacking_cards[2].attack:
                    v2 = l_attacking_cards[0].attack

                if v1 > v2:
                    return v1
                else:
                    return v2

            elif l_attacking_cards[2].lethal:
                v1 = 0
                v2 = 0
                if l_defensive_cards_with_guard[1].defense <= l_attacking_cards[0].attack:
                    v1 = l_attacking_cards[1].attack
                elif l_defensive_cards_with_guard[1].defense <= l_attacking_cards[1].attack:
                    v1 = l_attacking_cards[0].attack

                if l_defensive_cards_with_guard[0].defense <= l_attacking_cards[0].attack:
                    v2 = l_attacking_cards[1].attack
                elif l_defensive_cards_with_guard[0].defense <= l_attacking_cards[1].attack:
                    v2 = l_attacking_cards[0].attack

                if v1 > v2:
                    return v1
                else:
                    return v2

            # no lethal cards
            elif l_defensive_cards_with_guard[0].defense <= l_attacking_cards[0].attack and \
                 l_defensive_cards_with_guard[1].defense <= l_attacking_cards[1].attack:
                return l_attacking_cards[2].attack
            elif l_defensive_cards_with_guard[0].defense <= l_attacking_cards[0].attack and \
                 l_defensive_cards_with_guard[1].defense <= l_attacking_cards[2].attack:
                return l_attacking_cards[1].attack
            elif l_defensive_cards_with_guard[1].defense <= l_attacking_cards[0].attack and \
                 l_defensive_cards_with_guard[0].defense <= l_attacking_cards[1].attack:
                return l_attacking_cards[2].attack
            elif l_defensive_cards_with_guard[1].defense <= l_attacking_cards[0].attack and \
                 l_defensive_cards_with_guard[0].defense <= l_attacking_cards[2].attack:
                return l_attacking_cards[1].attack
            elif l_defensive_cards_with_guard[0].defense <= l_attacking_cards[1].attack and \
                 l_defensive_cards_with_guard[1].defense <= l_attacking_cards[2].attack:
                return l_attacking_cards[0].attack
            elif l_defensive_cards_with_guard[1].defense <= l_attacking_cards[1].attack and \
                 l_defensive_cards_with_guard[0].defense <= l_attacking_cards[2].attack:
                return l_attacking_cards[1].attack
            elif l_defensive_cards_with_guard[0].defense <= l_attacking_cards[2].attack and \
                 l_defensive_cards_with_guard[1].defense <= l_attacking_cards[1].attack:
                return l_attacking_cards[0].attack
            elif l_defensive_cards_with_guard[1].defense <= l_attacking_cards[2].attack and \
                 l_defensive_cards_with_guard[0].defense <= l_attacking_cards[1].attack:
                return l_attacking_cards[0].attack
            else:
                return 0

        return 0

    # ----------------------------------------
    # Perform an atomic action
    # ----------------------------------------
    def perform_atomic_action(self, action):
        ok = True
        v_action = action.split(" ")
        if v_action[0] == "SUMMON":
            ok = self.do_summon(v_action)
        elif v_action[0] == "USE":
            ok = self.do_use(v_action)
        elif v_action[0] == "ATTACK":
            ok = self.do_attack(v_action)
        elif v_action[0] == "PASS":
            ok = True
        return ok

    # --------------------------------
    # Perform an atomic summon action
    # Since the card values can change, it is needed a copy of the cards
    # Remember that by default, a card can not attack in the same turn that it has been summoned
    # --------------------------------
    def do_summon(self, v_action):
        instance_id = int(v_action[1])
        lane = int(v_action[2])

        # check if this action is valid
        ok = self.is_valid_summon(instance_id, lane)
        if not ok:
            return False

        card = self.remove_card(self.l_cards_on_hand, instance_id)
        self.player1.mana -= card.cost
        self.player1.hp += card.my_health_change
        self.player2.hp += card.opponent_health_change
        self.player1.draw += card.card_draw
        self.check_charge(card)

        if lane == self.LEFT_LANE:
            self.l_cards_on_player_left.append(copy.copy(card))
        else:
            self.l_cards_on_player_right.append(copy.copy(card))

        return True

    # --------------------------------
    # Return true if the action is a valid summon. False, otherwise
    # 1. there is enough mana
    # 2. The card is a creature
    # 3. The card is the hand of the player
    # 4. There is empty space in the lane
    # --------------------------------
    def is_valid_summon(self, instance_id, lane):
        card = self.look_for_card(self.l_cards_on_hand, instance_id)
        if lane == self.LEFT_LANE:
            n_cards_on_line = len(self.l_cards_on_player_left)
        else:
            n_cards_on_line = len(self.l_cards_on_player_right)

        if card == -1 or card.cost > self.player1.mana \
                      or card.card_type != self.CARD_TYPE_CREATURE \
                      or n_cards_on_line >= 3:
            return False

        return True

    # --------------------------------
    # Charge ability
    # Creatures with Charge can attack the turn they are summoned
    # --------------------------------
    def check_charge(self, card):
        if card.charge:
            card.can_attack = True

    # --------------------------------
    # Perform an atomic USE action
    # --------------------------------
    def do_use(self, v_action):
        instance_id = int(v_action[1])
        target = int(v_action[2])

        ok = self.is_valid_use(instance_id, target)
        if not ok:
            return False

        # remove card and run the use action
        card = self.remove_card(self.l_cards_on_hand, instance_id)
        self.player1.mana -= card.cost

        if card.card_type == self.CARD_TYPE_RED:
            ok = self.perform_use_red(card, target)
        elif card.card_type == self.CARD_TYPE_GREEN:
            ok = self.perform_use_green(card, target)
        else:
            ok = self.perform_use_blue(card, target)

        return ok

    # --------------------------------
    # Return true if the action is a valid use. False, otherwise
    # 1. there is enough mana
    # 2. The card is an item
    # 3. The card is the hand of the player
    # 4. The target exist
    # 5. The target is correct according with type of the item
    # --------------------------------
    def is_valid_use(self, instance_id, target):
        card = self.look_for_card(self.l_cards_on_hand, instance_id)
        if card == -1 or card.cost > self.player1.mana or card.card_type == self.CARD_TYPE_CREATURE:
            return False

        # If card is a red item, look for the target on the opponent side
        if card.card_type == self.CARD_TYPE_RED:
            opponent_card, lane = self.look_for_card_on_opponent_side(target)
            if opponent_card == -1:
                return False

        # If card is a green item, look for the target on the player side
        if card.card_type == self.CARD_TYPE_GREEN:
            friendly_card, lane = self.look_for_card_on_player_side(target)
            if friendly_card == -1:
                return False

        # If card is a blue item, the defense is <0 and target != 0 then look for the target on the opponent side
        if card.card_type == self.CARD_TYPE_BLUE:
            if card.defense >= 0 and target != -1:
                return False
            if card.defense < 0 and target != -1:
                # opponent creature
                opponent_card, lane = self.look_for_card_on_opponent_side(target)
                if opponent_card == -1:
                    return False

        return True

    # --------------------------------
    # Use card red
    # --------------------------------
    def perform_use_red(self, card, target):
        opponent_card, lane = self.look_for_card_on_opponent_side(target)
        if opponent_card == -1:
            return False

        opponent_card.attack += card.attack
        if opponent_card.attack < 0:
            opponent_card.attack = 0
        opponent_card.defense += card.defense

        self.player2.hp += card.opponent_health_change
        self.player1.draw += card.card_draw

        # check if the card has been destroyed. If true, remove it
        if opponent_card.defense <= 0:
            if lane == self.LEFT_LANE:
                self.remove_card(self.l_cards_on_opponent_left, opponent_card.instance_id)
            else:
                self.remove_card(self.l_cards_on_opponent_right, opponent_card.instance_id)
        else:
            if card.breakthrough:
                opponent_card.breakthrough = False

            if card.charge:
                opponent_card.charge = False

            if card.drain:
                opponent_card.drain = False

            if card.guard:
                opponent_card.guard = False

            if card.lethal:
                opponent_card.lethal = False

            if card.ward:
                opponent_card.ward = False

        return True

    # --------------------------------
    # Use card green
    # --------------------------------
    def perform_use_green(self, card, target):
        player_card, lane = self.look_for_card_on_player_side(target)
        if player_card == -1:
            return False

        player_card.attack += card.attack
        player_card.defense += card.defense

        if card.breakthrough:
            player_card.breakthrough = True

        if card.charge:
            player_card.charge = True

        if card.drain:
            player_card.drain = True

        if card.guard:
            player_card.guard = True

        if card.lethal:
            player_card.lethal = True

        if card.ward:
            player_card.ward = True

        self.player2.hp += card.opponent_health_change
        self.player1.draw += card.card_draw

        return True

    # --------------------------------
    # Use card blue
    # Blue items can be applied to target -1, but also to an opponent card
    # --------------------------------
    def perform_use_blue(self, card, target):
        self.player1.hp += card.my_health_change
        self.player2.hp += card.opponent_health_change
        self.player1.draw += card.card_draw

        if target != -1:
            opponent_card, opponent_lane = self.look_for_card_on_opponent_side(target)
            if opponent_card == -1:
                return False

            opponent_card.defense += card.defense

            # check if the card has been destroyed. If true, remove it
            if opponent_card.defense <= 0:
                if opponent_lane == self.LEFT_LANE:
                    self.remove_card(self.l_cards_on_opponent_left, opponent_card.instance_id)
                else:
                    self.remove_card(self.l_cards_on_opponent_right, opponent_card.instance_id)

        return True

    # --------------------------------
    # Perform an atomic attack action
    # --------------------------------
    def do_attack(self, v_action):
        instance_id = int(v_action[1])
        target = int(v_action[2])

        ok, player_card, opponent_card, lane = self.is_valid_attack(instance_id, target)
        if not ok:
            return False

        # atack to oponent player or to an oponent card
        if target == -1:
            self.player2.hp -= player_card.attack
            player_card.can_attack = False  # only one attack each turn
        else:
            player_card.defense -= opponent_card.attack
            opponent_card.defense -= player_card.attack

            self.check_breakthrough(player_card, opponent_card.defense)
            self.check_drain(player_card, opponent_card.attack)
            self.check_lethal(player_card, opponent_card)
            self.check_ward(player_card, opponent_card)

            player_card.can_attack = False  # only one attack each turn

            # remove from lane if the attacking card has defense <= 0
            if player_card.defense <= 0:
                if lane == self.LEFT_LANE:
                    self.remove_card(self.l_cards_on_player_left, instance_id)
                else:
                    self.remove_card(self.l_cards_on_player_right, instance_id)

            # remove from lane if the target card has defense <= 0
            if opponent_card.defense <= 0:
                if lane == self.LEFT_LANE:
                    self.remove_card(self.l_cards_on_opponent_left, instance_id)
                else:
                    self.remove_card(self.l_cards_on_opponent_right, instance_id)

        return True

    # --------------------------------
    # Return True if it is a valid attack. False otherwise
    # 1. attacking card exist on player hand and can attack
    # 2. if target is a card, it must exist on the same lane than the attacking card
    # 3. check if there is any card with guard in the opponent line
    # --------------------------------
    def is_valid_attack(self, instance_id, target):
        player_card, player_lane = self.look_for_card_on_player_side(instance_id)
        if player_card == -1:
            return False, -1, -1, -1

        there_is_guard = self.is_there_some_card_with_guard(player_lane)
        if target == -1:
            if there_is_guard or not player_card.can_attack:
                return False, -1, -1, -1
            opponent_card = -1
        else:
            opponent_card, opponent_lane = self.look_for_card_on_opponent_side(target)
            if opponent_card == -1 or \
               player_lane != opponent_lane or \
               not player_card.can_attack or \
               (there_is_guard and not opponent_card.guard):
                return False, -1, -1, -1

        return True, player_card, opponent_card, player_lane

    # --------------------------------
    # Breakthrough ability
    # Creatures with Breakthrough can deal extra damage to the opponent when they attack enemy creatures.
    # If their attack damage is greater than the defending creature's defense,
    # the excess damage is dealt to the opponent.
    # --------------------------------
    def check_breakthrough(self, player_card, opponent_card_defense):
        if player_card.breakthrough and opponent_card_defense < 0:
            self.player2.hp += opponent_card_defense

    # --------------------------------
    # Drain ability
    # Creatures with Drain heal the player of the amount of the damage they deal (when attacking only).
    # --------------------------------
    def check_drain(self, player_card, opponent_card_attack):
        if player_card.drain:
            self.player1.hp += opponent_card_attack

    # --------------------------------
    # Lethal ability
    # Creatures with Lethal kill the creatures they deal damage to.
    # --------------------------------
    def check_lethal(self, player_card, opponent_card):
        if player_card.lethal:
            opponent_card.defense = 0

    # --------------------------------
    # Ward ability
    # Creatures with Ward ignore once the next damage they would receive from any source.
    # The "shield" given by the Ward ability is then lost.
    # --------------------------------
    def check_ward(self, player_card, opponent_card):
        if opponent_card.ward:
            opponent_card.defense += player_card.attack
            opponent_card.ward = False
        if player_card.ward:
            player_card.defense += opponent_card.attack
            player_card.ward = False

    # --------------------------------
    # Return True ig there is at least one card in the opponent lane with guard
    # --------------------------------
    def is_there_some_card_with_guard(self, lane):
        if lane == self.LEFT_LANE:
            for card in self.l_cards_on_opponent_left:
                if card.guard:
                    return True
        else:
            for card in self.l_cards_on_opponent_right:
                if card.guard:
                    return True

    # --------------------------------
    # Look for a card on a list
    # --------------------------------
    def look_for_card(self, l_cards, instance_id):
        for card in l_cards:
            if card.instance_id == instance_id:
                return card
        return -1

    # --------------------------------
    # Remove a card (the one with instace_id) from the list
    # Return the removed card
    # --------------------------------
    def remove_card(self, l_cards, instance_id):
        card_ith = 0
        for i in range(len(l_cards)):
            if l_cards[i].instance_id == instance_id:
                card_ith = i
                break
        return l_cards.pop(card_ith)

    # --------------------------------
    # Look for the card with the instance_id on the player lanes
    # return -1 if the card is not in the player lanes
    # --------------------------------
    def look_for_card_on_player_side(self, instace_id):
        card = self.look_for_card(self.l_cards_on_player_left, instace_id)
        if card != -1:
            return card, self.LEFT_LANE

        card = self.look_for_card(self.l_cards_on_player_right, instace_id)
        if card != -1:
            return card, self.RIGHT_LANE

        # if not found
        return -1, -1

    # --------------------------------
    # Look for the card with the instance_id on the opponent lanes
    # return -1 if the card is not in the opponent lanes
    # --------------------------------
    def look_for_card_on_opponent_side(self, instace_id):
        card = self.look_for_card(self.l_cards_on_opponent_left, instace_id)
        if card != -1:
            return card, self.LEFT_LANE

        card = self.look_for_card(self.l_cards_on_opponent_right, instace_id)
        if card != -1:
            return card, self.RIGHT_LANE

        # if not found
        return -1, -1


# -----------------------------------------------------
# A mixed Coac and Uji2 draft algorithm
# -----------------------------------------------------
class MixedDraft:
    def __init__(self):
        self.TYPE_CREATURE = 0
        self.TYPE_GREEN = 1
        self.TYPE_RED = 2
        self.TYPE_BLUE = 3

        # best cards are before in the list
        self.sorted_cards = [68,   7,  65,  49, 116,  69, 151,  48,  53,  51,  44, 67,  29, 139,  84, 18,
                             158,  28,  64,  80,  33,  85,  32, 147, 103,  37,  54, 52,  50,  99,  23, 87,
                             66,  81, 148,  88, 150, 121,  82,  95, 115, 133, 152, 19, 109, 157, 105,  3,
                             75,  96, 114,   9, 106, 144, 129,  17, 111, 128,  12, 11, 145,  15,  21,  8,
                             134, 155, 141,  70,  90, 135, 104,  41, 112,  61,   5, 97,  26,  34,  73,  6,
                             36,  86,  77,  83,  13,  89,  79,  93, 149,  59, 159, 74,  94,  38,  98, 126,
                             39,  30, 137, 100,  62, 122,  22,  72, 118,   1,  47, 71,   4,  91,  27,  56,
                             119, 101, 45, 16, 146, 58, 120, 142, 127, 25, 108, 132, 40, 14, 76, 125, 102,
                             131, 123, 2, 35, 130, 107, 43, 63, 31, 138, 124, 154, 78, 46, 24, 10, 136, 113,
                             60, 57, 92, 117, 42, 55, 153, 20, 156, 143, 110, 160, 140]

        self.picked_card_type = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.prefer_card_type = [5, 4, 4, 3, 3, 3, 2, 2, 2, 1]  # this the desired number of cards of each type

    # ------------------------------------------------------------
    # Pick card
    # ------------------------------------------------------------
    def pick_card(self, l_cards):
        best_card = self.select_bestcard(l_cards)
        if l_cards[best_card].card_type == self.TYPE_CREATURE and l_cards[best_card].cost < 2:
            self.picked_card_type[0] += 1
        elif l_cards[best_card].card_type == self.TYPE_CREATURE and l_cards[best_card].cost < 3:
            self.picked_card_type[1] += 1
        elif l_cards[best_card].card_type == self.TYPE_CREATURE and l_cards[best_card].cost < 4:
            self.picked_card_type[2] += 1
        elif l_cards[best_card].card_type == self.TYPE_CREATURE and l_cards[best_card].cost < 5:
            self.picked_card_type[3] += 1
        elif l_cards[best_card].card_type == self.TYPE_CREATURE and l_cards[best_card].cost < 6:
            self.picked_card_type[4] += 1
        elif l_cards[best_card].card_type == self.TYPE_CREATURE and l_cards[best_card].cost < 7:
            self.picked_card_type[5] += 1
        elif l_cards[best_card].card_type == self.TYPE_CREATURE:
            self.picked_card_type[6] += 1
        elif l_cards[best_card].card_type == self.TYPE_GREEN:
            self.picked_card_type[7] += 1
        elif l_cards[best_card].card_type == self.TYPE_RED:
            self.picked_card_type[8] += 1
        else:
            self.picked_card_type[9] += 1

        return best_card

    # ------------------------------------------------------------
    # Algorithm to select the best card.
    # ------------------------------------------------------------
    def select_bestcard(self, l_cards):
        v = []
        for card in l_cards:
            if card.card_type == self.TYPE_CREATURE:
                if card.cost < 2:
                    v.append(self.picked_card_type[0] / self.prefer_card_type[0])
                elif card.cost < 3:
                    v.append(self.picked_card_type[1] / self.prefer_card_type[1])
                elif card.cost < 4:
                    v.append(self.picked_card_type[2] / self.prefer_card_type[2])
                elif card.cost < 5:
                    v.append(self.picked_card_type[3] / self.prefer_card_type[3])
                elif card.cost < 6:
                    v.append(self.picked_card_type[4] / self.prefer_card_type[4])
                elif card.cost < 7:
                    v.append(self.picked_card_type[5] / self.prefer_card_type[5])
                else:
                    v.append(self.picked_card_type[6] / self.prefer_card_type[6])
            elif card.card_type == self.TYPE_GREEN:
                v.append(self.picked_card_type[7] / self.prefer_card_type[7])
            elif card.card_type == self.TYPE_RED:
                v.append(self.picked_card_type[8] / self.prefer_card_type[8])
            else:
                v.append(self.picked_card_type[9] / self.prefer_card_type[9])

        selected_card = 0
        if v[0] == v[1]:
            if v[0] == v[2]:                                 # three equal
                selected_card = self.get_best_card(l_cards)
            else:                                            # 0 and 1 equal
                l_temp = [l_cards[0], l_cards[1]]
                selected_card = self.get_best_card(l_temp)

        elif v[0] == v[2]:                                   # 0 and 2 equal
            l_temp = [l_cards[0], l_cards[2]]
            selected_card = self.get_best_card(l_temp)
            if selected_card == 1:
                selected_card = 2

        elif v[1] == v[2]:                                  # 1 and 2 equal
            l_temp = [l_cards[1], l_cards[2]]
            selected_card = self.get_best_card(l_temp)
            if selected_card == 0:
                selected_card = 1
            else:
                selected_card = 2
        else:
            if v[0] < v[1] and v[0] < v[2]:
                selected_card = 0
            elif v[1] < v[0] and v[1] < v[2]:
                selected_card = 1
            elif v[2] < v[0] and v[2] < v[1]:
                selected_card = 2

        return selected_card

    def get_best_card(self, l_cards):
        best_score = 10E6
        best_instace_id = 0
        i = 0
        for card in l_cards:
            pos = self.sorted_cards.index(card.card_id)
            if pos < best_score:
                best_score = pos
                best_instace_id = i
            i += 1
        return best_instace_id


# --------------------------------
# UJI3Agent
# --------------------------------
class UJIAgent3:
    def __init__(self):
        self.allowed_time = 0
        self.state = None
        self.start_time = 0
        self.draft = MixedDraft()

    # --------------------------------
    # Setters
    # --------------------------------
    def set_allowed_time(self, allowed_time):
        self.allowed_time = allowed_time

    # --------------------------------
    # Read input
    # --------------------------------
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
            card_number, instance_id, location, card_type, cost, attack, defense, abilities, \
                         my_health_change, opponent_health_change, card_draw, lane = input().split()
            one_card = CardAgent(int(card_number), int(instance_id), int(location), int(card_type),
                                 int(cost), int(attack), int(defense), abilities, int(my_health_change),
                                 int(opponent_health_change), int(card_draw), int(lane))

            l_cards.append(one_card)

        player1 = PlayerAgent(player_health1, player_mana1, player_deck1, player_rune1, player_draw1)
        player2 = PlayerAgent(player_health2, player_mana2, player_deck2, player_rune2, player_draw2)
        self.state = StateAgent(player1, player2, l_cards)

    # --------------------------------
    # Act funtion, return the list of actions to do
    # --------------------------------
    def act(self):
        self.start_time = time.time()
        if self.state.is_draft():
            return self.ia_draft()
        else:
            return self.ia_battle()

    # --------------------------------
    # IA Draft
    # --------------------------------
    def ia_draft(self):
        n = self.draft.pick_card(self.state.l_cards_draft)
        return "PICK " + str(n)

    # --------------------------------
    # IA Battle
    # --------------------------------
    def ia_battle(self):
        # if it is possible to kill the opponent, then attack to them
        l_actions = self.can_win()

        # if not, learn the correct order to play the actions
        if len(l_actions) == 0:
            l_all_posible_actions = self.state.get_list_all_possible_actions()
            if len(l_all_posible_actions) == 0:
                return "PASS"
            elif len(l_all_posible_actions) == 1:
                return l_all_posible_actions[0]

            l_actions = self.oep(l_all_posible_actions)

        return self.to_str(l_actions)

    # --------------------------------
    # If the player can win the game, returns the list of actions to do it.
    # If not, returns []
    # --------------------------------
    # TODO, check other order to attack
    def can_win(self):
        l_actions = []
        total_attack_power = 0

        l_guard_l = []
        l_guard_r = []

        for card in self.state.l_cards_on_opponent_left:
            if card.guard:
                l_guard_l.append(copy.copy(card))

        for card in self.state.l_cards_on_opponent_right:
            if card.guard:
                l_guard_r.append(copy.copy(card))

        # left
        i_target = 0
        for card in self.state.l_cards_on_player_left:
            if i_target < len(l_guard_l):
                target = l_guard_l[i_target].instance_id
                l_guard_l[i_target].defense -= card.attack
                if l_guard_l[i_target].defense <= 0:
                    i_target += 1
            else:
                target = -1
                total_attack_power += card.attack

            l_actions.append("ATTACK " + str(card.instance_id) + " " + str(target))

        # right
        i_target = 0
        for card in self.state.l_cards_on_player_right:
            if i_target < len(l_guard_r):
                target = l_guard_r[i_target].instance_id
                l_guard_r[i_target].defense -= card.attack
                if l_guard_r[i_target].defense <= 0:
                    i_target += 1
            else:
                target = -1
                total_attack_power += card.attack

            l_actions.append("ATTACK " + str(card.instance_id) + " " + str(target))

        if self.state.player2.hp - total_attack_power <= 0:
            return l_actions
        else:
            return []

    # ---------------------------------------
    # Randomly shuffle the list of actions
    # ---------------------------------------
    def get_random_actions(self, l_all_posible_actions):
        l_actions = copy.copy(l_all_posible_actions)
        random.shuffle(l_actions)
        return l_actions

    # ---------------------------------------
    # From list to string
    # ---------------------------------------
    def to_str(self, individual):
        str_actions = ""
        for action in individual:
            str_actions += action + ";"

        return str_actions

    # ---------------------------------------
    # Online Evolution Algortihm
    # 1+1 EA
    # Select random or with a predefined order of the list of actions
    # Evolute
    # ---------------------------------------
    def oep(self, l_all_posible_actions):
        org_individual = self.get_random_actions(l_all_posible_actions)
        return self.oep_algorithm(org_individual)

    def oep_algorithm(self, org_individual):
        count = 0
        n = len(org_individual)

        if n == 1:
            return org_individual

        if n == 2:
            org_score, org_clean = self.state.evaluate(org_individual)
            new_individual = self.mutate(org_individual)
            new_score, new_clean = self.state.evaluate(new_individual)
            if new_score >= org_score:
                return new_clean
            else:
                return org_clean

        # 3 or more
        org_score, org_clean = self.state.evaluate(org_individual)

        actual_time = time.time() - self.start_time
        while actual_time < self.allowed_time:
            new_individual = self.mutate(org_individual)
            new_score, new_clean = self.state.evaluate(new_individual)
            count += 1
            if new_score >= org_score:
                org_individual = new_individual
                org_clean = new_clean
                org_score = new_score

            actual_time = time.time() - self.start_time

        return org_clean

    # -------------------------------
    # Mutate.
    # Only if the individual is len > 1
    # -------------------------------
    def mutate(self, org_individual):
        new_individual = copy.copy(org_individual)

        if len(new_individual) == 1:
            return new_individual

        if len(new_individual) == 2:
            temp = new_individual[1]
            new_individual[1] = new_individual[0]
            new_individual[0] = temp
            return new_individual

        # Three gens or more 
        # Select one gen to mutate
        n1 = random.randint(0, len(new_individual) - 1)
        n2 = n1
        while n2 == n1:
            n2 = random.randint(0, len(new_individual) - 1)

        temp = new_individual[n2]
        new_individual[n2] = new_individual[n1]
        new_individual[n1] = temp

        return new_individual


# ----------------------------------------------
# MAIN
# ----------------------------------------------
if __name__ == '__main__':
    agent = UJIAgent3()
    allowed_time = 0.190  # seconds
    agent.set_allowed_time(allowed_time)

    while True:
        agent.read_input()
        # agent.state.print_state(sys.stderr)
        actions = agent.act()
        print(actions)

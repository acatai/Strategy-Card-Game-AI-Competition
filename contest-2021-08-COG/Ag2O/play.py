import numpy as np
import time
import sys
import warnings
warnings.filterwarnings('ignore')

import ai

MAX_HAND_NUM = 8
HAND_CARD_FEATURE = 16
MAX_LANE_NUM = 2
MAX_CARD_IN_LANE = 3
PLAYER_LANE_CARD_FEATURE = 9
OPPONENT_LANE_CARD_FEATURE = 8
ABILITY_NUM = 6

class State:
    def __init__(self):
        self.state = np.array([])
        self.end = False
    
    # player information
    def set_player_info(self, player_health=0, player_mana=0, player_rune=0, player_draw=0,
                        opponent_health=0, opponent_mana=0, opponent_rune=0, opponent_draw=0):
        self.player_state = [player_health,player_mana,player_rune,player_draw,
                             opponent_health,opponent_mana,opponent_rune,opponent_draw]
        
    # hand
    def set_hand_state(self, hand_list):
        self.hand_id_state = [0] * MAX_HAND_NUM
        self.hand_state = [[0] * HAND_CARD_FEATURE] * MAX_HAND_NUM
        for i in range(len(hand_list)):
            self.hand_state[i] = hand_list[i][:16]
            self.hand_id_state[i] = hand_list[i][15]
    
    # encode ability
    def encode_ability(self, ability):
        ability_code = [0]*ABILITY_NUM
        if ("B" in ability): ability_code[0] = 1
        if ("C" in ability): ability_code[1] = 1
        if ("D" in ability): ability_code[2] = 1
        if ("G" in ability): ability_code[3] = 1
        if ("L" in ability): ability_code[4] = 1
        if ("W" in ability): ability_code[5] = 1
        return ability_code
    
    # player's lane
    def set_player_lane(self, left, right):
        #left
        self.player_lane = []
        self.players_left_lane = [[0] * PLAYER_LANE_CARD_FEATURE] * MAX_CARD_IN_LANE
        id_left_lane = [[0] * (PLAYER_LANE_CARD_FEATURE + 1)] * MAX_CARD_IN_LANE
        for i in range(len(left)):
            self.players_left_lane[i] = left[i][:9]
            id_left_lane[i] = left[i]
        
        # right
        self.players_right_lane = [[0] * PLAYER_LANE_CARD_FEATURE] * MAX_CARD_IN_LANE
        id_right_lane = [[0] * (PLAYER_LANE_CARD_FEATURE + 1)] * MAX_CARD_IN_LANE
        for i in range(len(right)):
            self.players_right_lane[i] = right[i][:9]
            id_right_lane[i] = right[i]

        self.player_lane.append(id_left_lane)
        self.player_lane.append(id_right_lane)
    
    # opponent's lane
    def set_opponent_lane(self, left, right):
        self.opponents_lane = []
        # left
        self.opponents_left_lane = [[0] * OPPONENT_LANE_CARD_FEATURE] * MAX_CARD_IN_LANE
        id_left_lane = [[0] * (OPPONENT_LANE_CARD_FEATURE + 1)] * MAX_CARD_IN_LANE
        for i in range(len(left)):
            self.opponents_left_lane[i] = left[i][:8]
            id_left_lane[i] = left[i]
        
        #r ight
        self.opponents_right_lane = [[0] * OPPONENT_LANE_CARD_FEATURE] * MAX_CARD_IN_LANE
        id_right_lane = [[0] * (OPPONENT_LANE_CARD_FEATURE + 1)] * MAX_CARD_IN_LANE
        for i in range(len(right)):
            self.opponents_right_lane[i] = right[i][:8]
            id_right_lane[i] = right[i]        

        self.opponents_lane.append(id_left_lane)
        self.opponents_lane.append(id_right_lane)
    
    # synchronize state
    def check_lane(self):
        for idx in range(MAX_CARD_IN_LANE):
            if self.player_lane[0][idx][1] <= 0:
                self.player_lane[0][idx] = [0] * (PLAYER_LANE_CARD_FEATURE + 1)

            if self.player_lane[1][idx][1] <= 0:
                self.player_lane[1][idx] = [0] * (PLAYER_LANE_CARD_FEATURE + 1)

            if self.opponents_lane[0][idx][1] <= 0:
                self.opponents_lane[0][idx] = [0] * (OPPONENT_LANE_CARD_FEATURE + 1)

            if self.opponents_lane[1][idx][1] <= 0:
                self.opponents_lane[1][idx] = [0] * (OPPONENT_LANE_CARD_FEATURE + 1)

    # merge
    def merge_state(self):
        self.state = np.array(self.player_state + sum(self.hand_state,[]) + \
                              sum(self.players_left_lane,[]) + sum(self.players_right_lane,[]) + \
                              sum(self.opponents_left_lane,[]) + sum(self.opponents_right_lane,[]))
        
        for i in range(len(self.state)):
            if abs(self.state[i]) > 30:
                if self.state[i] < 0:
                    self.state[i] = -12
                else:
                    if i < 8:
                        self.state[i] = 30
                    else:
                        self.state[i] = 12

    # get state
    def get_state(self):
        state_for_model = self.state
        for i in range(len(state_for_model)):
            if abs(state_for_model[i]) > 12:
                state_for_model[i] = 12 
        return state_for_model / 30
    
    # update the state
    def update_state(self, action_code):
        #action_code = [actiontype, from_index, to_index]

        # summon
        if action_code[0] == 1:
            summon_card = self.hand_state[action_code[1]]
            self.player_state[1] -= summon_card[6]
            self.player_state[0] += summon_card[13]
            self.player_state[4] += summon_card[14]
            self.player_state[3] += summon_card[15]
            del summon_card[13:16]
            del summon_card[6]
            del summon_card[0:4]

            # charge
            if summon_card[3] == 1:
                summon_card.append(1)
            else:
                summon_card.append(0)

            if action_code[2] == 0:
                for idx in range(MAX_CARD_IN_LANE):
                    if self.players_left_lane[idx][1] == 0:
                        self.players_left_lane[idx] = summon_card
                        self.player_lane[0][idx] = summon_card + [self.hand_id_state[action_code[1]]]
                        break
            else:
                for idx in range(MAX_CARD_IN_LANE):
                    if self.players_right_lane[idx][1] == 0:
                        self.players_right_lane[idx] = summon_card
                        self.player_lane[1][idx] = summon_card + [self.hand_id_state[action_code[1]]]
                        break

            self.hand_state[action_code[1]] = [0]*HAND_CARD_FEATURE
        
        # use
        elif action_code[0] == 2:
            use_card = self.hand_state[action_code[1]]
            self.hand_state[action_code[1]] = [0]*HAND_CARD_FEATURE

            # green
            if use_card[1] == 1:
                temp = action_code[2]
                action_code[2] -= 1
                if temp == 0:
                    # error
                    pass
                # left
                elif (action_code[2] % 6) / 3 == 0:
                    # to creature
                    index = action_code[2] % 3
                    self.players_left_lane[index][0] += use_card[4]
                    self.players_left_lane[index][1] += use_card[5]
                    self.players_left_lane[index][2] += use_card[7]
                    self.players_left_lane[index][3] += use_card[8]
                    self.players_left_lane[index][4] += use_card[9]
                    self.players_left_lane[index][5] += use_card[10]
                    self.players_left_lane[index][6] += use_card[11]
                    self.players_left_lane[index][7] += use_card[12]

                    # to player
                    self.player_state[0] += use_card[13]
                    self.player_state[1] -= use_card[6]
                    self.player_state[3] += use_card[14]
                    self.player_state[4] += use_card[15]

                    # ATK and DEF
                    if self.players_left_lane[index][0] < 0:
                        self.players_left_lane[index][0] = 0
                    if self.players_left_lane[index][1] <= 0:
                        self.players_left_lane[index] = [0,0,0,0,0,0,0,0]
                # right
                else:
                    # to creature
                    index = action_code[2] % 3
                    self.players_right_lane[index][0] += use_card[4]
                    self.players_right_lane[index][1] += use_card[5]
                    self.players_right_lane[index][2] += use_card[7]
                    self.players_right_lane[index][3] += use_card[8]
                    self.players_right_lane[index][4] += use_card[9]
                    self.players_right_lane[index][5] += use_card[10]
                    self.players_right_lane[index][6] += use_card[11]
                    self.players_right_lane[index][7] += use_card[12]

                    # to player
                    self.player_state[0] += use_card[13]
                    self.player_state[1] -= use_card[6]
                    self.player_state[4] += use_card[14]
                    self.player_state[3] += use_card[15]

                    # ATK and DEF
                    if self.players_right_lane[index][0] < 0:
                        self.players_right_lane[index][0] = 0
                    if self.players_right_lane[index][1] <= 0:
                        self.players_right_lane[index] = [0,0,0,0,0,0,0,0]
            # red,blue
            elif use_card[2] == 1 or use_card[3] == 1:
                temp = action_code[2]
                action_code[2] -= 1

                # to opponent
                if temp == 0:
                    self.player_state[4] += use_card[5]
                    self.player_state[0] += use_card[13]
                    self.player_state[1] -= use_card[6]
                    self.player_state[4] += use_card[14]
                    self.player_state[3] += use_card[15]

                # left
                elif (action_code[2] % 6) / 3 == 0:
                    # to creature
                    index = action_code[2] % 3
                    self.opponents_left_lane[index][0] += use_card[4]
                    # ward
                    if self.opponents_left_lane[index][7] >= 1:
                        self.opponents_left_lane[index][1] += use_card[5]
                    else:
                        self.opponents_left_lane[index][7] = 0
                    self.opponents_left_lane[index][2] -= use_card[7]
                    self.opponents_left_lane[index][3] -= use_card[8]
                    self.opponents_left_lane[index][4] -= use_card[9]
                    self.opponents_left_lane[index][5] -= use_card[10]
                    self.opponents_left_lane[index][6] -= use_card[11]
                    self.opponents_left_lane[index][7] -= use_card[12]

                    # ability
                    for i in range(6):
                        if self.opponents_left_lane[index][2+i] < 0:
                            self.opponents_left_lane[index][2+i] = 0

                    # to player
                    self.player_state[0] += use_card[13]
                    self.player_state[1] -= use_card[6]
                    self.player_state[4] += use_card[14]
                    self.player_state[3] += use_card[15]

                    # ATK and DEF
                    if self.opponents_left_lane[index][0] < 0:
                        self.opponents_left_lane[index][0] = 0
                    if self.opponents_left_lane[index][1] <= 0:
                        self.opponents_left_lane[index] = [0,0,0,0,0,0,0,0]
                # right
                else:
                    # to creature
                    index = action_code[2] % 3
                    self.opponents_right_lane[index][0] += use_card[4]

                    # ward
                    if self.opponents_right_lane[index][7] >= 1:
                        self.opponents_right_lane[index][1] += use_card[5]
                    else:
                        self.opponents_right_lane[index][7] = 0

                    self.opponents_right_lane[index][2] -= use_card[4]
                    self.opponents_right_lane[index][3] -= use_card[4]
                    self.opponents_right_lane[index][4] -= use_card[4]
                    self.opponents_right_lane[index][5] -= use_card[4]
                    self.opponents_right_lane[index][6] -= use_card[4]
                    self.opponents_right_lane[index][7] -= use_card[4]

                    # ability
                    for i in range(6):
                        if self.opponents_right_lane[index][2+i] < 0:
                            self.opponents_right_lane[index][2+i] = 0

                    #to player
                    self.player_state[0] += use_card[13]
                    self.player_state[1] -= use_card[6]
                    self.player_state[4] += use_card[14]
                    self.player_state[3] += use_card[15]

                    # ATK and DEF
                    if self.opponents_right_lane[index][0] < 0:
                        self.opponents_right_lane[index][0] = 0
                    if self.opponents_right_lane[index][1] <= 0:
                        self.opponents_right_lane[index] = [0,0,0,0,0,0,0,0]

        # attack
        elif action_code[0] == 3:
            # left
            if action_code[1] // 3 == 0:
                # attack from
                from_atk = self.players_left_lane[action_code[1] % 3][0]

                if action_code[2] == 0:
                    # direct attack
                    self.player_state[4] -= from_atk
                else:
                    # attack to
                    action_code[2] -= 1
                    to_atk = self.opponents_left_lane[action_code[2]][0]

                    # ward
                    if self.opponents_left_lane[action_code[2]][7] >= 1:
                        self.opponents_left_lane[action_code[2]][7] == 0
                    else:
                        self.opponents_left_lane[action_code[2]][1] -= from_atk

                    if self.players_left_lane[action_code[1] % 3][7] >= 1:
                        self.players_left_lane[action_code[1] % 3][7] = 0
                    else:
                        self.players_left_lane[action_code[1] % 3][1] -= to_atk
                    
                    # drain
                    if (self.players_left_lane[action_code[1] % 3][4] >= 1):
                        if (self.opponents_left_lane[action_code[2]][1] > from_atk):
                            self.player_state[0] += from_atk
                        else:
                            self.player_state[0] += self.opponents_left_lane[action_code[2]][1]

                    # breakthrogh
                    if (self.players_left_lane[action_code[1] % 3][2] >= 1) and (self.opponents_left_lane[action_code[2]][1] < from_atk):
                        dmg = from_atk - self.opponents_left_lane[action_code[2]][1]
                        self.player_state[4] -= dmg
                    
                    # lethal
                    if (self.players_left_lane[action_code[1] % 3][6] >= 1):
                        self.opponents_left_lane[action_code[2]][1] = 0
                        self.players_left_lane[action_code[1] % 3][1] -= to_atk
                    if (self.opponents_left_lane[action_code[2]][6] >= 1):
                        self.players_left_lane[action_code[1] % 3][1] = 0

                # can attack update
                self.players_left_lane[action_code[1] % 3][8] = 0

            else:
                # attack from
                from_atk = self.players_right_lane[action_code[1] % 3][0]

                if action_code[2] == 0:
                    # direct attack
                    self.player_state[4] -= from_atk
                else:
                    # attack to
                    action_code[2] -= 1
                    to_atk = self.opponents_right_lane[action_code[2]][0]

                    # ward
                    if self.opponents_right_lane[action_code[2]][7] >= 1:
                        self.opponents_right_lane[action_code[2]][7] == 0
                    else:
                        self.opponents_right_lane[action_code[2]][1] -= from_atk

                    if self.players_right_lane[action_code[1] % 3][7] >= 1:
                        self.players_right_lane[action_code[1] % 3][7] = 0
                    else:
                        self.players_right_lane[action_code[1] % 3][1] -= to_atk
                    
                    # drain
                    if (self.players_right_lane[action_code[1] % 3][4] >= 1):
                        if (self.opponents_right_lane[action_code[2]][1] > from_atk):
                            self.player_state[0] += from_atk
                        else:
                            self.player_state[0] += self.opponents_right_lane[action_code[2]][1]

                    # breakthrogh
                    if (self.players_right_lane[action_code[1] % 3][2] >= 1) and (self.opponents_right_lane[action_code[2]][1] < from_atk):
                        dmg = from_atk - self.opponents_right_lane[action_code[2]][1]
                        self.player_state[4] -= dmg
                    
                    # lethal
                    if (self.players_right_lane[action_code[1] % 3][6] >= 1):
                        self.opponents_right_lane[action_code[2]][1] = 0
                        self.players_right_lane[action_code[1] % 3][1] -= to_atk
                    if (self.opponents_right_lane[action_code[2]][6] >= 1):
                        self.players_right_lane[action_code[1] % 3][1] = 0

                # can attack update
                self.players_right_lane[action_code[1] % 3][8] = 0

        # check dead of card 
        for idx in range(MAX_CARD_IN_LANE):
            if self.players_left_lane[idx][1] <= 0:
                self.players_left_lane[idx] = [0,0,0,0,0,0,0,0,0]

            if self.players_right_lane[idx][1] <= 0:
                self.players_right_lane[idx] = [0,0,0,0,0,0,0,0,0]

            if self.opponents_left_lane[idx][1] <= 0:
                self.opponents_left_lane[idx] = [0,0,0,0,0,0,0,0]

            if self.opponents_right_lane[idx][1] <= 0:
                self.opponents_right_lane[idx] = [0,0,0,0,0,0,0,0]
        
        # merge state
        self.merge_state()
        self.check_lane()
    
    # emepty in lane
    def get_lane(self):
        left_count = 0
        right_count = 0
        for idx in range(MAX_CARD_IN_LANE):
            if [0]*PLAYER_LANE_CARD_FEATURE == self.players_left_lane[idx]:
                left_count += 1
            if [0]*PLAYER_LANE_CARD_FEATURE == self.players_right_lane[idx]:
                right_count += 1
        return left_count, right_count
    
    # legal actions
    def get_legal_actions(self):
        legal_actions = [0]
        current_mana = self.player_state[1]
        empty_left, empty_right = self.get_lane()

        # summon and use
        for idx in range(len(self.hand_state)):

            # check mana
            if current_mana >= self.hand_state[idx][6]:

                # creature
                if self.hand_state[idx][0] >= 1:
                    # summon
                    if empty_left >= 1:
                        legal_actions.append(1+idx*2)
                    if empty_right >= 1:
                        legal_actions.append(1+idx*2+1)

                # green
                elif self.hand_state[idx][1] >= 1:
                    for target in range(MAX_CARD_IN_LANE):
                        if 0 != self.players_left_lane[target][1]:
                            legal_actions.append(17+idx*13+1+target)

                        if 0 != self.players_right_lane[target][1]:
                            legal_actions.append(17+idx*13+4+target)

                # red
                elif self.hand_state[idx][2] >= 1:
                    for target in range(MAX_CARD_IN_LANE):
                        if 0 != self.opponents_left_lane[target][1]:
                            legal_actions.append(17+idx*13+7+target)

                        if 0 != self.opponents_right_lane[target][1]:
                            legal_actions.append(17+idx*13+10+target)

                # blue
                elif self.hand_state[idx][3] >= 1:
                    legal_actions.append(17+idx*13)
        
        # attack:left
        is_guard = False
        for idx in range(MAX_CARD_IN_LANE):
            if self.players_left_lane[idx][8] >= 1:
                for target in range(MAX_CARD_IN_LANE):
                    # guard
                    if self.opponents_left_lane[target][5] >= 1:
                        legal_actions.append(121+idx*4+1+target)
                        is_guard = True

                for target in range(MAX_CARD_IN_LANE):
                    # direct and normal attack
                    if not is_guard:
                        if 121+idx*4 not in legal_actions:
                            legal_actions.append(121+idx*4)

                        if self.opponents_left_lane[target][1] > 0:
                            legal_actions.append(121+idx*4+1+target)
        
        # attack:right
        is_guard = False
        for idx in range(MAX_CARD_IN_LANE):
            if self.players_right_lane[idx][8] >= 1:
                idx += 3
                for target in range(MAX_CARD_IN_LANE):
                    # guard
                    if self.opponents_right_lane[target][5] >= 1:
                        legal_actions.append(121+idx*4+1+target)
                        is_guard = True

                for target in range(MAX_CARD_IN_LANE):
                    # direct and normal attack
                    if not is_guard:
                        if 121+idx*4 not in legal_actions:
                            legal_actions.append(121+idx*4)

                        if self.opponents_right_lane[target][1] > 0:
                            legal_actions.append(121+idx*4+1+target)
        
        return legal_actions
    
    # decode the action from action number
    def decode_action(self,action, player_hand, player_lanes, opponent_lanes):
        action_code = [0, 0, 0]
        # pass
        if action == 0:
            return "PASS", action_code

        # summon
        elif 1 <= action <= 16:
            action -= 1
            origin = int(action / 2)
            target = int(action % 2)
            action_code = [1, origin, target]
            origin = player_hand[origin][16]
            return "SUMMON "+ str(origin) + " " + str(target), action_code

        # use
        elif 17 <= action <= 120:
            action -= 17
            index = int(action / 13)
            target = action % 13
            action_code = [2, index, target]
            origin = player_hand[index][16]

            if target == 0:
                target = -1
            else:
                target -= 1
                # green
                if player_hand[index][1] >= 1:
                    index = target % 3
                    lane = int((target % 6) / 3)
                    target = player_lanes[lane][index][9]
                # red,blue?
                elif (player_hand[index][2] >= 1) or (player_hand[index][3] >= 1):
                    index = target % 3
                    lane = int((target % 6) / 3)
                    target = opponent_lanes[lane][index][8]
            return "USE " + str(origin) + " " + str(target), action_code
        
        # attack
        elif 121 <= action <= 144:
            action -= 121
            origin = action // 4
            target = action % 4
            action_code = [3, origin, target]
            lane = origin // 3
            origin = player_lanes[lane][origin % 3][9]

            if target == 0:
                target = -1
            else:
                target -= 1
            
                target = opponent_lanes[lane][target][8]
            return "ATTACK " + str(origin) + " " + str(target), action_code
        else:
            return "PASS", action_code


if __name__ == "__main__":
    # turn
    turn = 0

    # agent
    agent = ai.DQNAgent()

    # game state
    state = State()

    # game loop
    while True:
        # input player's infomation
        player_health, player_mana, player_deck, player_rune, player_draw = [int(j) for j in input().split()]
        opponent_health, opponent_mana,opponent_deck,opponent_rune, opponent_draw = [int(j) for j in input().split()]
        opponent_hand, opponent_actions_num = [int(i) for i in input().split()]
        state.set_player_info(player_health, player_mana, player_rune, player_draw, \
                            opponent_health, opponent_mana, opponent_rune, opponent_draw)
        
        # load model
        if opponent_deck == 0 and turn == 0:
            # first
            print("---load first model---",file=sys.stderr,flush=True)
            agent.load_model("first")
            agent.load_score("first")
        elif opponent_deck == 1 and turn == 0:
            # second
            print("---load second model---",file=sys.stderr,flush=True)
            agent.load_model("second")
            agent.load_score("second")

        # opponent's action history
        oppoent_actions = []
        for i in range(opponent_actions_num):
            oppoent_actions.append(input())
        del oppoent_actions

        # card information
        card_count = int(input())
        card_in_hand = []
        card_in_leftlane = []
        card_in_rightlane = []
        card_in_opp_leftlane = []
        card_in_opp_rightlane = []
        card_id = []
        for i in range(card_count):
            card_name, instance_id, location, type, cost, attack, defense, keywords, my_health, opponent_health, card_draw, lane = input().split()
            card_name = int(card_name)
            instance_id = int(instance_id)
            location = int(location)
            type = int(type)
            mana = int(cost)
            attack = int(attack)
            defense = int(defense)
            my_health = int(my_health)
            opponent_health = int(opponent_health)
            card_draw = int(card_draw)
            lane = int(lane)
            ability_code = state.encode_ability(keywords)

            encode_type = [0,0,0,0]
            if card_name != 0:
                encode_type[type] = 1

            # my left lane
            if ((location == 1) and (lane == 0)):
                card_in_leftlane.append([attack,defense] + ability_code + [1] + [instance_id])
            
            # my right lane
            elif ((location == 1) and (lane == 1)):
                card_in_rightlane.append([attack,defense] + ability_code + [1] + [instance_id])
            
            # opponent's left lane
            elif ((location == -1) and (lane == 0)):
                card_in_opp_leftlane.append([attack,defense] + ability_code + [instance_id])
            
            # opponent's right lane
            elif ((location == -1) and (lane == 1)):
                card_in_opp_rightlane.append([attack,defense] + ability_code + [instance_id])

            # my hand
            elif location == 0:
                card_in_hand.append(encode_type + [attack,defense,mana] + ability_code + [my_health,opponent_health,card_draw] + [instance_id])
                card_id.append(card_name)
            
            # error
            else:
                print("error: why?",file=sys.stderr,flush=True)

        state.set_hand_state(card_in_hand)
        state.set_player_lane(card_in_leftlane,card_in_rightlane)
        state.set_opponent_lane(card_in_opp_leftlane,card_in_opp_rightlane)
        state.merge_state()

        # draft
        if turn < 30:
            action = agent.draft_act(card_id)
            print("PICK "+str(action),file=sys.stderr,flush=True)
            print("PICK "+str(action))

        # battle
        else:
            start = time.time()
            update_time = 0
            action = ""
            while True:
                current_state = state.get_state()
                legal_actions = state.get_legal_actions()
                if len(legal_actions) > 1:
                    del legal_actions[0]

                # action
                act_num, max_q = agent.greedy_act(state,4,start,legal_actions,card_in_hand[:17])
                act, act_code = state.decode_action(act_num,card_in_hand[:17],state.player_lane,state.opponents_lane)
                action += act
                print("action: ",act," max_q: ",float(max_q),file=sys.stderr,flush=True)

                # time up
                if 0.17 < (time.time() - start):
                    while True:
                        state.update_state(act_code)
                        action += ";"
                        current_state = state.get_state()
                        legal_actions = state.get_legal_actions()
                        if len(legal_actions) > 1:
                            del legal_actions[0]
                        
                        qs = agent.battle_act(current_state,legal_actions)
                        act_num = legal_actions[np.argmax(qs)]
                        act, act_code = state.decode_action(act_num,card_in_hand[:17],state.player_lane,state.opponents_lane)
                        action += act
                        print("action: ",act," max_q: ",float(max_q),file=sys.stderr,flush=True)

                        if 0.19 < (time.time() - start) or act == "PASS":
                            print("action time: ",(time.time() - start),file=sys.stderr,flush=True)
                            break
                    break
                
                # pass
                if act == "PASS":
                    print("action time: ",(time.time() - start),file=sys.stderr,flush=True)
                    break

                # update state
                state.update_state(act_code)
                action += ";"

            print(action)
        turn += 1
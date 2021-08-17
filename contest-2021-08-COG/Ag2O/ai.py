import numpy as np
import json
import os
import sys
import copy
import time
import warnings
warnings.filterwarnings('ignore')

import card

# dqn agent
class DQNAgent:
    def __init__(self):
        self.card_list = []         # card score
        for i in range(160):
            self.card_list.append(card.Card(card_id=i+1))
        self.deck = []              # deck
    
    # load learnd model
    def load_model(self, moji): 
        PATH = os.getcwd()
        with open(PATH + '/Ag2O/bot_model/weights_'+ moji +'.json', 'r') as json_file:
            params = json.load(json_file)

        self.network = {}

        for label, weights in params.items():
            self.network[label] = np.array(weights)
    
    # load card's scores
    def load_score(self, moji):
        PATH = os.getcwd()
        with open(PATH + '/Ag2O/bot_model/cardscores_'+ moji +'.json','r') as json_file:
            cards = json.load(json_file)
        
        for idx, score_list in cards.items():
            idx = int(idx)
            self.card_list[idx-1].id = idx
            self.card_list[idx-1].score = score_list[0]
            self.card_list[idx-1].list_list = score_list[1]
            self.card_list[idx-1].link_score = score_list[2]
    
    # choice the most score of card
    def draft_act(self, state):
        max_value = - 10.0
        choice_idx = 0
        card_num = 0

        # combination
        for idx, card_id in enumerate(state):
            score = self.card_list[card_id-1].score*0.6
            
            link_score = 0.0
            for deck_card_id in self.deck:
                if deck_card_id in self.card_list[card_id-1].link_list:
                    link_score += self.card_list[card_id-1].score*0.4
                if deck_card_id == card_id:
                    link_score -= self.card_list[card_id-1].score*0.4
            
            if len(self.card_list[card_id-1].link_list) > 0:
                link_score = link_score / len(self.card_list[card_id-1].link_list)
            
            score = score + link_score
            print("card_score: ",score,file=sys.stderr,flush=True)

            # choice
            if score > max_value:
                max_value = score
                choice_idx = idx
                card_num = card_id

        self.deck.append(card_num)
        return choice_idx
    
    # choice the action
    def battle_act(self, state, legal_actions):
        #activation function
        tanh = lambda x: np.tanh(x)

        # calculate the Q by neural network
        qs = []
        for la in legal_actions:
            temp = state
            temp = np.append(temp,(la/144))
            
            weights = np.array(self.network[f"DENSE0"])
            temp = np.dot(temp, weights)
            temp = tanh(temp)

            weights = np.array(self.network[f"DENSE2"])
            temp = np.dot(temp, weights)
            temp = tanh(temp)

            weights = np.array(self.network[f"DENSE4"])
            temp = np.dot(temp, weights)
            temp = tanh(temp)

            weights = np.array(self.network[f"DENSE6"])
            temp = np.dot(temp, weights)
            temp = tanh(temp)

            qs.append(temp)
        
        return qs
    
    # greedy search
    def greedy_act(self, state, depth, start_time, legal_actions, card_in_hand):
        current_state = state.get_state()

        qs = self.battle_act(current_state, legal_actions)

        # hp check
        if current_state[0] <= 0:
            return legal_actions[np.argmax(qs)], -1*depth
        if current_state[4] <= 0:
            return legal_actions[np.argmax(qs)], 1*depth
        if depth < 0:
            return legal_actions[np.argmax(qs)], 0

        actions = []
        values = []
        width = len(legal_actions) if len(legal_actions) < 4 else 4

        for _ in range(width):
            values.append(np.max(qs))
            actions.append(legal_actions[np.argmax(qs)])
            qs[np.argmax(qs)] = -1.0
        
        # search
        for i in range(width):
            max_q = -1.0
            state_copy = copy.deepcopy(state)

            act_num = legal_actions[i]
            _, act_code = state_copy.decode_action(act_num,card_in_hand,state_copy.player_lane,state_copy.opponents_lane)

            state_copy.update_state(act_code)
            next_legal_actions = state_copy.get_legal_actions()
            if len(next_legal_actions) > 1:
                del next_legal_actions[0]
            
            if depth > 0:
                _, max_q = self.greedy_act(state_copy,depth-1,start_time,next_legal_actions,card_in_hand)

            values[i] = (max_q + values[i]) / 2
            
            # time up
            if time.time() - start_time > 0.165:
                return legal_actions[np.argmax(values)], np.max(values)
        
        return legal_actions[np.argmax(values)], np.max(values)


if __name__ == "__main__":
    agent = DQNAgent()
    agent.load_model()
    agent.load_score()
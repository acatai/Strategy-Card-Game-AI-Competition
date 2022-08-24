from copy import deepcopy
from model import SCModel
import pickle
import numpy as np
import os
os.environ["CUDA_VISIBLE_DEVICES"]="-1"  

class Card:
    def __init__(self, id: int = -1, instance_id: int = -1, location: int = 0,  type: int = 0,
                 cost: int = 0, attack: int = 0, defense: int = 0, keywords: str = '',
                 my_hp: int = 0, opp_hp: int = 0, draw: int = 0, area: int = 0, can_attack = False):
        self.id = id
        self.instance_id = instance_id
        self.location = location
        self.type = type
        self.cost = cost
        self.attack = attack
        self.defense = defense
        self.keyword = keywords
        self.keywords = set(list(keywords.replace("-", "")))
        self.my_hp = my_hp
        self.opp_hp = opp_hp
        self.draw = draw
        self.area = area
        self.can_attack = can_attack
        self.intensity = self.Intensity()
    
    def __str__(self):
        return 'id' + str(self.instance_id) + 'intensity' + str(self.intensity)
    
    __repr__ = __str__
    
    def IsEmpty(self) -> bool:
        return True if self.id == -1 else False

    def HasAbility(self, keyword: str) -> bool:
        return keyword in self.keywords

    def RemoveAbility(self, ability):
        if isinstance(ability, set):
            self.keywords = self.keywords - ability
        elif isinstance(ability, str):
            ability = set(ability)
            self.keywords = self.keywords - ability

    def AddAbility(self, ability):
        if isinstance(ability, set):
            self.keywords = self.keywords | ability
        elif isinstance(ability, str):
            ability = set(ability)
            self.keywords = self.keywords | ability

    def Card2Matrix(self) -> list:
        '''
        每张卡牌15维信息
        '''
        if self.id == -1:
            return [0.0] * 15
        
        keywords_M = [0.0] * 6
        for i in range(len(self.keywords)):
            if self.keyword[i] != '-':
                keywords_M[i] = 1.0
        return [(self.type + 1)/5, (self.location + 1)/5, (self.area + 1)/3, (self.cost + 1)/13, (self.attack + 1)/20, (self.defense + 1)/20] + \
                keywords_M + [(self.my_hp + 1)/5, (self.opp_hp + 1)/5, (self.draw + 1)/7]

    def Intensity(self):
        if self.id == -1:
            return 0

        attack_adv=7.851177531588
        defense_adv=6.897344834022
        draw_strength=-1.080735136721
        myhp_strength=0.26025185005359
        opphp_strength=-8.577825200648
        area_strength=4.332644071123
        type_strength=2.4854152882320
        cost_strength=-7.862590566574
        B_strength=-8.630110012455
        C_strength=3.486426491993
        G_strength=-3.106492424095
        D_strength=0.7981755245809
        L_strength=-2.1397474107089
        W_strength=-5.630508048635
        LW_strength=-8.259745581540
        GW_strength=4.965336276901
        CL_strength=-0.790584975607
        intensity = 0
        base_cost = int(self.cost * (0.7 if self.area != 0 else 1) - self.draw //2 - self.my_hp//2 - abs(self.opp_hp)//2 - len(self.keywords) + 1)
        intensity += (abs(self.attack) - base_cost) * attack_adv + (abs(self.defense) - base_cost) * defense_adv
        intensity += draw_strength * self.draw + myhp_strength * self.my_hp + opphp_strength * int(self.opp_hp) + area_strength * self.area + type_strength * self.type + cost_strength * self.cost
        intensity += B_strength if 'B' in self.keywords else 0
        intensity += C_strength if 'C' in self.keywords else 0
        intensity += G_strength if 'G' in self.keywords else 0
        intensity += D_strength if 'D' in self.keywords else 0
        intensity += L_strength if 'L' in self.keywords else 0
        intensity += W_strength if 'W' in self.keywords else 0
        intensity += LW_strength if 'W' in self.keywords and 'L' in self.keywords else 0
        intensity += GW_strength if 'W' in self.keywords and 'G' in self.keywords else 0
        intensity += CL_strength if 'C' in self.keywords and 'L' in self.keywords else 0

        return intensity


class HandCards:
    def __init__(self) -> None:
        self.my_hand_maxnum = 8
        self.my_hand_empty_flag = 0
        self.my_hand_cards = [Card() for _ in range(self.my_hand_maxnum)]
    
    def __getitem__(self, index):
        return self.my_hand_cards[index]  

    def AddCard(self, card_id, instance_id, location, card_type, cost, attack, defense, keywords, my_health, opponent_health, card_draw, area) -> None:
        self.my_hand_cards[self.my_hand_empty_flag] = Card(card_id, instance_id, location, card_type, cost, attack, defense, keywords, my_health, opponent_health, card_draw, area)
        self.my_hand_empty_flag += 1

    def PopCard(self, index):
        res = self.my_hand_cards.pop(index)
        self.my_hand_cards.append(Card())
        self.my_hand_empty_flag -= 1
        return res

    def Card2Matrix(self):
        res = []
        for i in range(self.my_hand_maxnum):
            res += self.my_hand_cards[i].Card2Matrix()
        return res


class BoardCards:
    def __init__(self) -> None:
        self.board_maxnum = 3
        self.my_left_board_cards = [Card() for _ in range(self.board_maxnum)]
        self.my_right_board_cards = [Card() for _ in range(self.board_maxnum)]
        self.opp_left_board_cards = [Card() for _ in range(self.board_maxnum)]
        self.opp_right_board_cards = [Card() for _ in range(self.board_maxnum)]
        self.my_left_board_empty_flag = 0
        self.my_right_board_empty_flag = 0
        self.opp_left_board_empty_flag = 0
        self.opp_right_board_empty_flag = 0
        self.num_replica = 0

    def __getitem__(self, index):
        if 0 <= index < 3:
            return self.my_left_board_cards[index]  
        elif 3 <= index < 6:
            return self.my_right_board_cards[index%3]  
        elif 6 <= index < 9:
            return self.opp_left_board_cards[index%3]  
        elif 9 <= index < 12:
            return self.opp_right_board_cards[index%3]  
        else:
            return Card()

    def AddCard(self, card_id, instance_id, location, card_type, cost, attack, defense, keywords, my_health, opponent_health, card_draw, area) -> None:
        can_attack = True
        if instance_id > 60 and instance_id - 60 > self.num_replica:
            self.num_replica = instance_id - 60
        if location == 1:
            self.my_left_board_cards[self.my_left_board_empty_flag] = Card(card_id, instance_id, location, card_type, cost, attack, defense, keywords, my_health, opponent_health, card_draw, area, can_attack)
            self.my_left_board_empty_flag += 1
        elif location == 2:
            self.my_right_board_cards[self.my_right_board_empty_flag] = Card(card_id, instance_id, location, card_type, cost, attack, defense, keywords, my_health, opponent_health, card_draw, area, can_attack)
            self.my_right_board_empty_flag += 1
        elif location == 3:
            self.opp_left_board_cards[self.opp_left_board_empty_flag] = Card(card_id, instance_id, location, card_type, cost, attack, defense, keywords, my_health, opponent_health, card_draw, area, can_attack)
            self.opp_left_board_empty_flag += 1
        elif location == 4:
            self.opp_right_board_cards[self.opp_right_board_empty_flag] = Card(card_id, instance_id, location, card_type, cost, attack, defense, keywords, my_health, opponent_health, card_draw, area, can_attack)
            self.opp_right_board_empty_flag += 1

    def PopCard(self, index):
        res = Card()
        index -= 9
        if 0 <= index < 3:
            res = self.my_left_board_cards.pop(index)
            self.my_left_board_cards.append(Card())
            self.my_left_board_empty_flag -= 1
        elif 3 <= index < 6:
            res = self.my_right_board_cards.pop(index%3)
            self.my_right_board_cards.append(Card())
            self.my_right_board_empty_flag -= 1
        elif 6 <= index < 9:
            res = self.opp_left_board_cards.pop(index%3)
            self.opp_left_board_cards.append(Card())
            self.opp_left_board_empty_flag -= 1
        elif 9 <= index < 12:
            res = self.opp_right_board_cards.pop(index%3)
            self.opp_right_board_cards.append(Card())
            self.opp_right_board_empty_flag -= 1
        return res

    def GetCards(self, lane):
        if lane == 0:
            return self.my_right_board_cards
        elif lane == 1:
            return self.my_left_board_cards
        else:
            return self.my_left_board_cards + self.my_right_board_cards

    def SummonCard(self, card: Card, lane):
        sum_numb = 1
        if card.area == 0:
            if lane == 1:
                card.location = 1
                self.my_left_board_cards[self.my_left_board_empty_flag] = card
                self.my_left_board_empty_flag += 1
            elif lane == 0:
                card.location = 2
                self.my_right_board_cards[self.my_right_board_empty_flag] = card
                self.my_right_board_empty_flag += 1
        elif card.area == 1:
            if lane == 1:
                card.location = 1
                self.my_left_board_cards[self.my_left_board_empty_flag] = card
                self.my_left_board_empty_flag += 1
                if self.my_left_board_empty_flag <= 2:
                    self.num_replica += 1
                    new_card = Card(card.id, 60 + self.num_replica, 2, card.type, card.cost,
                                    card.attack, card.defense, card.keyword, card.my_hp,
                                    card.opp_hp, card.draw, card.area, card.can_attack)
                    self.my_left_board_cards[self.my_left_board_empty_flag] = new_card
                    self.my_left_board_empty_flag += 1
                    sum_numb += 1
            elif lane == 0:
                card.location = 2
                self.my_right_board_cards[self.my_right_board_empty_flag] = card
                self.my_right_board_empty_flag += 1
                if self.my_right_board_empty_flag <= 2:
                    self.num_replica += 1
                    new_card = Card(card.id, 60 + self.num_replica, 1, card.type, card.cost,
                                    card.attack, card.defense, card.keyword, card.my_hp,
                                    card.opp_hp, card.draw, card.area, card.can_attack)
                    self.my_right_board_cards[self.my_right_board_empty_flag] = new_card
                    self.my_right_board_empty_flag += 1
                    sum_numb += 1
        elif card.area == 2:
            if lane == 1:
                card.location = 1
                self.my_left_board_cards[self.my_left_board_empty_flag] = card
                self.my_left_board_empty_flag += 1
                if self.my_right_board_empty_flag <= 2:
                    self.num_replica += 1
                    new_card = Card(card.id, 60 + self.num_replica, 2, card.type, card.cost,
                                    card.attack, card.defense, card.keyword, card.my_hp,
                                    card.opp_hp, card.draw, card.area, card.can_attack)
                    self.my_right_board_cards[self.my_right_board_empty_flag] = new_card
                    self.my_right_board_empty_flag += 1
                    sum_numb += 1
            elif lane == 0:
                card.location = 2
                self.my_right_board_cards[self.my_right_board_empty_flag] = card
                self.my_right_board_empty_flag += 1
                if self.my_left_board_empty_flag <= 2:
                    self.num_replica += 1
                    new_card = Card(card.id, 60 + self.num_replica, 1, card.type, card.cost,
                                    card.attack, card.defense, card.keyword, card.my_hp,
                                    card.opp_hp, card.draw, card.area, card.can_attack)
                    self.my_left_board_cards[self.my_left_board_empty_flag] = new_card
                    self.my_left_board_empty_flag += 1
                    sum_numb += 1
        return sum_numb
    
    def Card2Matrix(self):
        res = []
        for i in range(self.board_maxnum):
            res += self.my_left_board_cards[i].Card2Matrix()
        for i in range(self.board_maxnum):
            res += self.my_right_board_cards[i].Card2Matrix()
        for i in range(self.board_maxnum):
            res += self.opp_left_board_cards[i].Card2Matrix()
        for i in range(self.board_maxnum):
            res += self.opp_right_board_cards[i].Card2Matrix()
        return res


class AllCards:
    def __init__(self) -> None:
        self.hand_cards = HandCards()
        self.board_cards = BoardCards()

    def __getitem__(self, index):
        if 0 <= index < 8:
            return self.hand_cards[index]  
        elif 8 <= index < 20:
            return self.board_cards[index-8]
        else:
            return Card()

    def _get_hand_cards(self) -> HandCards:
        return self.hand_cards
        
    def _get_board_cards(self) -> BoardCards:
        return self.board_cards

    def AddCards(self, card_info: str):
        card_id, instance_id, location, card_type, cost, attack, defense, keywords, my_health, opponent_health, card_draw, area, lane = card_info.split()
        if location == '0':
            location = 0
            self.hand_cards.AddCard(int(card_id), int(instance_id), int(location), int(card_type), int(cost), int(attack), int(defense), keywords, int(my_health), int(opponent_health), int(card_draw), int(area))
        else:
            if location == '1' and lane == '1':
                location = 1
            elif location == '1' and lane == '0':
                location = 2
            elif location == '-1' and lane == '1':
                location = 3
            elif location == '-1' and lane == '0':
                location = 4
            self.board_cards.AddCard(int(card_id), int(instance_id), int(location), int(card_type), int(cost), int(attack), int(defense), keywords, int(my_health), int(opponent_health), int(card_draw), int(area))

    def Card2Matrix(self):
        return self.hand_cards.Card2Matrix() + self.board_cards.Card2Matrix()

    def Summon(self, origin, target):
        opp_health_ch = 0
        my_health_ch = 0
        my_draw_inc = 0
        mana_ch = 0
        card = self.hand_cards.PopCard(origin)
        mana_ch = card.cost
        if card.HasAbility('C'):
            card.can_attack = True
        sum_numb = self.board_cards.SummonCard(card, target)
        opp_health_ch = card.opp_hp * sum_numb
        my_health_ch = card.my_hp * sum_numb
        my_draw_inc = card.draw * sum_numb
        return opp_health_ch, my_health_ch, my_draw_inc, mana_ch

    def Use(self, origin, target):
        demage2opp = 0
        healing2my = 0
        my_draw_inc = 0
        mana_ch = 0
        origin_card = self.hand_cards.PopCard(origin)
        mana_ch = origin_card.cost
        use_numb = 0
        if target != -1:
            if origin_card.area == 0:
                target_card = self.board_cards[target-9]
                target_card.attack += origin_card.attack
                target_card.attack = 0 if target_card.attack < 0 else target_card.attack
                if origin_card.type == 1:
                    target_card.AddAbility(origin_card.keywords)
                elif origin_card.type == 2:
                    target_card.RemoveAbility(origin_card.keywords)
                if target_card.HasAbility('W') and origin_card.defense < 0:
                    target_card.RemoveAbility('W')
                else:
                    target_card.defense += origin_card.defense
                if target_card.defense <= 0:
                    self.board_cards.PopCard(target)
                use_numb += 1  
            elif origin_card.area == 1:
                if origin_card.type == 1:
                    target_card_num = [self.board_cards.my_left_board_empty_flag, self.board_cards.my_right_board_empty_flag]
                    target_lane = (target-9)//3%2
                    for j in range(target_card_num[target_lane]):
                        self.board_cards[target_lane*3+j].attack += origin_card.attack
                        self.board_cards[target_lane*3+j].defense += origin_card.defense
                        self.board_cards[target_lane*3+j].AddAbility(origin_card.keywords)
                        use_numb += 1
                else:
                    target_card_num = [self.board_cards.opp_left_board_empty_flag, self.board_cards.opp_right_board_empty_flag]
                    target_lane = (target-15)//3%2
                    pop_list = []

                    for j in range(target_card_num[target_lane]):
                        self.board_cards[6+target_lane*3+j].attack += origin_card.attack
                        self.board_cards[6+target_lane*3+j].attack = 0 if self.board_cards[6+target_lane*3+j].attack < 0 else self.board_cards[6+target_lane*3+j].attack
                        self.board_cards[6+target_lane*3+j].RemoveAbility(origin_card.keywords)
                        if self.board_cards[6+target_lane*3+j].HasAbility('W') and origin_card.defense < 0:
                            self.board_cards[6+target_lane*3+j].RemoveAbility('W')
                        else:
                            self.board_cards[6+target_lane*3+j].defense += origin_card.defense
                        if self.board_cards[6+target_lane*3+j].defense <= 0:
                            pop_list.append(15+target_lane*3+j)
                        use_numb += 1
                    for i in pop_list[::-1]:
                        self.board_cards.PopCard(i)
            elif origin_card.area == 2:
                if origin_card.type == 1:
                    target_card_num = [self.board_cards.my_left_board_empty_flag, self.board_cards.my_right_board_empty_flag]
                    for i in range(2):
                        for j in range(target_card_num[i]):
                            self.board_cards[i*3+j].attack += origin_card.attack
                            self.board_cards[i*3+j].defense += origin_card.defense
                            self.board_cards[i*3+j].AddAbility(origin_card.keywords)
                            use_numb += 1
                else:
                    target_card_num = [self.board_cards.opp_left_board_empty_flag, self.board_cards.opp_right_board_empty_flag]
                    pop_list = []
                    for i in range(2):
                        for j in range(target_card_num[i]):
                            self.board_cards[6+i*3+j].attack += origin_card.attack
                            self.board_cards[6+i*3+j].attack = 0 if self.board_cards[6+i*3+j].attack < 0 else self.board_cards[6+i*3+j].attack
                            self.board_cards[6+i*3+j].RemoveAbility(origin_card.keywords)
                            if self.board_cards[6+i*3+j].HasAbility('W') and origin_card.defense < 0:
                                self.board_cards[6+i*3+j].RemoveAbility('W')
                            else:
                                self.board_cards[6+i*3+j].defense += origin_card.defense
                            if self.board_cards[6+i*3+j].defense <= 0:
                                pop_list.append(15+i*3+j)
                            use_numb += 1
                    for i in pop_list[::-1]:
                        self.board_cards.PopCard(i)
        else:
            use_numb = 1
            demage2opp += abs(origin_card.defense)
        demage2opp += abs(origin_card.opp_hp) * use_numb
        healing2my += origin_card.my_hp * use_numb
        my_draw_inc += origin_card.draw * use_numb

        return demage2opp, healing2my, my_draw_inc, mana_ch

    def Attack(self, origin, target):
        demage2opp = 0
        healing2my = 0
        is_origin_dead = False
        is_target_dead = False
        origin_card = self.board_cards[origin-9]
        if target == -1:
            demage2opp += origin_card.attack
            if origin_card.HasAbility('D'):
                healing2my += origin_card.attack
            origin_card.can_attack = False
        else:
            target_card = self.board_cards[target-9]
            if origin_card.HasAbility('W') and target_card.HasAbility('W'):
                if target_card.attack != 0:
                    origin_card.RemoveAbility('W')
                if origin_card.attack != 0:
                    target_card.RemoveAbility('W')
            elif origin_card.HasAbility('W') and not target_card.HasAbility('W'):
                # 我方生物变化
                if target_card.attack != 0:
                    origin_card.RemoveAbility('W')
                if origin_card.HasAbility('D'):
                    healing2my += origin_card.attack
                # 敌方生物变化
                if (origin_card.HasAbility('L') and origin_card.attack != 0) or origin_card.attack >= target_card.defense:
                    is_target_dead = True
                    if origin_card.HasAbility('B') and origin_card.attack > target_card.defense:
                        demage2opp += origin_card.attack - target_card.defense
                else:
                    target_card.defense -= origin_card.attack
            elif not origin_card.HasAbility('W') and target_card.HasAbility('W'):
                # 我方生物变化
                if (target_card.HasAbility('L') and target_card.attack != 0) or target_card.attack >= origin_card.defense:
                    is_origin_dead = True
                else:
                    origin_card.defense -= target_card.attack
                # 敌方生物变化
                if origin_card.attack != 0:
                    target_card.RemoveAbility('W')
            else:
                # 我方生物变化
                if (target_card.HasAbility('L') and target_card.attack != 0) or target_card.attack >= origin_card.defense:
                    is_origin_dead = True
                else:
                    origin_card.defense -= target_card.attack
                if origin_card.HasAbility('D'):
                    healing2my += origin_card.attack
                # 敌方生物变化
                if (origin_card.HasAbility('L') and origin_card.attack != 0) or origin_card.attack >= target_card.defense:
                    is_target_dead = True
                    if origin_card.HasAbility('B') and origin_card.attack > target_card.defense:
                        demage2opp += origin_card.attack - target_card.defense
                else:
                    target_card.defense -= origin_card.attack
            if is_origin_dead:
                self.board_cards.PopCard(origin)
            else:
                origin_card.can_attack = False
            if is_target_dead:
                self.board_cards.PopCard(target)

        return demage2opp, healing2my


class State:
    def __init__(self, game_input, num_replica, pos) -> None:
        self.all_cards = AllCards()
        self.all_cards.board_cards.num_replica = num_replica
        
        self.my_health, self.my_mana, self.my_deck, self.my_draw = map(int, game_input[0].split())
        self.my_draw = 1
        self.opp_health, self.opp_mana, self.opp_deck, self.opp_draw = map(int, game_input[1].split())
        self.opp_draw_origin = self.opp_draw
        self.opp_hand_num, self.opp_actions = map(int, game_input[2].split())

        cards = game_input[4 + self.opp_actions:]
        for card in cards:
            self.all_cards.AddCards(card)

        self.round_start_opp_health = self.opp_health
        self.round_start_mana = self.my_mana
        self.pos = pos
        
    def Info2Matrix(self) -> list:
        return [self.my_health/40, self.my_mana/13, self.my_deck/30, self.my_draw/6, 
                self.opp_health/40, self.opp_mana/13, self.opp_deck/30, self.opp_draw/6,
                self.round_start_opp_health/40, self.round_start_mana/13, self.opp_hand_num/8, self.pos]

    def State2Matrix(self) -> list:
        return self.Info2Matrix() + self.all_cards.Card2Matrix()

    def LegalAction(self) -> list:
        legal_action = [0]*145
        legal_action[0] = 1
        hand_cards = self.all_cards._get_hand_cards()
        board_cards = self.all_cards._get_board_cards()
        for i in range(hand_cards.my_hand_empty_flag):
            if hand_cards[i].cost <= self.my_mana: # SUMMON & USE
                if hand_cards[i].type == 0: # 生物
                    if board_cards.my_left_board_empty_flag <= 2:
                        legal_action[i+9] = 1
                    if board_cards.my_right_board_empty_flag <= 2:
                        legal_action[i+1] = 1
                elif hand_cards[i].type == 1: # 绿物品
                    for j in range(board_cards.my_left_board_empty_flag):
                        legal_action[i*13+17+(j+1)] = 1
                    for j in range(board_cards.my_right_board_empty_flag):
                        legal_action[i*13+17+(j+4)] = 1
                elif hand_cards[i].type == 2: # 红物品
                    for j in range(board_cards.opp_left_board_empty_flag):
                        legal_action[i*13+17+(j+7)] = 1
                    for j in range(board_cards.opp_right_board_empty_flag):
                        legal_action[i*13+17+(j+10)] = 1
                elif hand_cards[i].type == 3: # 蓝物品
                    legal_action[i*13+17] = 1
                    if hand_cards[i].defense != 0:
                        for j in range(board_cards.opp_left_board_empty_flag):
                            legal_action[i*13+17+(j+7)] = 1
                        for j in range(board_cards.opp_right_board_empty_flag):
                            legal_action[i*13+17+(j+10)] = 1

        guard_creatures = []
        for j in range(board_cards.opp_left_board_empty_flag):
            if board_cards.opp_left_board_cards[j].HasAbility('G'):
                guard_creatures.append(j)
        for i in range(board_cards.my_left_board_empty_flag):
            if board_cards.my_left_board_cards[i].can_attack:
                if len(guard_creatures) == 0:
                    legal_action[i*4+121] = 1
                    for j in range(board_cards.opp_left_board_empty_flag):
                        legal_action[i*4+121+j+1] = 1
                else:
                    for j in guard_creatures:
                        legal_action[i*4+121+j+1] = 1

        guard_creatures = []
        for j in range(board_cards.opp_right_board_empty_flag):
            if board_cards.opp_right_board_cards[j].HasAbility('G'):
                guard_creatures.append(j)
        for i in range(board_cards.my_right_board_empty_flag):
            if board_cards.my_right_board_cards[i].can_attack:
                if len(guard_creatures) == 0:
                    legal_action[i*4+133] = 1
                    for j in range(board_cards.opp_right_board_empty_flag):
                        legal_action[i*4+133+j+1] = 1
                else:
                    for j in guard_creatures:
                        legal_action[i*4+133+j+1] = 1
        
        return legal_action

    def Act(self, index: int) -> None:
        if index == 0:
            return
        elif 1 <= index <= 16:
            opp_health_ch, my_health_ch, my_draw_inc, mana_ch = self.all_cards.Summon((index-1)%8, index//9)
            self.my_mana -= mana_ch
            self.my_health += my_health_ch
            self.my_draw += my_draw_inc
            self.opp_health += opp_health_ch
            self.opp_draw = self.opp_draw_origin + ((self.round_start_opp_health - self.opp_health)//5 if self.round_start_opp_health - self.opp_health > 0 else 0)
        elif 17 <= index <= 120:
            demage2opp, healing2my, my_draw_inc, mana_ch = self.all_cards.Use((index-17)//13, (index-17)%13 + 8 if (index-17)%13 != 0 else -1)
            self.my_mana -= mana_ch
            self.my_health += healing2my
            self.my_draw += my_draw_inc
            self.opp_health -= demage2opp
            self.opp_draw = self.opp_draw_origin + ((self.round_start_opp_health - self.opp_health)//5 if self.round_start_opp_health - self.opp_health > 0 else 0)
        elif 121 <= index <= 144:
            if index < 133:
                demage2opp, healing2my = self.all_cards.Attack((index-121)//4+9, (index-121)%4+14 if (index-121)%4 != 0 else -1)
            else:
                demage2opp, healing2my = self.all_cards.Attack((index-121)//4+9, (index-121)%4+17 if (index-121)%4 != 0 else -1)
            self.my_health += healing2my
            self.opp_health -= demage2opp
            self.opp_draw = self.opp_draw_origin + ((self.round_start_opp_health - self.opp_health)//5 if self.round_start_opp_health - self.opp_health > 0 else 0)

    def Pos2InstanceID(self, pos) -> int:
        return self.all_cards[pos-1].instance_id if pos != -1 else -1

    def ActionIndex2Str(self, index: int) -> str:
        if 1 <= index <= 16:
            return f'SUMMON {self.Pos2InstanceID((index-1) % 8 + 1)} {index // 9}'
        elif 17 <= index <= 120:
            return f'USE {self.Pos2InstanceID((index-17)//13 + 1)} {self.Pos2InstanceID((index-17)%13 + 8 if (index-17)%13 != 0 else -1)}'
        elif 121 <= index <= 144:
            if index < 133:
                return f'ATTACK {self.Pos2InstanceID((index-121)//4+9)} {self.Pos2InstanceID((index-121)%4 + 14 if (index-121)%4 != 0 else -1)}'
            else:
                return f'ATTACK {self.Pos2InstanceID((index-121)//4+9)} {self.Pos2InstanceID((index-121)%4 + 17 if (index-121)%4 != 0 else -1)}'
        else:
            return 'PASS'
            
    def IsFinish(self):
        return self.opp_health <= 0


def ReadGameInput() -> list:
    '''
    读取游戏输入, 每项输入的详细解释见官网
    return: gamecore每回合传给agent的输入
    '''
    # player's & opponent's info
    game_input = [input(), input()]

    # number of cards in the opponent's hand, number of opponent's action last turn
    opp_hand, opp_actions = [int(i) for i in input().split()]
    game_input.append(f"{opp_hand} {opp_actions}")

    # all opponent actions
    for _ in range(opp_actions):
        game_input.append(input())

    # number of cards on the board and in the player's hand
    card_count = int(input())
    game_input.append(str(card_count))

    # all cards
    for _ in range(card_count):
        game_input.append(input())

    return game_input


def ConvertCardInfo(game_input):
    card_list = []
    cards = game_input[4:]
    for card in cards:
        card_id, instance_id, location, card_type, cost, attack, defense, keywords, my_health, opponent_health, card_draw, area, lane = card.split()
        temp = Card(int(card_id), int(instance_id), int(location), int(card_type), int(cost), int(attack), int(defense), keywords, int(my_health), int(opponent_health), int(card_draw), int(area))
        if int(cost) >= 6 or len(card_list) > 50:
            break
        else:
            card_list.append(temp)
        
    card_list.sort(key=lambda card:card.intensity, reverse=True)
    return card_list[:15]


def FindMaxReplicaNum(game_input):
    res = 0
    _, opp_action_num = map(int, game_input[2].split())

    opp_actions = game_input[3:3 + opp_action_num]
    for opp_action in opp_actions:
        _, action_type, origin, _ = opp_action.split()
        if action_type == 'ATTACK':
            if int(origin) > 60:
                res = max((int(origin) - 60), res)
    return res


if __name__ == '__main__':
    # game loop
    num_replica = 0
    agent_pos = -1

    model = SCModel((312,), (145))
    with open('./USTC-gogogo/model.ckpt', 'rb') as f:
        weight = pickle.load(f)
    model.set_weights(weight)
    model.forward(np.random.uniform(size=(1,312)), np.random.uniform(size=(1, 145)))

    while True:
        game_input = ReadGameInput()
        num_replica = max(FindMaxReplicaNum(game_input), num_replica)
        is_constuct_phase = int(game_input[0].split()[1]) == 0
        if is_constuct_phase:
            pick_list = []
            card_list = ConvertCardInfo(game_input)
            for card in card_list:
                pick_list.append(f'CHOOSE {card.id}')
                pick_list.append(f'CHOOSE {card.id}')
            print(';'.join(pick_list))
        else:
            state = State(game_input, num_replica, agent_pos)
            if state.pos == -1:
                if state.my_mana > state.opp_mana:
                    state.pos = 1
                else:
                    state.pos = 0
            action_list = []
            while True:
                if state.my_health <= 0:
                    action_list.append('PASS')
                    break
                if state.IsFinish():
                    action_list.append('PASS')
                    break
                legal_action = state.LegalAction()
                if sum(legal_action) == 1 and legal_action[0] == 1:
                    action_list.append('PASS')
                    break
                else:
                    legal_action[0] = 0
                action, v, p = model.forward([state.State2Matrix()], [legal_action])
                act_index = action[0] 
                action_list.append(state.ActionIndex2Str(act_index))
                if action_list[-1] == 'PASS':
                    break
                state.Act(act_index)
            num_replica = state.all_cards.board_cards.num_replica
            print(';'.join(action_list))

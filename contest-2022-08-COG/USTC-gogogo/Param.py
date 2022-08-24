import sys
from copy import deepcopy

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

# Write an action using print
# To debug: print("Debug messages...", file=sys.stderr, flush=True)
class Card:
    def __init__(self, id: int = -1, instance_id: int = -1, location: int = 0,  type: int = 0,
                 cost: int = 0, attack: int = 0, defense: int = 0, keywords: str = '',
                 my_hp: int = 0, opp_hp: int = 0, draw: int = 0, area: int = 0, PARAM: dict = {}, can_attack = False):
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
        self.PARAM = PARAM
        self.intensity = self.Intensity()
    
    def __str__(self):
        return 'id' + str(self.instance_id)
    
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
    
    def Intensity(self):
        if self.id == -1:
            return 0
        attack_adv = self.PARAM['attack_adv']
        defense_adv = self.PARAM['defense_adv']
        draw_strength = self.PARAM['draw_strength']
        myhp_strength = self.PARAM['myhp_strength']
        opphp_strength = self.PARAM['opphp_strength']
        area_strength = self.PARAM['area_strength']
        type_strength = self.PARAM['type_strength']
        cost_strength = self.PARAM['cost_strength']
        B_strength = self.PARAM['B_strength']
        C_strength = self.PARAM['C_strength']
        G_strength = self.PARAM['G_strength']
        D_strength = self.PARAM['D_strength']
        L_strength = self.PARAM['L_strength']
        W_strength = self.PARAM['W_strength']
        red_strength = self.PARAM['red_strength']
        blue_strength = self.PARAM['blue_strength']

        intensity = 0
        base_cost = int(self.cost * (0.7 if self.area != 0 else 1) - self.draw //2 - self.my_hp//2 - abs(self.opp_hp)//2 - len(self.keywords) + 1)
        intensity += (abs(self.attack) - base_cost) * attack_adv + (abs(self.defense) - base_cost) * defense_adv
        intensity += draw_strength * self.draw + myhp_strength * self.my_hp + opphp_strength * int(self.opp_hp) + area_strength * self.area + type_strength * (self.type+1) + cost_strength * (self.cost+1)
        intensity += B_strength if 'B' in self.keywords else 0
        intensity += C_strength if 'C' in self.keywords else 0
        intensity += G_strength if 'G' in self.keywords else 0
        intensity += D_strength if 'D' in self.keywords else 0
        intensity += L_strength if 'L' in self.keywords else 0
        intensity += W_strength if 'W' in self.keywords else 0
        intensity += red_strength if self.type == 2 else 0
        intensity += blue_strength if self.type == 3 else 0

        return intensity


class HandCards:
    def __init__(self) -> None:
        self.my_hand_maxnum = 8
        self.my_hand_empty_flag = 0
        self.my_hand_cards = [Card() for _ in range(self.my_hand_maxnum)]
    
    def __getitem__(self, index):
        return self.my_hand_cards[index]  

    def AddCard(self, card_id, instance_id, location, card_type, cost, attack, defense, keywords, my_health, opponent_health, card_draw, area, PARAM) -> None:
        self.my_hand_cards[self.my_hand_empty_flag] = Card(card_id, instance_id, location, card_type, cost, attack, defense, keywords, my_health, opponent_health, card_draw, area, PARAM)
        self.my_hand_empty_flag += 1

    def PopCard(self, index):
        res = self.my_hand_cards.pop(index)
        self.my_hand_cards.append(Card())
        self.my_hand_empty_flag -= 1
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

    def AddCard(self, card_id, instance_id, location, card_type, cost, attack, defense, keywords, my_health, opponent_health, card_draw, area, PARAM) -> None:
        can_attack = True
        if instance_id > 60 and instance_id - 60 > self.num_replica:
            self.num_replica = instance_id - 60
        if location == 1:
            self.my_left_board_cards[self.my_left_board_empty_flag] = Card(card_id, instance_id, location, card_type, cost, attack, defense, keywords, my_health, opponent_health, card_draw, area, PARAM, can_attack)
            self.my_left_board_empty_flag += 1
        elif location == 2:
            self.my_right_board_cards[self.my_right_board_empty_flag] = Card(card_id, instance_id, location, card_type, cost, attack, defense, keywords, my_health, opponent_health, card_draw, area, PARAM, can_attack)
            self.my_right_board_empty_flag += 1
        elif location == 3:
            self.opp_left_board_cards[self.opp_left_board_empty_flag] = Card(card_id, instance_id, location, card_type, cost, attack, defense, keywords, my_health, opponent_health, card_draw, area, PARAM, can_attack)
            self.opp_left_board_empty_flag += 1
        elif location == 4:
            self.opp_right_board_cards[self.opp_right_board_empty_flag] = Card(card_id, instance_id, location, card_type, cost, attack, defense, keywords, my_health, opponent_health, card_draw, area, PARAM, can_attack)
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
                                    card.opp_hp, card.draw, card.area, card.PARAM, card.can_attack)
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
                                    card.opp_hp, card.draw, card.area, card.PARAM, card.can_attack)
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
                                    card.opp_hp, card.draw, card.area, card.PARAM, card.can_attack)
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
                                    card.opp_hp, card.draw, card.area, card.PARAM, card.can_attack)
                    self.my_left_board_cards[self.my_left_board_empty_flag] = new_card
                    self.my_left_board_empty_flag += 1
                    sum_numb += 1
        return sum_numb


class AllCards:
    def __init__(self, PARAM) -> None:
        self.hand_cards = HandCards()
        self.board_cards = BoardCards()
        self.PARAM = PARAM

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
            self.hand_cards.AddCard(int(card_id), int(instance_id), int(location), int(card_type), int(cost), int(attack), int(defense), keywords, int(my_health), int(opponent_health), int(card_draw), int(area), self.PARAM)
        else:
            if location == '1' and lane == '1':
                location = 1
            elif location == '1' and lane == '0':
                location = 2
            elif location == '-1' and lane == '1':
                location = 3
            elif location == '-1' and lane == '0':
                location = 4
            self.board_cards.AddCard(int(card_id), int(instance_id), int(location), int(card_type), int(cost), int(attack), int(defense), keywords, int(my_health), int(opponent_health), int(card_draw), int(area), self.PARAM)

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
    def __init__(self, game_input, num_replica, PARAM) -> None:
        self.all_cards = AllCards(PARAM)
        self.PARAM = PARAM
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

    def LegalActions(self):
        '''
        依据当前状态返回可使用的卡以及与之相关的可选动作
        return: [[card, numb, numb, ...], [card, numb, numb, ...], ...] * 3
        '''
        can_summon, can_use, can_attack_left, can_attack_right = [], [], [], []
        hand_cards = self.all_cards.hand_cards
        board_cards = self.all_cards.board_cards
        for i in range(hand_cards.my_hand_empty_flag):
            temp = []
            if hand_cards[i].cost <= self.my_mana: # SUMMON & USE
                temp.append(hand_cards[i])
                if hand_cards[i].type == 0: # 生物
                    if board_cards.my_left_board_empty_flag <= 2:
                        temp.append(i+9)
                    if board_cards.my_right_board_empty_flag <= 2:
                        temp.append(i+1)
                    if len(temp) > 1:
                        can_summon.append(temp)
                else:
                    if hand_cards[i].type == 1:
                        for j in range(board_cards.my_left_board_empty_flag):
                            temp.append(i*13+17+(j+1))
                        for j in range(board_cards.my_right_board_empty_flag):
                            temp.append(i*13+17+(j+4))
                    elif hand_cards[i].type == 2:
                        for j in range(board_cards.opp_left_board_empty_flag):
                            temp.append(i*13+17+(j+7))
                        for j in range(board_cards.opp_right_board_empty_flag):
                            temp.append(i*13+17+(j+10))
                    else:
                        temp.append(i*13+17)
                        if hand_cards[i].defense != 0:
                            for j in range(board_cards.opp_left_board_empty_flag):
                                temp.append(i*13+17+(j+7))
                            for j in range(board_cards.opp_right_board_empty_flag):
                                temp.append(i*13+17+(j+10))
                    if len(temp) > 1:
                        can_use.append(temp)

        guard_creatures = []
        for j in range(board_cards.opp_left_board_empty_flag):
            if board_cards.opp_left_board_cards[j].HasAbility('G'):
                guard_creatures.append(j)
        for i in range(board_cards.my_left_board_empty_flag):
            temp = []
            if board_cards.my_left_board_cards[i].can_attack:
                temp.append(board_cards.my_left_board_cards[i])
                if len(guard_creatures) == 0:
                    temp.append(i*4+121)
                    for j in range(board_cards.opp_left_board_empty_flag):
                        temp.append(i*4+121+j+1)
                else:
                    for j in guard_creatures:
                        temp.append(i*4+121+j+1)
                can_attack_left.append(temp)

        guard_creatures = []
        for j in range(board_cards.opp_right_board_empty_flag):
            if board_cards.opp_right_board_cards[j].HasAbility('G'):
                guard_creatures.append(j)
        for i in range(board_cards.my_right_board_empty_flag):
            temp = []
            if board_cards.my_right_board_cards[i].can_attack:
                temp.append(board_cards.my_right_board_cards[i])
                if len(guard_creatures) == 0:
                    temp.append(i*4+133)
                    for j in range(board_cards.opp_right_board_empty_flag):
                        temp.append(i*4+133+j+1)
                else:
                    for j in guard_creatures:
                        temp.append(i*4+133+j+1)
                can_attack_right.append(temp)
        
        return can_summon, can_use, can_attack_left, can_attack_right

    def ChooseActions(self, can_summon, can_use, can_attack_left, can_attack_right):
        '''
        根据当前状态选择本回合要使用的卡牌, 包括召唤、法术和攻击, 并决定最终采取哪个动作
        return: numb or [numb, numb]
        '''
        if len(can_summon) == 0 and len(can_use) == 0:
            can_attack_all = can_attack_left + can_attack_right
            if len(can_attack_all) == 0:
                return [0]
            else:
                if len(can_attack_all[0]) == 2 and (can_attack_all[0][1] - 133) % 4 == 0: # 只能走脸
                    return [can_attack_all[0][1]]
                else:
                    left_action_numb = -1
                    right_action_numb = -1
                    if len(can_attack_left) != 0:
                        left_action_numb = self.ChooseAttackAction(can_attack_left)
                    if len(can_attack_right) != 0:
                        right_action_numb = self.ChooseAttackAction(can_attack_right)
                    return [left_action_numb, right_action_numb]
        else:
            summon_use = can_summon + can_use
            action_indexs = []
            for card in summon_use:
                action_indexs += card[1:]
            values = []
            for card in summon_use:
                values += self.SummonUseValue(card)
            index = values.index(max(values))
            return [action_indexs[index]]

    def ChooseAttackAction(self, my_cards):
        card_list = []
        action_list = []
        value_list = []
        for card in my_cards:
            card_list.append(card[0])
            for action in card[1:]:
                action_list.append(action)
                if (action-121)%4 == 0:
                    value_list.append(1)
                else:
                    if action < 133:
                        value_list.append(self.AttackValue(card[0], self.all_cards.board_cards[(action-121)%4+5]))
                    else:
                        value_list.append(self.AttackValue(card[0], self.all_cards.board_cards[(action-121)%4+8]))
        index = value_list.index(max(value_list))
        return action_list[index]

    def AttackValue(self, my_card: Card, opp_card: Card):
        is_oppcard_dead = 0
        is_mycard_dead = 0
        opp_card_defense_change = 0
        my_card_defense_change = 0
        opp_hp = 0
        my_hp = 0
        if opp_card.HasAbility('W'):
            is_oppcard_dead = 0
            opp_card_defense_change = 0
        else:
            is_oppcard_dead = (my_card.attack >= opp_card.defense) or (my_card.HasAbility('L') and my_card.attack > 0)
            opp_card_defense_change = my_card.attack if my_card.attack < opp_card.defense else opp_card.defense
        if my_card.HasAbility('W'):
            is_mycard_dead = 0
            my_card_defense_change = 0
        else:
            is_mycard_dead = (opp_card.attack >= my_card.defense)
            my_card_defense_change = opp_card.attack if opp_card.attack < my_card.defense else my_card.defense
        if my_card.HasAbility('D') and not opp_card.HasAbility('W'):
            my_hp = my_card.attack if my_card.attack < opp_card.defense else opp_card.defense
        if my_card.HasAbility('B') and is_oppcard_dead:
            opp_hp = my_card.attack - opp_card.defense
        value = 0
        if is_oppcard_dead:
            value += opp_card.defense/my_card.attack + (my_card.defense/opp_card.attack if opp_card.attack != 0 else 3)
            if opp_card.HasAbility('G'):
                value += 0.3
        else:
            value += opp_card_defense_change / opp_card.defense
        if is_mycard_dead:
            value -= 0.5
        else:
            value -= my_card_defense_change / 2*my_card.defense
        
        value += opp_hp / self.opp_health + my_hp / self.my_health

        return value

    def SummonUseValue(self, card_list):
        value_list = []
        action_indexs = card_list[1:]
        origin_card: Card = card_list[0]
        for action in action_indexs:
            value = origin_card.intensity
            add_creature_numb = 0
            kill_creature_numb = 0
            add_creature_a = 0
            add_creature_d = 0
            weak_creature_a = 0
            weak_creature_d = 0
            mana = 0
            healing2my = 0
            demage2opp = 0
            draw = 0
            if origin_card.type == 0:
                if origin_card.area == 0 or (origin_card.area == 1 and self.CountMyCreature(action//9) == 2) or (origin_card.area == 2 and self.CountMyCreature(1-action//9) == 3):
                    add_creature_numb += 1
                    add_creature_a += origin_card.attack
                    add_creature_d += origin_card.defense
                elif (origin_card.area == 1 and self.CountMyCreature(action//9) < 2) or (origin_card.area == 2 and self.CountMyCreature(1-action//9) < 3):
                    add_creature_numb += 2
                    add_creature_a += origin_card.attack *2
                    add_creature_d += origin_card.defense *2
                mana = origin_card.cost
                healing2my = origin_card.my_hp * add_creature_numb
                demage2opp = abs(origin_card.opp_hp) * add_creature_numb
                draw = origin_card.draw * add_creature_numb
            elif origin_card.type == 1:
                if origin_card.area == 0:
                    target_cards = [self.all_cards.board_cards[(action-17)%13-1]]
                else:
                    if origin_card.area == 1:
                        if (action-17)%13+8 <= 11:
                            target_cards = self.all_cards.board_cards.my_left_board_cards
                        else:
                            target_cards = self.all_cards.board_cards.my_right_board_cards
                    else:
                        target_cards = self.all_cards.board_cards.my_left_board_cards + self.all_cards.board_cards.my_right_board_cards
                numb = len(target_cards)
                add_creature_a = origin_card.attack * numb
                add_creature_d = origin_card.defense * numb
                mana = origin_card.cost
                healing2my = origin_card.my_hp * numb
                demage2opp = abs(origin_card.opp_hp) * numb
                draw = origin_card.draw * numb
            else:
                if (action-17)%13 != 0:
                    if origin_card.area == 0:
                        target_cards = [self.all_cards.board_cards[(action-17)%13-1]]
                    else:
                        if origin_card.area == 1:
                            if (action-17)%13+8 <= 11:
                                target_cards = self.all_cards.board_cards.opp_left_board_cards
                            else:
                                target_cards = self.all_cards.board_cards.opp_right_board_cards
                        else:
                            target_cards = self.all_cards.board_cards.opp_left_board_cards + self.all_cards.board_cards.opp_right_board_cards
                
                    for card in target_cards:
                        if card.HasAbility('W') and not origin_card.HasAbility('W'):
                            pass
                        else:
                            if origin_card.defense > card.defense:
                                kill_creature_numb += 1
                            weak_creature_a += min(origin_card.attack, card.attack)
                            weak_creature_d += min(origin_card.defense, card.defense)
                    numb = len(target_cards)
                    mana = origin_card.cost
                    healing2my = origin_card.my_hp * numb
                    demage2opp = abs(origin_card.opp_hp) * numb
                    draw = origin_card.draw * numb
                else:
                    mana = origin_card.cost
                    healing2my = origin_card.my_hp
                    demage2opp = abs(origin_card.opp_hp) + abs(origin_card.defense)
                    draw = origin_card.draw

            addc_strength = self.PARAM['addc_strength']
            killc_strength = self.PARAM['killc_strength']
            adda_strength = self.PARAM['adda_strength']
            addd_strength = self.PARAM['addd_strength']
            weaka_strength = self.PARAM['weaka_strength']
            weakd_strength = self.PARAM['weakd_strength']
            mana_strength = self.PARAM['mana_strength']
            healm_strength = self.PARAM['healm_strength']
            demageo_strength = self.PARAM['demageo_strength']
            drawa_strength = self.PARAM['drawa_strength']

            value += add_creature_numb * addc_strength +  \
                kill_creature_numb * killc_strength + \
                add_creature_a * adda_strength + \
                add_creature_d * addd_strength + \
                weak_creature_a * weaka_strength + \
                weak_creature_d * weakd_strength + \
                mana * mana_strength + \
                healing2my * healm_strength + \
                demage2opp * demageo_strength + \
                draw * drawa_strength

            value_list.append(value)
        return value_list

    def CountMyCreature(self, lane):
        if lane == 1:
            return self.all_cards.board_cards.my_left_board_empty_flag
        else:
            return self.all_cards.board_cards.my_right_board_empty_flag

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


def ConvertCardInfo(game_input, PARAM):
    card_list = []
    cards = game_input[4:]
    for card in cards:
        card_id, instance_id, location, card_type, cost, attack, defense, keywords, my_health, opponent_health, card_draw, area, lane = card.split()
        temp = Card(int(card_id), int(instance_id), int(location), int(card_type), int(cost), int(attack), int(defense), keywords, int(my_health), int(opponent_health), int(card_draw), int(area), PARAM)
        if int(cost) > 6 or len(card_list) > 55:
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

    param_dict = {'attack_adv': 3.696339007636457, 'defense_adv': 7.05927915421972, 'draw_strength': -3.820332216633692, 'myhp_strength': 8.191440440138717, 'opphp_strength': -8.781690675107924, 'area_strength': 7.535748353994574, 'type_strength': 4.238630415977463, 'cost_strength': -6.369836928981427, 'B_strength': 0.6872959161095196, 'C_strength': 3.345518754196096, 'G_strength': -3.379017862565295, 'D_strength': -0.3740325513432996, 'L_strength': -8.60716251549646, 'W_strength': -2.527781797039319, 'red_strength': 1.7422097943807593, 'blue_strength': 4.394302955700368, 'addc_strength': 1.2021321877738345, 'killc_strength': -5.958362135292816, 'adda_strength': 1.9357493292013537, 'addd_strength': 4.457367350122636, 'weaka_strength': 1.3332767364954385, 'weakd_strength': -8.844627430686227, 'mana_strength': 2.8451125634778425, 'healm_strength': 2.78599689382035, 'demageo_strength': 2.148955506770127, 'drawa_strength': 5.1215244173472225}
    
    while True:
        game_input = ReadGameInput()

        is_constuct_phase = int(game_input[0].split()[1]) == 0
        if is_constuct_phase:
            pick_list = []
            card_list = ConvertCardInfo(game_input, param_dict)
            for card in card_list:
                pick_list.append(f'CHOOSE {card.id}')
                pick_list.append(f'CHOOSE {card.id}')
            print(';'.join(pick_list))
        else:
            num_replica = max(FindMaxReplicaNum(game_input), num_replica)
            state = State(game_input, num_replica, param_dict)
            action_list = []
            while True:
                if state.my_health <= 0:
                    print('IsDead', file=sys.stderr, flush=True)
                    action_list.append('PASS')
                    break
                if state.IsFinish():
                    print('IsFinish', file=sys.stderr, flush=True)
                    action_list.append('PASS')
                    break
                can_summon, can_use, can_attack_left, can_attack_right = state.LegalActions()
                print('legalaction', can_summon, can_use, can_attack_left, can_attack_right, file=sys.stderr, flush=True)
                action_index = state.ChooseActions(can_summon, can_use, can_attack_left, can_attack_right)
                for index in action_index:
                    if index != -1:
                        action = state.ActionIndex2Str(index)
                        action_list.append(action)
                for index in action_index:
                    if index != -1:
                        state.Act(index)
                        print(index , file=sys.stderr, flush=True)

                if action_list[-1] == 'PASS':
                    break
            num_replica = state.all_cards.board_cards.num_replica
            print(';'.join(action_list))

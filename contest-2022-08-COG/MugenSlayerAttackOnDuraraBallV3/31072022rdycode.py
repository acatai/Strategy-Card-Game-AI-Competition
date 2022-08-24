import sys
import math
from enum import Enum
import itertools
from itertools import combinations
# LANE LOGIC AND TARGET LOGIC IS MISSING
# when to put cards in which lane, spread cards to counter area effect 
#when to use area cards to not waste area effect on single cards
#which cards should be targetted first, which boosted first 
# LETHAL LOGIC AND CARD PLACEMENT LOGIC
# dont kill when close to lethal but cant lethal just yet
#what happens if i only have blue cards
#calculate if lethal is close
#check if i can kill cards with spell
#use spells only when worth it both lane spells only when both lanes are full
# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.
class Card():
    def __init__(self, i, card_number, instance_id,location, card_type, cost, attack, defense, abilities, my_health_change, opponent_health_change, card_draw, area, lane, score):
        self.number = str(i) 
        self.card_number = card_number 
        self.instance_id = str(instance_id)
        self.location = location
        self.card_type = card_type
        self.cost = cost
        self.attack = attack
        self.defense = defense
        self.abilities = abilities
        self.my_health_change = my_health_change
        self.opponent_health_change = opponent_health_change
        self.card_draw = card_draw
        self.area = area
        self.lane = lane
        self.score = score

class Player():
    def __init__(self, health, mana, deck, draw, hand, board):
        self.health = health
        self.mana = mana
        self.deck = deck
        self.draw = draw
        self.hand = hand
        self.board = board

class Opponent():
    def __init__(self, health, mana, board):
        self.health = health
        self.mana = mana
        self.board = board
                        

def Attack(id, target_id):
        return "ATTACK " + id + " " + str(target_id)
    
def Summon(id, lane):
        return "SUMMON " + id + " " + str(lane)

def Choose(id):
        return "CHOOSE " + id  

def Use(id, target_id):
        return "USE " + id + " " + str(target_id)         

class Lane(Enum):
    LEFT = 0
    RIGHT = 1

    def __int__(self):
        return self.value

class Area(Enum):
    NONE = 0
    ONELANE = 1
    BOTHLANE = 2

    def __int__(self):
        return self.value

class CardType(Enum):
    MONSTER = 0
    GREEN = 1
    RED = 2
    BLUE = 3

    def __int__(self):
        return self.value

class Location(Enum):
    OPPONENT_BOARD = -1
    PLAYER_HAND = 0
    BOARD = 1

    def __int__(self):
        return self.value

class Ability(Enum):
    BREAKTHROUGH = 'B'
    CHARGE = 'C'
    DRAIN = 'D'
    GUARD = 'G'
    LETHAL = 'L'
    WARD = 'W'      

    def __int__(self):
        return self.value              


def find_sum_in_list(numbers, target):
    results = []
    for x in range(len(numbers)):
        results.extend(
            [   
                combo for combo in combinations(numbers ,x)  
                    if sum(combo) <= target
            ]   
        )   

    print(results)

def find_all_combinations(numbers):
    results = []
    for x in range(len(numbers) + 1):
        results.extend(
            [   
                combo for combo in combinations(numbers ,x)  
            ]   
        )   

    return results

def find_combi(a):
    if len(a) == 0:
        return [[]]
    cs = []
    for c in find_combi(a[1:]):
        cs += [c, c+[a[0]]]
    return cs       

def createScore():
    for card in cards:
        if(card.card_type == int(CardType.MONSTER)):
            card.score = (2*card.attack) + (2*card.defense) - (3*card.cost) + card.my_health_change - card.opponent_health_change
        elif(card.card_type == int(CardType.GREEN)):
            card.score = (2*card.attack) + (2*card.defense) - (3*card.cost) + card.my_health_change - card.opponent_health_change
        elif(card.card_type == int(CardType.RED)):
            card.score = (-2*card.attack) + (-2*card.defense) - (3*card.cost) + card.my_health_change - card.opponent_health_change
        else:
            card.score = (-4*card.defense) - (3*card.cost) + card.my_health_change - card.opponent_health_change




def chooseCardsBasedOnScore():
    count = 0
    cardlist = []
    card2ndRound = []
    for card in cards:    
            if(((card.cost <= 6) & (card.area > 0))):                
                card2ndRound.append(card)    
    card2ndRound = sorted(card2ndRound, key=lambda card: card.score, reverse=True)        
    for card in card2ndRound:
                cardlist.append(Choose(card.number))
                cardlist.append(Choose(card.number))
                count += 2
                if(count ==30):
                    break    
    print(";".join(cardlist))

def chooseCardsBasedOnScoreCap4Mana():
    count = 0
    cardlist = []
    card2ndRound = []
    for card in cards:    
            if(((card.cost <= 4) & (card.area > 0))):                
                card2ndRound.append(card)    
    card2ndRound = sorted(card2ndRound, key=lambda card: card.score, reverse=True)        
    for card in card2ndRound:
                cardlist.append("CHOOSE " + str(card.number))
                cardlist.append("CHOOSE " + str(card.number))
                count += 2
                if(count ==30):
                    break    
    if count < 30:
                for cardA in cards:
                    if ((cardA.cost <= 1) & (cardA.area ==0)):
                        cardlist.append("CHOOSE " + str(cardA.number))
                        #print(str(cardA[7]) + " " +str(cardA[1])+  " " +str(cardA[2])+  " " +str(cardA[3])+  " " +str(cardA[4])+  " " +str(cardA[5]),  file=sys.stderr, flush=True)
                        cardlist.append("CHOOSE " + str(cardA.number))
                        count += 2
                        if(count ==30):
                            break                        
    print(";".join(cardlist))


def DestroyCards():
        if(len(lane0opp) == len(lane1opp)) :
            for cardA in bothLaneSpell:
                    for cardB in cards:
                            actions.append(Use(cardA.instance_id, cardB.instance_id)) 
        if(len(lane0opp) >= len(lane1opp)) :
            for cardA in sameLaneSpell:
                    for cardB in cards:
                        if(cardB in lane0opp):
                            actions.append(Use(cardA.instance_id, cardB.instance_id))
            for cardA in bothLaneSpell:
                    for cardB in cards:
                        if(cardB in lane0opp):
                            actions.append(Use(cardA.instance_id, cardB.instance_id))                  
        else:
            for cardA in sameLaneSpell:
                    for cardB in cards:
                        if(cardB in lane1opp):
                            actions.append(Use(cardA.instance_id, cardB.instance_id))
            for cardA in bothLaneSpell:
                    for cardB in cards:
                        if(cardB in lane1opp):
                            actions.append(Use(cardA.instance_id, cardB.instance_id))    

def getSpellsAboveMinDamage(current_mana, damage_min, bothLanes):
        minList = []
        if(bothLanes == 1):    
            minList = find_combi(bothLaneSpell)
        else:
            minList = find_combi(sameLaneSpell)  
        for tup in minList:
            print("new tuple: " ,  file=sys.stderr, flush=True)  
            for t in tup:
                print("t in tup: " , t.defense, " ", t.instance_id, file=sys.stderr, flush=True)  
        new_list_kai = []
        print("bothlaneSpells: " ,  file=sys.stderr, flush=True)  
        for card in bothLaneSpell:
            print("bothlanespell: " , card.defense, " ", card.instance_id, file=sys.stderr, flush=True)  
        print("sameLaneSpell: " ,  file=sys.stderr, flush=True)  
        for card in sameLaneSpell:
            print("samelanespell: " , card.defense, " ", card.instance_id, file=sys.stderr, flush=True)      
        for tup in minList:
            if(sum(t.cost for t in tup) <= current_mana):
                new_list_kai.append(tup)
        for tup in new_list_kai:
            print("newlistkaiHIGH_managrenze: " ,  file=sys.stderr, flush=True)  
            for t in tup:
                print("mana: " , t.cost, file=sys.stderr, flush=True)         
        spells_higher = []
        for tup in new_list_kai:
            if(sum(abs(t.defense) for t in tup) >= damage_min):
                spells_higher.append(tup)  
        for tup in spells_higher:
            print("spell candidates: " ,  file=sys.stderr, flush=True)  
            for t in tup:
                print("defense of candidate: " , t.defense, file=sys.stderr, flush=True)        
        new_spells_higher = min(spells_higher, key=lambda spells_higher: abs(sum(card.defense for card in spells_higher)), default = [])  
        if (len(new_spells_higher) == 0) & (len(spells_higher) == 0):
            return []
        if (len(new_spells_higher) == 0) & (len(spells_higher) > 0):
            return spells_higher[0] 
        for spell in new_spells_higher:
            if bothLanes == 1:
                bothLaneSpell.remove(spell)
            else:
                sameLaneSpell.remove(spell)       
        return new_spells_higher

def getSpellsBelowMinDamage(current_mana, damage_min, bothLanes):
        minList = []
        if(bothLanes == 1):    
            minList = find_combi(bothLaneSpell)
        else:
            minList = find_combi(sameLaneSpell)  
        new_list_kai = []

        for tup in minList:
            print("new tuple: " ,  file=sys.stderr, flush=True)  
            for t in tup:
                print("t in tup: " , t.defense, " ", t.instance_id, file=sys.stderr, flush=True) 
        for tup in minList:
            if(sum(t.cost for t in tup) <= current_mana):
                new_list_kai.append(tup)
        for tup in new_list_kai:
            print("newlistkaiLOWER_managrenze: " ,  file=sys.stderr, flush=True)  
            for t in tup:
                print("mana: " , t.cost, file=sys.stderr, flush=True)   
        spells_lower = []
        for tup in new_list_kai:
            if(sum(abs(t.defense) for t in tup) < damage_min):
                spells_lower.append(tup)  
        for tup in spells_lower:
            print("spell candidates: " ,  file=sys.stderr, flush=True)  
            for t in tup:
                print("defense of candidate: " , t.defense, file=sys.stderr, flush=True)            
        new_spells_lower = max(spells_lower, key=lambda spells_lower: abs(sum(card.defense for card in spells_lower)), default = [])  
        if (len(new_spells_lower) == 0) & (len(spells_lower) == 0):
            return []
        
        if (len(new_spells_lower) == 0) & (len(spells_lower) > 0):
            return spells_lower[0]
        #maybe add this for spells lower as well    
        for spell in new_spells_lower:
            if bothLanes == 1:
                bothLaneSpell.remove(spell)
            else:
                 sameLaneSpell.remove(spell)     
        return new_spells_lower

#check for ward, still not working
#what happens if you only have samelane spells and monsters on different lanes
def DestroyCardsV2(current_mana, damage_min, card_to_beat):
    if('W' in card_to_beat.abilities):
        card_to_beat.abilities = card_to_beat.abilities.replace('W', '-')
        current_mana = DestroyCardsV2(current_mana, 0, card_to_beat)
    mana_needed = 0
    if((len(lane0opp) != 0) & (len(lane1opp) != 0)):
        spells_higher = getSpellsAboveMinDamage(current_mana, damage_min, 1)
        spells_lower = getSpellsBelowMinDamage(current_mana, damage_min, 1)
        print("spellshigher: ", len(spells_higher) ,  file=sys.stderr, flush=True)
        print("spellslower: ", len(spells_lower) ,  file=sys.stderr, flush=True)
        if len(spells_higher) == 0 :
            for card in spells_lower:
                actions.append(Use(card.instance_id, card_to_beat.instance_id))
                print("spelluse1: " ,  file=sys.stderr, flush=True)
    
                mana_needed = mana_needed + card.cost
                damage_min = damage_min + card.defense
            current_mana = current_mana - mana_needed
            spells_higher = getSpellsAboveMinDamage(current_mana, damage_min, 0)
            spells_lower = getSpellsBelowMinDamage(current_mana, damage_min, 0)
            print("spellshigher: ", len(spells_higher) ,  file=sys.stderr, flush=True)
            print("spellslower: ", len(spells_lower) ,  file=sys.stderr, flush=True)
            if len(spells_higher) == 0 :
                    for card in spells_lower:
                        actions.append(Use(card.instance_id, card_to_beat.instance_id))
                        print("spelluse2: " ,  file=sys.stderr, flush=True)
                        mana_needed = mana_needed + card.cost
                    current_mana = current_mana - mana_needed
                    return current_mana
            else:
                    for card in spells_higher:
                        actions.append(Use(card.instance_id, card_to_beat.instance_id))
                        print("spelluse3: " ,  file=sys.stderr, flush=True)
                        mana_needed = mana_needed + card.cost
                    current_mana = current_mana - mana_needed
                    return current_mana    

        else:
            
            for card in spells_higher:
                actions.append(Use(card.instance_id, card_to_beat.instance_id))
                print("spelluse4: " ,  file=sys.stderr, flush=True)
                mana_needed = mana_needed + card.cost
            current_mana = current_mana - mana_needed
            return current_mana        

    elif((lane1opp != 0) & (lane0opp != 0)) & (len(bothLaneSpell) == 0):
        damage_min = 0
        highest_defense_card = None
        for card in lane0opp:
            if(card.defense > damage_min):
                damage_min = card.defense
                highest_defense_card = card
                print("defense: " , card.defense,  file=sys.stderr, flush=True)
        if(highest_defense_card != None):        
            current_mana = DestroyCardsV3(current_mana, damage_min, highest_defense_card)
        damage_min = 0
        highest_defense_card = None
        for card in lane1opp:
            if(card.defense > damage_min):
                damage_min = card.defense
                highest_defense_card = card
                print("defense: " , card.defense,  file=sys.stderr, flush=True)
        if(highest_defense_card != None):        
            current_mana = DestroyCardsV3(current_mana, damage_min, highest_defense_card)    
        return current_mana    

    else:
        spells_higher = getSpellsAboveMinDamage(current_mana, damage_min, 0)
        spells_lower = getSpellsBelowMinDamage(current_mana, damage_min, 0)
        spells_higher_bothLanes = getSpellsAboveMinDamage(current_mana, damage_min, 1)
        if((len(spells_higher_bothLanes) != 0) & (len(spells_higher) == 0)):
            for card in spells_higher_bothLanes:
                actions.append(Use(card.instance_id, card_to_beat.instance_id))
                print("spelluse special case: " ,  file=sys.stderr, flush=True)
                mana_needed = mana_needed + card.cost
            current_mana = current_mana - mana_needed
            return current_mana    
        print("spellshigher: ", len(spells_higher) ,  file=sys.stderr, flush=True)
        print("spellslower: ", len(spells_lower) ,  file=sys.stderr, flush=True)
        if (len(spells_higher)) == 0 :
            for card in spells_lower:
                actions.append(Use(card.instance_id, card_to_beat.instance_id))
                print("spelluse5: " ,  file=sys.stderr, flush=True)
                mana_needed = mana_needed + card.cost
                damage_min = damage_min + card.defense
            current_mana = current_mana - mana_needed
            spells_higher = getSpellsAboveMinDamage(current_mana, damage_min, 1)
            spells_lower = getSpellsBelowMinDamage(current_mana, damage_min, 1)
            print("spellshigher: ", len(spells_higher) ,  file=sys.stderr, flush=True)
            print("spellslower: ", len(spells_lower) ,  file=sys.stderr, flush=True)
            if len(spells_higher) == 0 :
                    for card in spells_lower:
                        actions.append(Use(card.instance_id, card_to_beat.instance_id))
                        print("spelluse6: " ,  file=sys.stderr, flush=True)
                        mana_needed = mana_needed + card.cost
                    current_mana = current_mana - mana_needed
                    
                    return current_mana
            else:
                    for card in spells_higher:
                        actions.append(Use(card.instance_id, card_to_beat.instance_id))
                        print("spelluse7: " ,  file=sys.stderr, flush=True)
                        mana_needed = mana_needed + card.cost
                    current_mana = current_mana - mana_needed
                    return current_mana    

        else:
            for card in spells_higher:
                actions.append(Use(card.instance_id, card_to_beat.instance_id))
                print("spelluse8: " ,  file=sys.stderr, flush=True)
                mana_needed = mana_needed + card.cost
            current_mana = current_mana - mana_needed
            return current_mana            

def DestroyCardsV3(current_mana, damage_min, card_to_beat):
        if('W' in card_to_beat.abilities):
            card_to_beat.abilities = card_to_beat.abilities.replace('W', '-')
            current_mana = DestroyCardsV3(current_mana, 0, card_to_beat)
        mana_needed = 0
    
        spells_higher = getSpellsAboveMinDamage(current_mana, damage_min, 1)
        spells_lower = getSpellsBelowMinDamage(current_mana, damage_min, 1)
        print("spellshigher: ", len(spells_higher) ,  file=sys.stderr, flush=True)
        print("spellslower: ", len(spells_lower) ,  file=sys.stderr, flush=True)
        if len(spells_higher) == 0 :
            for card in spells_lower:
                actions.append(Use(card.instance_id, card_to_beat.instance_id))
                print("spelluse1: " ,  file=sys.stderr, flush=True)
    
                mana_needed = mana_needed + card.cost
                damage_min = damage_min + card.defense
            current_mana = current_mana - mana_needed
            spells_higher = getSpellsAboveMinDamage(current_mana, damage_min, 0)
            spells_lower = getSpellsBelowMinDamage(current_mana, damage_min, 0)
            print("spellshigher: ", len(spells_higher) ,  file=sys.stderr, flush=True)
            print("spellslower: ", len(spells_lower) ,  file=sys.stderr, flush=True)
            if len(spells_higher) == 0 :
                    for card in spells_lower:
                        actions.append(Use(card.instance_id, card_to_beat.instance_id))
                        print("spelluse2: " ,  file=sys.stderr, flush=True)
                        mana_needed = mana_needed + card.cost
                    current_mana = current_mana - mana_needed
                    return current_mana
            else:
                    for card in spells_higher:
                        actions.append(Use(card.instance_id, card_to_beat.instance_id))
                        print("spelluse3: " ,  file=sys.stderr, flush=True)
                        mana_needed = mana_needed + card.cost
                    current_mana = current_mana - mana_needed
                    return current_mana    

        else:
            
            for card in spells_higher:
                actions.append(Use(card.instance_id, card_to_beat.instance_id))
                print("spelluse4: " ,  file=sys.stderr, flush=True)
                mana_needed = mana_needed + card.cost
            current_mana = current_mana - mana_needed
            return current_mana              
    

# game loop
while True:
    #inputinput = input()
    for i in range(2):
        player_health, player_mana, player_deck, player_draw = [int(j) for j in input().split()]
    opponent_hand, opponent_actions = [int(i) for i in input().split()]
    cards = []  
    cardsOld = []
    cardsNew = []
    for i in range(opponent_actions):
        card_number_and_action = input()
    card_count = int(input())
   
    for i in range(card_count):
        inputs = input().split()
        card_number = int(inputs[0])
        instance_id = int(inputs[1])
        location = int(inputs[2])
        card_type = int(inputs[3])
        cost = int(inputs[4])
        attack = int(inputs[5])
        defense = int(inputs[6])
        abilities = inputs[7]
        my_health_change = int(inputs[8])
        opponent_health_change = int(inputs[9])
        card_draw = int(inputs[10])
        area = int(inputs[11])
        lane = int(inputs[12])
        score = 0
        card = Card(i, card_number, instance_id,location, card_type, cost, attack, defense, abilities, my_health_change, opponent_health_change, card_draw, area, lane, score)
        cards.append(card)
        cardsOld.append([i, card_number, instance_id,location, card_type, cost, attack, defense, abilities, my_health_change, opponent_health_change, card_draw, area, lane, score])
    
    for cardA in cards:
        if cardA.instance_id == -1:
            continue
    
    if player_mana == 0:
        createScore()
        #choose_cards()
        #chooseCardsBasedOnScore()
        chooseCardsBasedOnScoreCap4Mana()

        
    else:
        actions = []
        targetids = []
        hand = []
        lane0 = []
        lane1 = []
        lane0opp = []
        lane1opp = []
        board = []
        sameLaneMonster = []
        bothLaneMonster = []
        sameLaneSpell = []
        bothLaneSpell = []
        for cardA in cards:
            if(cardA.card_type == int(CardType.MONSTER)) & (cardA.area == int(Area.ONELANE)) & (cardA.location == int(Location.BOARD)):
                sameLaneMonster.append(cardA)
            if(cardA.card_type == int(CardType.MONSTER)) & (cardA.area == int(Area.BOTHLANE)) & (cardA.location == int(Location.BOARD)):
                bothLaneMonster.append(cardA)    
            if(cardA.card_type == int(CardType.RED)) & (cardA.area == int(Area.ONELANE)):
                sameLaneSpell.append(cardA)
            if(cardA.card_type == int(CardType.RED)) & (cardA.area == int(Area.BOTHLANE)):
                bothLaneSpell.append(cardA)
            if(cardA.card_type == int(CardType.BLUE)) & (cardA.area == int(Area.ONELANE)):
                sameLaneSpell.append(cardA)
            if(cardA.card_type == int(CardType.BLUE)) & (cardA.area == int(Area.BOTHLANE)):
                bothLaneSpell.append(cardA)        
            if (cardA.card_type == int(CardType.MONSTER)) & (cardA.lane == int(Lane.LEFT)) & (cardA.location == int(Location.BOARD)):
                lane0.append(cardA)
                board.append(cardA)
            if (cardA.card_type == int(CardType.MONSTER)) & (cardA.lane == int(Lane.RIGHT)) & (cardA.location == int(Location.BOARD)):
                lane1.append(cardA)
                board.append(cardA)
            if (cardA.card_type == int(CardType.MONSTER)) & (cardA.lane == int(Lane.LEFT)) & (cardA.location == int(Location.OPPONENT_BOARD)):
                lane0opp.append(cardA)
            if (cardA.card_type == int(CardType.MONSTER)) & (cardA.lane == int(Lane.RIGHT)) & (cardA.location == int(Location.OPPONENT_BOARD)):
                lane1opp.append(cardA)
            else:
                if(cardA.location == int(Location.PLAYER_HAND)):
                    hand.append(cardA)  
        print("length: " , len(lane0),  file=sys.stderr, flush=True)
        
        #for cardA in hand:
        #    if(cardA[4] == 3):
        #        actions.append("USE " + str(cardA[2]) + " -1 ")
        print("lngth", len(sameLaneSpell),  file=sys.stderr, flush=True)
        bothLaneSpell = sorted(bothLaneSpell, key=lambda card: card.cost)
        sameLaneSpell = sorted(sameLaneSpell, key=lambda card: card.cost)
        damage_min = 0
        highest_defense_card = None
        for card in cards:
            if(card.location == int(Location.OPPONENT_BOARD)) & (card.defense > damage_min):
                damage_min = card.defense
                highest_defense_card = card
                print("defense: " , card.defense,  file=sys.stderr, flush=True)
        if(highest_defense_card != None):        
            player_mana = DestroyCardsV2(player_mana, damage_min, highest_defense_card)                                  
        
        
        if(len(lane0) == 2) & (len(lane1) == 2):
            for cardA in bothLaneMonster:
                actions.append(Summon(cardA.instance_id, 1) )
        elif(len(lane0) == 3) & (len(lane1) == 0):  
            for cardA in sameLaneMonster:
                actions.append(Summon(cardA.instance_id, 1))
        elif(len(lane0) == 0) & (len(lane1) == 3):  
            for cardA in sameLaneMonster:
                actions.append(Summon(cardA.instance_id, 0))
        elif(len(lane0) == 3) & (len(lane1) == 1):  
            for cardA in sameLaneMonster:
                actions.append(Summon(cardA.instance_id, 1))
        elif(len(lane0) == 1) & (len(lane1) == 3):  
            for cardA in sameLaneMonster:
                actions.append(Summon(cardA.instance_id, 0))                
        for cardA in hand:
            if (cardA.card_type == int(CardType.MONSTER)) :
                if (len(lane0) >= len(lane1)) :
                    actions.append(Summon(cardA.instance_id, 1))
                else:
                    actions.append(Summon(cardA.instance_id, 0))

        
        for cardA in hand:
            if(cardA.card_type == int(CardType.GREEN)) :
                for cardB in cards:
                    actions.append(Use(cardA.instance_id, cardB.instance_id))
        for cardA in board:
            for cardB in cards:
                if(('G' in cardB.abilities) & (cardB.location == int(Location.OPPONENT_BOARD))):
                    actions.append(Attack(cardA.instance_id, cardB.instance_id))  
            actions.append(Attack(cardA.instance_id, -1))        
        if(len(hand) == 8):
            for cardA in hand:
                if(cardA.card_type == int(CardType.BLUE) ) :
                    actions.append(Use(cardA.instance_id, -1))  
        print(';'.join(actions))
    #print("; SUMMON " + str(cards[0][2]) + " 0;")
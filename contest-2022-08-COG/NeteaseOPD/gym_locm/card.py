# !/usr/bin/env python
# coding: utf-8

'''
@file:      card.py
@Author:    liyunkun
@email:     liyunkun@corp.netease.com
@Time:      2022/4/13
'''

from enum import Enum

from gym_locm.exceptions import WardShieldError


class Area(Enum):
    TARGET = 0
    LANE1 = 1
    LANE2 = 2
    # TARGET = 'target'
    # LANE1 = 'lane1'
    # LANE2 = 'lane2'


class Card:
    def __init__(self, card_id, card_type, cost, attack, defense, keywords,
                 player_hp, enemy_hp, card_draw, area, instance_id=None):
        self.id = int(card_id)
        self.instance_id = instance_id
        # self.name = name
        self.type = int(card_type)
        self.cost = int(cost)
        self.attack = int(attack)
        self.defense = int(defense)
        self.keywords = set(list(keywords.replace("-", "")))
        self.player_hp = int(player_hp)
        self.enemy_hp = int(enemy_hp)
        self.card_draw = int(card_draw)
        if isinstance(area, str):
            if area == 'target':
                area = 0
            elif area == 'lane1':
                area = 1
            elif area == 'lane2':
                area = 2
            # else:
            #     raise ValueError("'{}' is not a valid Area".format(area))
        self.area = Area(int(area))
        # self.text = ''  # text deprecated as we are far from TESL in many cards
        # self.generate_text()

    # def generate_text(self):
    #     self.text = ''

    def has_ability(self, keyword: str) -> bool:
        return keyword in self.keywords

    def make_copy(self, instance_id=None) -> 'Card':
        cloned_card = Card.empty_copy(self)

        cloned_card.id = self.id
        # cloned_card.name = self.name
        cloned_card.type = self.type
        cloned_card.cost = self.cost
        cloned_card.attack = self.attack
        cloned_card.defense = self.defense
        cloned_card.keywords = set(self.keywords)
        cloned_card.player_hp = self.player_hp
        cloned_card.enemy_hp = self.enemy_hp
        cloned_card.card_draw = self.card_draw
        cloned_card.area = self.area
        # cloned_card.text = self.text

        if instance_id is not None:
            cloned_card.instance_id = instance_id
        else:
            cloned_card.instance_id = None

        return cloned_card

    def __eq__(self, other):
        return other is not None \
               and self.instance_id is not None \
               and other.instance_id is not None \
               and self.instance_id == other.instance_id

    def __repr__(self):
        # if self.name:
        #     return f"({self.instance_id}: {self.name})"
        return f"({self.instance_id})"

    @staticmethod
    def empty_copy(card):

        new_copy = EmptyCard()
        new_copy.__class__ = type(card)

        return new_copy

    @staticmethod
    def mockup_card():
        return Card(0, 0, 0, 0, 0, "------", 0, 0, 0, 'target', instance_id=None)


class EmptyCard(Card):
    def __init__(self):
        pass


class Creature(Card):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.is_dead = False
        self.can_attack = False
        self.has_attacked_this_turn = False

    def remove_ability(self, ability: str):
        self.keywords.discard(ability)

    def add_ability(self, ability: str):
        self.keywords.add(ability)

    def able_to_attack(self) -> bool:
        return not self.has_attacked_this_turn and \
               (self.can_attack or self.has_ability('C'))

    def damage(self, amount: int = 1, lethal: bool = False) -> int:
        if amount <= 0:
            return 0

        if self.has_ability('W'):
            self.remove_ability('W')

            raise WardShieldError()

        self.defense -= amount

        if lethal or self.defense <= 0:
            self.is_dead = True

        return amount

    def make_copy(self, instance_id=None) -> 'Card':
        cloned_card = super().make_copy(instance_id)

        cloned_card.is_dead = self.is_dead
        cloned_card.can_attack = self.can_attack
        cloned_card.has_attacked_this_turn = self.has_attacked_this_turn

        return cloned_card


class Item(Card):
    pass


class GreenItem(Item):
    pass


class RedItem(Item):
    pass


class BlueItem(Item):
    pass

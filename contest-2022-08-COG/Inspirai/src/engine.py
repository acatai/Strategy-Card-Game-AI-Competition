from src import const
from src.envs_utils import MINION, GREEN, RED, BLUE, BOARD, FOE, HAND, ENEMY_HAND, ENEMY_DECK, LEFT, RIGHT


def int_except(value):
    try:
        return int(value)
    except ValueError:
        return value


class Player:
    def __init__(self):
        self.player_id = None
        self.health = 30
        self.mana = 0
        self.deck = 0
        self.draw = 0
        self.cum_damage = 0

        self.hand = []
        self.lanes = ([], [])
        self.deck_card = []

    def damage(self, amount):
        # positive amount for HP lost, negative amount for HP increase
        self.health -= amount
        amount = max(0, amount)

        # get 1 bouns draw for every 5 HP lost
        self.cum_damage += amount
        bouns_drawn = self.cum_damage // 5
        self.draw += bouns_drawn
        self.cum_damage -= bouns_drawn * 5

        return amount


class Card:
    def __init__(self, card_id, instance_id, location, card_type, cost, attack, defense, keywords,
                 player_hp, enemy_hp, card_draw, area, lane):
        self.id = card_id
        self.instance_id = instance_id
        self.location = location
        self.card_type = card_type
        self.cost = cost
        self.attack = attack
        self.defense = defense
        self.reverse_keywords = keywords
        self.keywords = set(list(keywords.replace("-", "")))
        self.player_hp = player_hp
        self.enemy_hp = enemy_hp
        self.card_draw = card_draw
        self.area = area
        self.lane = lane

    def make_copy(self, instance_id):
        cloned_card = Card.empty_copy(self)

        cloned_card.id = self.id
        cloned_card.instance_id = instance_id
        cloned_card.card_type = self.card_type
        cloned_card.cost = self.cost
        cloned_card.location = self.location
        cloned_card.attack = self.attack
        cloned_card.defense = self.defense
        cloned_card.reverse_keywords = self.reverse_keywords
        cloned_card.keywords = set(self.keywords)
        cloned_card.player_hp = self.player_hp
        cloned_card.enemy_hp = self.enemy_hp
        cloned_card.card_draw = self.card_draw
        cloned_card.area = self.area
        cloned_card.lane = self.lane

        return cloned_card

    def has_ability(self, keyword):
        return keyword in self.keywords

    @staticmethod
    def empty_copy(card):
        class Empty(Card):
            def __init__(self):
                pass

        new_copy = Empty()
        new_copy.__class__ = type(card)

        return new_copy


class Creature(Card):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_dead = False
        self.can_attack = False
        self.has_attacked_this_turn = False

    def remove_ability(self, ability):
        self.keywords.discard(ability)

    def add_ability(self, ability):
        self.keywords.add(ability)

    def able_to_attack(self):
        return not self.has_attacked_this_turn and \
            (self.can_attack or self.has_ability('C'))

    def damage(self, amount, lethal: bool = False):
        # positive amount for HP lost
        if amount <= 0:
            return 0

        if self.has_ability('W'):
            self.remove_ability('W')
            return 0

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


class GreenCard(Card):
    pass


class RedCard(Card):
    pass


class BlueCard(Card):
    pass


class State:
    def __init__(self):
        self.max_instance_id = 60
        self.players = (Player(), Player())
        self.opponent_hand = None
        self.opponent_action_num = None
        self.opponent_actions = None

    @property
    def current_player(self) -> Player:
        return self.players[0]

    @property
    def opposing_player(self) -> Player:
        return self.players[1]

    def step(self, card_id: int, target_id: int):
        """
        Args:
            card_id (int): card instance_id
            target_id (int): target instance_id
        Returns:
            action: SUMMON id1 id2
            obs: gamecore obs
        """
        action = self.get_action(card_id, target_id)
        obs = self.act(action)
        return obs, action

    def get_action(self, card_id: int, target_id: int):
        """
        Args:
            card_id (Int): Origin card instance id
            target_id (Int): Target card instance id or opposing player
        """
        origin = self.find_cards(card_id)
        location = origin.location
        card_type = origin.card_type
        cmd = {
            (HAND, MINION): 'SUMMON',
            (BOARD, MINION): 'ATTACK',
            (HAND, GREEN): 'USE',
            (HAND, RED): 'USE',
            (HAND, BLUE): 'USE',
            }.get((location, card_type))

        action = f'{cmd} {card_id} {target_id}'
        return action

    def act(self, action):
        cmd, origin_id, target = map(int_except, action.split())
        origin = self.find_cards(origin_id)

        if cmd == 'SUMMON':
            self.do_summon(origin, target)
        elif cmd == 'ATTACK':
            target = self.find_cards(target) if target != -1 else target
            self.do_attack(origin, target)
        elif cmd == 'USE':
            target = self.find_cards(target) if target != -1 else target
            self.do_use(origin, target)

        for player in self.players:
            for lane in player.lanes:
                dead_creatures = [c for c in lane if c.is_dead]
                for creature in dead_creatures:
                    lane.remove(creature)

        obs = self.encoding_obs()
        return obs

    def find_cards(self, card_id):
        c, o = self.current_player, self.opposing_player

        card_location = {
            HAND: c.hand,
            BOARD: c.lanes[0] + c.lanes[1],
            FOE: o.lanes[0] + o.lanes[1]
        }

        for location, cards in card_location.items():
            for card in cards:
                if card.instance_id == card_id:
                    return card

    def do_summon(self, origin: Creature, target: int):
        """
        Args:
            origin (Creature): origin card
            target (Int): target lane id
        """
        self.current_player.hand.remove(origin)
        self._apply_summon_effect(origin, target)

        # area effect
        if origin.area == 1:
            if len(self.current_player.lanes[target]) < 3:
                self.max_instance_id += 1
                origin_clone = origin.make_copy(self.max_instance_id)
                self._apply_summon_effect(origin_clone, target)
        elif origin.area == 2:
            other_lane = RIGHT if target == LEFT else LEFT
            if len(self.current_player.lanes[other_lane]) < 3:
                self.max_instance_id += 1
                origin_clone = origin.make_copy(self.max_instance_id)
                self._apply_summon_effect(origin_clone, other_lane)

        # mana cost
        self.current_player.mana -= origin.cost

    def _apply_summon_effect(self, origin: Creature, target: int):
        c, o = self.current_player, self.opposing_player
        origin.location = BOARD
        origin.lane = target
        c.lanes[target].append(origin)
        c.draw += origin.card_draw
        c.damage(-origin.player_hp)
        o.damage(-origin.enemy_hp)

    def do_attack(self, origin: Creature, target):
        """
        Args:
            origin (Creature): origin card
            target (Creature/int): attack target or player
        """
        c, o = self.current_player, self.opposing_player
        # attack opposing player
        if isinstance(target, int):
            damage_dealt = o.damage(origin.attack)

        # attack creature
        elif isinstance(target, Creature):
            # origin cause damage
            damage_dealt = target.damage(origin.attack, lethal=origin.has_ability('L'))

            # origin received damage
            damage_received = origin.damage(target.attack, lethal=target.has_ability('L'))

            excess_damage = damage_dealt - damage_received
            if origin.has_ability('B') and excess_damage > 0:
                o.damage(excess_damage)

        if origin.has_ability('D'):
            c.health += damage_dealt

        origin.has_attacked_this_turn = True

    def do_use(self, origin: Card, target):
        """
        Args:
            origin (Card): origin card
            target (Card/int): target Creature or player
        """
        c, o = self.current_player, self.opposing_player

        c.hand.remove(origin)

        targets = None
        if origin.area == 0 or isinstance(target, int):
            # affect a single creature or the opposing player
            targets = [target]

        elif origin.area == 1 or origin.area == 2:
            # area affect
            target_lane, target_player = None, None
            for player in [c, o]:
                for lane in [LEFT, RIGHT]:
                    for creature in player.lanes[lane]:
                        if creature.instance_id == target.instance_id:
                            target_lane = lane
                            target_player = player
                            break
            if origin.area == 1:
                # affect all creatures on the same lane
                targets = target_player.lanes[target_lane]
            elif origin.area == 2:
                # affect all creatures on the all lane
                targets = target_player.lanes[LEFT] + target_player.lanes[RIGHT]

        for t in targets:
            self._apply_use_effect(origin, t)

        c.mana -= origin.cost
        return

    def _apply_use_effect(self, origin: Card, target: Creature):
        c, o = self.current_player, self.opposing_player

        if isinstance(origin, GreenCard):
            target.attack = max(0, target.attack + origin.attack)
            target.defense += origin.defense
            target.keywords = target.keywords.union(origin.keywords)

            if target.defense <= 0:
                target.is_dead = True

        elif isinstance(origin, RedCard) or isinstance(origin, BlueCard):
            if isinstance(target, Creature):
                target.attack = max(0, target.attack + origin.attack)
                target.keywords = target.keywords.difference(origin.keywords)
                target.damage(-origin.defense)
                target.is_dead = True if target.defense <= 0 else False

            else:
                o.damage(-origin.defense)

        c.draw += origin.card_draw
        c.damage(-origin.player_hp)
        o.damage(-origin.enemy_hp)

    def update(self, obs):

        # update obs information
        self.players = (Player(), Player())

        p, o = self.current_player, self.opposing_player
        p.player_id = obs['player_id']
        p.health, p.mana, p.deck, _ = map(int, list(obs[const.players][0].values()))
        o.health, o.mana, o.deck, o.draw = map(int, list(obs[const.players][1].values()))

        # update opponent info
        self.opponent_hand = obs['opponent_hand']
        self.opponent_action_num = obs['opponent_actions']
        self.opponent_actions = obs['card_number_and_action']

        # update max instance id
        for opponent_action in obs['card_number_and_action']:
            _, _, instanceid, _ = map(int_except, opponent_action.split())
            self.max_instance_id = max(self.max_instance_id, instanceid)

        type_class_dict = {0: Creature, 1: GreenCard, 2: RedCard, 3: BlueCard}

        for card in obs[const.cards]:
            card_number, instance_id, location, card_type, cost, attack, defense,\
            abilities, player_hp, enemy_hp, card_draw, area, lane = map(int_except, list(card.values()))

            self.max_instance_id = max(self.max_instance_id, instance_id)
            type_class = type_class_dict[card_type]

            card = type_class(card_number, instance_id, location, card_type, cost, attack, defense,
                        abilities, player_hp, enemy_hp, card_draw, area, lane)

            if location == HAND:
                p.hand.append(card)
            elif location == BOARD:
                card.can_attack = True
                p.lanes[lane].append(card)
            elif location == FOE:
                o.lanes[lane].append(card)
            elif location == ENEMY_HAND:
                o.hand.append(card)
            elif location == ENEMY_DECK:
                o.deck_card.append(card)

    def get_action_mask(self):
        """
            returns: {'card instance id': [[available target], [lanes]]}
        """
        action_mask = {}
        players, opposing = self.current_player, self.opposing_player
        players_board = players.lanes[LEFT] + players.lanes[RIGHT]

        for card in players.hand:
            available_target, lanes = [], []

            if card.cost > players.mana:
                continue

            if isinstance(card, Creature):
                for index, lane in enumerate(players.lanes):
                    if len(lane) < 3:
                        lanes.append(index)

            elif isinstance(card, RedCard):
                for index, lane in enumerate(opposing.lanes):
                    for enemy_card in lane:
                        available_target.append(enemy_card.instance_id)

            elif isinstance(card, GreenCard):
                for index, lane in enumerate(players.lanes):
                    for my_card in lane:
                        available_target.append(my_card.instance_id)

            elif isinstance(card, BlueCard):
                if card.defense < 0:
                    for index, lane in enumerate(opposing.lanes):
                        for enemy_card in lane:
                            available_target.append(enemy_card.instance_id)
                available_target.append(-1)

            action_mask.update({card.instance_id: (available_target, lanes)})

        for card in players_board:
            available_target, lanes = [], []
            if not card.able_to_attack():
                continue

            guard_creature = []
            for enemy_card in opposing.lanes[card.lane]:
                if enemy_card.has_ability('G'):
                    guard_creature.append(enemy_card.instance_id)

            available_target = [card.instance_id for card in opposing.lanes[card.lane]] if not guard_creature else guard_creature

            if not guard_creature:
                available_target.append(-1)

            action_mask.update({card.instance_id: (available_target, lanes)})

        action_mask = {k: v for k, v in action_mask.items() if len(v[0] + v[1])}

        return action_mask

    def post_process(self, action_mask):
        actions = []
        players_board = self.current_player.lanes[LEFT] + self.current_player.lanes[RIGHT]

        for card in players_board:
            if card.able_to_attack():
                (available_target, lanes) = action_mask.get(card.instance_id, ([], []))
                if -1 in available_target:
                    actions.append(f'ATTACK {card.instance_id} -1')

        for action in actions:
            self.act(action)

        obs = self.encoding_obs()
        return obs, actions

    def encoding_obs(self):
        obs = {}
        c, o = self.current_player, self.opposing_player
        # construct player_id
        obs.setdefault('player_id', c.player_id)

        # construct player info
        players_info = []
        for player in self.players:
            player_info = {'player_health': player.health, 'player_mana': player.mana, 'player_deck': player.deck, 'player_draw': player.draw}
            players_info.append(player_info)

        obs.setdefault('players', players_info)

        # construct opponent info
        obs.setdefault('opponent_hand', self.opponent_hand)
        obs.setdefault('opponent_actions', self.opponent_action_num)
        obs.setdefault('card_number_and_action', self.opponent_actions)

        # construct card info
        cards = c.hand + c.lanes[0] + c.lanes[1] + o.lanes[0] + o.lanes[1] + o.hand + o.deck_card
        cards_info = []
        for card in cards:
            card = {'card_number': card.id, 'instance_id': card.instance_id, 'location': card.location,
                    'card_type': card.card_type, 'cost': card.cost, 'attack': card.attack, 'defense': card.defense,
                    'abilities': card.reverse_keywords, 'my_health_change': card.player_hp, 'opponent_health_change': card.enemy_hp,
                    'card_draw': card.card_draw, 'area': card.area, 'lane': card.lane}
            cards_info.append(card)

        obs.setdefault('cards', cards_info)

        return obs
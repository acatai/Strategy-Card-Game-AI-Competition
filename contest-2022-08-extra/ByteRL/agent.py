from abc import ABC, abstractmethod
from collections import OrderedDict
from copy import deepcopy
import os

import numpy as np
from engine import *
from model import fully_connected_layers,LSTM_layers,Conv1d,model_import,cb_discrete_action_head,discrete_action_head

class Agent(ABC):
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def seed(self, seed):
        pass

    @abstractmethod
    def reset(self, **kwargs):
        pass

    @abstractmethod
    def act(self, state):
        pass

card_types = {Creature: 0, GreenItem: 1, RedItem: 2, BlueItem: 3}


def encode_card(card):
    """Encodes a card object into a numerical array."""
    card_type = [1.0 if isinstance(card, card_type) else 0.0
                 for card_type in card_types]
    cost = card.cost / 12
    attack = card.attack / 12
    defense = max(-12, card.defense) / 12
    keywords = list(map(int, map(card.keywords.__contains__, 'BCDGLW')))
    player_hp = card.player_hp / 12
    enemy_hp = card.enemy_hp / 12
    card_draw = card.card_draw / 2

    return card_type + [cost, attack, defense, player_hp,
                        enemy_hp, card_draw] + keywords


def encode_friendly_card_on_board(card: Creature):
    """Encodes a card object into a numerical array."""
    attack = card.attack / 12
    defense = card.defense / 12
    can_attack = int(card.can_attack and not card.has_attacked_this_turn)
    keywords = list(map(int, map(card.keywords.__contains__, 'BCDGLW')))

    return [attack, defense, can_attack] + keywords


def encode_enemy_card_on_board(card: Creature):
    """Encodes a card object into a numerical array."""
    attack = card.attack / 12
    defense = card.defense / 12
    keywords = list(map(int, map(card.keywords.__contains__, 'BCDGLW')))

    return [attack, defense] + keywords

def encode_players(current: Player, opposing: Player):
    return current.health / 30, \
           current.mana / 13, \
           current.next_rune / 30, \
           (1 + current.bonus_draw) / 6, \
           opposing.health / 30, \
           (opposing.base_mana + opposing.bonus_mana) / 13, \
           opposing.next_rune / 30, \
           (1 + opposing.bonus_draw) / 6

class CardRecorder:
    def __init__(self) -> None:
        self.my_deck = []
        self.last_hands_instanceid = []

    def recorder_draft(self, cards, my_choose):
        self.my_deck.append(cards[my_choose])

    def recorder_battle(self, state):
        for card in state.players[0].hand:
            if card.instance_id not in self.last_hands_instanceid:
                for idx, card in enumerate(self.my_deck):
                    if card.id == card.id:
                        self.my_deck.pop(idx)
                        break
        self.last_hands_instanceid = [card.instance_id for card in state.current_player.hand]

    def full_missing_cards(self, state):
        instance_id = max(card.instance_id for card in state.current_player.hand) + 1
        d1 = []
        assert len(self.my_deck) == len(state.current_player.deck)
        for card in self.my_deck:
            d1.append(card.make_copy(instance_id))
            instance_id += 1
        state.current_player.deck = d1
        return state

class SubmitInterface:

    def __init__(self):
        self.drafts = []
        self.cb_actions = []
        self.card_recorder=CardRecorder()
        self.cards_num = 90
        self.selected_num = 30
        self.cb_card_features = 16
        self.cb_action_size = 4

        # battle phase observation and action size
        self.player_features = 4  # hp, mana, next_rune, next_draw
        self.cards_in_hand = 8
        self.bt_card_features = 16
        self.friendly_cards_on_board = 6
        self.enemy_cards_on_board = 6
        self.friendly_board_card_features = 9
        self.enemy_board_card_features = 8
        self.bt_action_size = 145

    def env_to_agt_trans_observation(self, observation):
        """
        Args:
            observation: an LOCM `State` instance

        Returns:
            Transformed observations for each agent
        """

        state = observation  # shorthand

        self.cb_phase_mask = True if state.phase == Phase.DRAFT else False

        if self.cb_phase_mask ==False:
            self.card_recorder.recorder_battle(state)

        p0, p1 = state.current_player, state.opposing_player

        def fill_cards(card_list, up_to, features):
            remaining_cards = up_to - len(card_list)

            return card_list + [[0] * features for _ in range(remaining_cards)]

        players_encoder = encode_players(p0, p1)
        player = np.array(players_encoder[:4], dtype=np.float32)
        oppo_player = np.array(players_encoder[4:], dtype=np.float32)

        deck_cards = np.array(
            fill_cards(list(map(encode_card, self.card_recorder.my_deck)), up_to=self.selected_num, features=self.bt_card_features),
            dtype=np.float32)

        turn = len(self.cb_actions) + 1
        if self.cb_phase_mask:

            self.drafts.extend(state.current_player.hand)
            drafts_encode = list(map(encode_card, self.drafts))
            card_set_encode = fill_cards(drafts_encode, self.cards_num, self.cb_card_features)
            card_set_encode = np.array(card_set_encode, dtype=np.float32)

            cards_selected_mask = np.zeros([self.cards_num, ], dtype=np.float32)
            for i, cb_act in enumerate(self.cb_actions):
                cards_selected_mask[i * 3 + cb_act] = 1.
            cards_can_select_mask = np.full(self.cards_num, 0., dtype=np.float32)
            cards_can_select_mask[int((turn - 1) * 3):int(turn * 3)] = 1.

            cb_action_mask = np.concatenate([np.array([0.]), np.array(deepcopy(state.action_mask))]).astype(np.float32)
            cur_player_obs = OrderedDict([('cb_phase_mask', np.array([self.cb_phase_mask], dtype=np.float32)),
                                          ('card_set', card_set_encode),
                                          ('cards_selected_mask', cards_selected_mask),
                                          ('cards_can_select_mask', cards_can_select_mask),
                                          ('hand_cards',
                                           np.zeros((self.cards_in_hand, self.cb_card_features), dtype=np.float32)),
                                          ('deck_cards', deck_cards),
                                          ('me_lane0_cards',
                                           np.zeros((3, self.friendly_board_card_features,), dtype=np.float32)),
                                          ('me_lane1_cards',
                                           np.zeros((3, self.friendly_board_card_features,), dtype=np.float32)),
                                          ('oppo_lane0_cards',
                                           np.zeros((3, self.enemy_board_card_features,),
                                                    dtype=np.float32)),
                                          ('oppo_lane1_cards',
                                           np.zeros((3, self.enemy_board_card_features,),
                                                    dtype=np.float32)),
                                          ('player', player),
                                          ('oppo_player', oppo_player),
                                          ('cb_action_mask', cb_action_mask),  # TODO
                                          ('bt_action_mask',
                                           np.zeros((self.bt_action_size,), dtype=np.float32)),
                                          ])



        else:
            bt_action_mask = np.array(deepcopy(state.action_mask), dtype=np.float32)
            all_cards = []
            drafts_encode = list(map(encode_card, self.drafts))

            hand_cards = np.array(
                fill_cards(list(map(encode_card, p0.hand)), up_to=self.cards_in_hand, features=self.bt_card_features),
                dtype=np.float32)
            me_lane0_cards = np.array(fill_cards(list(map(encode_friendly_card_on_board, p0.lanes[0])), up_to=3,
                                                 features=self.friendly_board_card_features), dtype=np.float32)
            me_lane1_cards = np.array(fill_cards(list(map(encode_friendly_card_on_board, p0.lanes[1])), up_to=3,
                                                 features=self.friendly_board_card_features), dtype=np.float32)
            oppo_lane0_cards = np.array(fill_cards(list(map(encode_enemy_card_on_board, p1.lanes[0])), up_to=3,
                                                   features=self.enemy_board_card_features), dtype=np.float32)
            oppo_lane1_cards = np.array(fill_cards(list(map(encode_enemy_card_on_board, p1.lanes[1])), up_to=3,
                                                   features=self.enemy_board_card_features), dtype=np.float32)

            cards_selected_mask = np.zeros([self.cards_num, ], dtype=np.float32)
            for i, cb_act in enumerate(self.cb_actions):
                cards_selected_mask[i * 3 + cb_act] = 1.

            cur_player_obs = OrderedDict([('cb_phase_mask', np.array([self.cb_phase_mask], dtype=np.float32)),
                                          ('card_set', np.array(drafts_encode, dtype=np.float32)),
                                          ('cards_selected_mask', cards_selected_mask),
                                          ('cards_can_select_mask', np.full(self.cards_num, 0., dtype=np.float32)),
                                          ('hand_cards', hand_cards),
                                          ('deck_cards', deck_cards),
                                          ('me_lane0_cards', me_lane0_cards),
                                          ('me_lane1_cards', me_lane1_cards),
                                          ('oppo_lane0_cards', oppo_lane0_cards),
                                          ('oppo_lane1_cards', oppo_lane1_cards),
                                          ('player', player),
                                          ('oppo_player', oppo_player),
                                          ('cb_action_mask', np.array([1., 0., 0., 0.], dtype=np.float32)),  # TODO
                                          ('bt_action_mask', np.array(bt_action_mask, dtype=np.float32)),
                                          ])
        return cur_player_obs
        
    def convert_to_locm_action(self, state, action_number):
        if state.phase == Phase.DRAFT:
            action_number -= 1
            self.card_recorder.recorder_draft(state.current_player.hand, action_number)
            return Action(ActionType.ATTACK, action_number)

        me_player = state.current_player
        oppo_player = state.opposing_player

        if not state.items and action_number > 16:
            action_number += 104

        if action_number == 0:
            return Action(ActionType.PASS)
        elif 1 <= action_number <= 16:
            action_number -= 1

            origin = int(action_number / 2)
            target = Lane(action_number % 2)

            origin = me_player.hand[origin].instance_id

            return Action(ActionType.SUMMON, origin, target)
        elif 17 <= action_number <= 120:
            action_number -= 17

            origin = int(action_number / 13)
            target = action_number % 13

            origin = me_player.hand[origin].instance_id

            if target == 0:
                target = None
            else:
                target -= 1

                side = [me_player, oppo_player][int(target / 6)]
                lane = int((target % 6) / 3)
                index = target % 3

                target = side.lanes[lane][index].instance_id

            return Action(ActionType.USE, origin, target)
        elif 121 <= action_number <= 144:
            action_number -= 121

            origin = action_number // 4
            target = action_number % 4

            lane = origin // 3

            origin = me_player.lanes[lane][origin % 3].instance_id

            if target == 0:
                target = None
            else:
                target -= 1

                target = oppo_player.lanes[lane][target].instance_id

            return Action(ActionType.ATTACK, origin, target)
        else:
            raise MalformedActionError(f'Invalid action_number {action_number}')

class ByterlAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        weights_name = ['self/shared_raw_card_embed/conv0/weights:0', 'self/shared_raw_card_embed/conv0/biases:0',
                        'self/shared_raw_card_embed/conv1/weights:0', 'self/shared_raw_card_embed/conv1/biases:0',
                        'self/cb_mebed/att0/weights:0', 'self/cb_mebed/att0/biases:0',
                        'self/shared_me_lane_card_embed/weights:0', 'self/shared_me_lane_card_embed/biases:0',
                        'self/shared_oppo_lane_card_embed/weights:0', 'self/shared_oppo_lane_card_embed/biases:0',
                        'self/shared_player_embed/weights:0', 'self/shared_player_embed/biases:0',
                        'self/bt_fc0/weights:0', 'self/bt_fc0/biases:0', 'self/bt_fc1/weights:0',
                        'self/bt_fc1/biases:0', 'self/bt_fc2/weights:0', 'self/bt_fc2/biases:0',
                        'self/lstm_embed/rnn/multi_rnn_cell/cell_0/lstm_cell_layer_0/kernel:0',
                        'self/lstm_embed/rnn/multi_rnn_cell/cell_0/lstm_cell_layer_0/bias:0',
                        'self/lstm_embed/rnn/multi_rnn_cell/cell_0/lstm_cell_layer_0/projection/kernel:0',
                        'self/cb_action_head/logits/weights:0', 'self/cb_action_head/logits/biases:0',
                        'self/bt_action_head/action/logits/weights:0', 'self/bt_action_head/action/logits/biases:0',
                        'self/vf/values/weights:0', 'self/vf/values/biases:0']

        weights=model_import(os.path.join(os.path.dirname(__file__),'Agent3.weights'),weights_name)

        self.shared_raw_card_embed_cv0 = Conv1d(weights['self/shared_raw_card_embed/conv0/weights:0'],
                                                weights['self/shared_raw_card_embed/conv0/biases:0'])
        self.shared_raw_card_embed_cv1 = Conv1d(weights['self/shared_raw_card_embed/conv1/weights:0'],
                                                weights['self/shared_raw_card_embed/conv1/biases:0'])
        self.cb_embed_cv_att0 = Conv1d(weights['self/cb_mebed/att0/weights:0'],
                                       weights['self/cb_mebed/att0/biases:0'])



        self.shared_me_lane_card_embed_cv = Conv1d(weights['self/shared_me_lane_card_embed/weights:0'],
                                                   weights['self/shared_me_lane_card_embed/biases:0'])
        self.shared_oppo_lane_card_embed_cv = Conv1d(weights['self/shared_oppo_lane_card_embed/weights:0'],
                                                     weights['self/shared_oppo_lane_card_embed/biases:0'])

        self.shared_player_embed_fc = fully_connected_layers(weights['self/shared_player_embed/weights:0'],
                                                             weights['self/shared_player_embed/biases:0'])

        self.bt_fc0 = fully_connected_layers(weights['self/bt_fc0/weights:0'],
                                             weights['self/bt_fc0/biases:0'])
        self.bt_fc1 = fully_connected_layers(weights['self/bt_fc1/weights:0'],
                                             weights['self/bt_fc1/biases:0'])
        self.bt_fc2 = fully_connected_layers(weights['self/bt_fc2/weights:0'],
                                             weights['self/bt_fc2/biases:0'])

        self.bt_lstm_embed = LSTM_layers(
            weights['self/lstm_embed/rnn/multi_rnn_cell/cell_0/lstm_cell_layer_0/kernel:0'],
            weights['self/lstm_embed/rnn/multi_rnn_cell/cell_0/lstm_cell_layer_0/bias:0'],
            weights['self/lstm_embed/rnn/multi_rnn_cell/cell_0/lstm_cell_layer_0/projection/kernel:0'])

        self.cb_action_head = cb_discrete_action_head(weights['self/cb_action_head/logits/weights:0'],
                                                      weights['self/cb_action_head/logits/biases:0'])

        self.bt_action_head = discrete_action_head(weights['self/bt_action_head/action/logits/weights:0'],
                                                   weights['self/bt_action_head/action/logits/biases:0'])
        self.cb_hs_new = None
        self.bt_hs_new = None
        self.intf = SubmitInterface()

    def _raw_card_feature_map(self, inputs):
        x = self.shared_raw_card_embed_cv0(inputs)
        outputs = self.shared_raw_card_embed_cv1(x)
        return outputs

    def seed(self, seed):
        pass

    def reset(self, **kwargs):
        pass

    def act(self, state):

        obs = self.intf.env_to_agt_trans_observation(state)

        card_set = np.expand_dims(obs['card_set'], axis=0)
        cards_fm = self._raw_card_feature_map(card_set)

        selected_mask = np.expand_dims(obs['cards_selected_mask'], axis=-1)
        selected_mask = np.tile(selected_mask, [1, 1, 32])

        sel_cards_fm = cards_fm * selected_mask
        sel_cards_emb = np.mean(sel_cards_fm, axis=1, keepdims=True)
        sel_cards_emb_to_return = np.squeeze(sel_cards_emb, axis=1)

        n_cards = obs['cards_selected_mask'].shape[0]
        sel_cards_emb = np.tile(sel_cards_emb, [1, n_cards, 1])
        x = np.concatenate([cards_fm, sel_cards_emb], axis=-1)
        x = self.cb_embed_cv_att0(x)

        can_sel_mask = np.expand_dims(obs['cards_can_select_mask'], axis=-1)
        can_sel_mask = np.tile(can_sel_mask, [1, 1, 64])
        cb_fm = x * can_sel_mask  # (bs, n_cards, 2*card_dim)
        selected_cards_embed = sel_cards_emb_to_return

        # (bs, 30, card_dim)
        deck_cards = np.expand_dims(obs['deck_cards'], axis=0)
        deck_cards_embed = self._raw_card_feature_map(deck_cards)
        deck_cards_embed = np.mean(deck_cards_embed, axis=1)  # (bs, card_dim)

        # (bs, 8, card_dim)
        hand_cards = np.expand_dims(obs['hand_cards'], axis=0)
        hand_cards_embed = self._raw_card_feature_map(hand_cards)
        hand_cards_embed = np.reshape(hand_cards_embed, newshape=(1, -1))  # (bs, 8*card_dim)

        # (bs, 3, dim)
        me_lane0_cards = np.expand_dims(obs['me_lane0_cards'], axis=0)
        me_lane0_cards_embed = self.shared_me_lane_card_embed_cv(me_lane0_cards)
        me_lane0_cards_embed = np.reshape(me_lane0_cards_embed, newshape=(1, -1))  # (bs, 3*dim)

        # (bs, 3, dim)
        me_lane1_cards = np.expand_dims(obs['me_lane1_cards'], axis=0)
        me_lane1_cards_embed = self.shared_me_lane_card_embed_cv(me_lane1_cards)
        me_lane1_cards_embed = np.reshape(me_lane1_cards_embed, newshape=(1, -1))  # (bs, 3*dim)

        # (bs, 3, dim)
        oppo_lane0_cards = np.expand_dims(obs['oppo_lane0_cards'], axis=0)
        oppo_lane0_cards_embed = self.shared_oppo_lane_card_embed_cv(oppo_lane0_cards)
        oppo_lane0_cards_embed = np.reshape(oppo_lane0_cards_embed, newshape=(1, -1))  # (bs, 3*dim)

        # (bs, 3, dim)
        oppo_lane1_cards = np.expand_dims(obs['oppo_lane1_cards'], axis=0)
        oppo_lane1_cards_embed = self.shared_oppo_lane_card_embed_cv(oppo_lane1_cards)
        oppo_lane1_cards_embed = np.reshape(oppo_lane1_cards_embed, newshape=(1, -1))  # (bs, 3*dim)

        # (bs, dim)
        player = np.expand_dims(obs['player'], axis=0)
        player_embed = self.shared_player_embed_fc(player)

        # (bs, dim)
        oppo_player = np.expand_dims(obs['oppo_player'], axis=0)
        oppo_player_embed = self.shared_player_embed_fc(oppo_player)

        #  # (bs, 10*card_dim+14*bt_base_dim)
        bt_embed = np.concatenate([
            deck_cards_embed,
            hand_cards_embed,
            me_lane0_cards_embed,
            me_lane1_cards_embed,
            oppo_lane0_cards_embed,
            oppo_lane1_cards_embed,
            player_embed,
            oppo_player_embed
        ], axis=-1)

        bt_embed = np.concatenate([bt_embed, selected_cards_embed], axis=-1)

        bt_embed = self.bt_fc0(bt_embed)
        bt_embed = self.bt_fc1(bt_embed)
        bt_embed = self.bt_fc2(bt_embed)

        bt_lstm_embed, self.bt_hs_new = self.bt_lstm_embed(bt_embed, self.bt_hs_new)

        if state.phase == Phase.DRAFT:
            cb_action_logit = self.cb_action_head(cb_fm, obs['cb_action_mask'], obs['cards_can_select_mask'])
            cb_action_num = np.argmax(cb_action_logit, -1)
            self.intf.cb_actions.append(cb_action_num - 1)

            return self.intf.convert_to_locm_action(state, cb_action_num)

        else:
            bt_action_logit = self.bt_action_head(bt_lstm_embed, obs['bt_action_mask'])
            bt_action_num = np.argmax(bt_action_logit, -1)
            return self.intf.convert_to_locm_action(state, bt_action_num)

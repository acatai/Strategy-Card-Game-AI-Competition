import time
from typing import Iterable, Set, Tuple, List, Optional, Union

import numpy as np

from serving_utils import (
    RLlibObsFlatSavedModelONNXUtils,
    OnnxOutputs,
)

from gym_locm.draft_env import LOCMDraftEnv
from gym_locm.battle_env import LOCMBattleEnv

from gym_locm.agents import Agent
from gym_locm.engine import (
    Phase,
    Action,
    PlayerOrder,
    ActionType,
    State,
    Player,
    EMPTY_DECK_DAMAGE,
    PLAYER_TURNLIMIT,
    Area,
    Card,
    Creature,
    Lane,
    GreenItem,
    RedItem,
    BlueItem,
    has_enough_mana,
)


class CustomRLONNXAgent(Agent):
    def __init__(
        self,
        model_path,
        phase: Union[Phase, int],
        action_dist_name: Optional[str] = None,
    ):
        env_cls = None
        if phase == Phase.DRAFT:
            env_cls = LOCMDraftEnv
        elif phase == Phase.BATTLE:
            env_cls = LOCMBattleEnv
        else:
            raise ValueError("Invalid phase: {}".format(phase))

        import onnxruntime

        self.phase = phase
        self.env_cls = env_cls
        self.env = env_cls(config={"skip_draft": True}, inferring=True)
        self.model_path = model_path

        sess_options = onnxruntime.SessionOptions()
        ## 减少线程竞争导致超时
        sess_options.intra_op_num_threads = 1
        sess_options.inter_op_num_threads = 1
        sess_options.log_severity_level = 3

        self.onnx_session = onnxruntime.InferenceSession(model_path, sess_options)

        if isinstance(action_dist_name, str):
            self.action_dist_name = action_dist_name
        else:
            session_outputs = [x.name for x in self.onnx_session.get_outputs()]
            self.action_dist_name = find_action_dist_name(session_outputs)

        session_inputs = [x.name for x in self.onnx_session.get_inputs()]
        policy_id = session_inputs[0].split("/")[0]
        self.smu = RLlibObsFlatSavedModelONNXUtils(
            observation_space=self.env.observation_space, policy_id=policy_id
        )

    def seed(self, seed):
        pass

    def reset(self):
        pass

    def act(self, state: State) -> Action:
        # 检查状态阶段是否对应模型
        if state.phase != self.phase:
            raise ValueError(
                "state's phase() != model's phase()".format(state.phase, self.phase)
            )

        self.env.state = state

        action_mask = self.env.state.action_mask
        state_encode = self.env.encode_state()  # to dict(numpy)

        observation = self.smu.state_preprocess(state_encode)  # to numpy
        inputs = self.smu.batch_to_tensor_inputs([observation])  # fill input terms

        outputs = self.onnx_session.run([self.action_dist_name], inputs)

        logits = np.array(outputs[0][0])
        action_mask = state_encode["action_mask"]
        masked_logits = logits - (1 - action_mask) * 1e6
        action_number = int(masked_logits.argmax())

        action_instance = self.env.decode_action(action_number)

        return action_instance


def find_action_dist_name(session_outputs):
    """
    session_outputs: like
    [
        'draft_main/add_1:0',
        'draft_main/cond_2/Merge:0',
        'draft_main/Reshape_2:0',
        'draft_main/Exp:0',
        'draft_main/cond_1/Merge:0'
    ]
    """
    for name in session_outputs:
        _name = "/".join(name.split("/")[1:])
        if "add" in _name:
            return name
    raise ValueError("action dist output name not found")


class CustomRLDraftONNXAgent(CustomRLONNXAgent):
    def __init__(self, model_path, action_dist_name: Optional[str] = None):
        super().__init__(model_path, phase=Phase.DRAFT, action_dist_name=action_dist_name)


class CustomRLBattleONNXAgent(CustomRLONNXAgent):
    def __init__(self, model_path, action_dist_name: Optional[str] = None):
        super().__init__(model_path, phase=Phase.BATTLE, action_dist_name=action_dist_name)


class ModelImprovementRules:
    def __init__(self) -> None:
        pass

    def otk(
        self, state: State, time_limit: Optional[float] = None
    ) -> Tuple[bool, Optional[List[Action]], bool, float, int, int]:
        """
        return
        是否可以在本回合击杀对方
        击杀行动列表
        搜索是否超时
        搜索耗时
        搜索过的状态（相同状态不重复计入）
        搜索过的状态（相同状态重复计入）
        """
        return False, None, False, 0.0, 0, 0

    def naive_otk(self, state: State) -> Tuple[bool, List[Action]]:
        return False, []

    def before_model(self, state: State) -> List[Action]:
        """
        Do actions before model inferrence.
        """
        return []

    def replace_action(self, state: State) -> List[Action]:
        """
        Replace model's action.
        """
        return []

    def before_pass(self, state: State) -> List[Action]:
        """
        Do actions before model pass.
        """
        return []


class BattleModelImprovementRules(ModelImprovementRules):
    def otk(
        self, state: State, time_limit: Optional[float] = None
    ) -> Tuple[bool, Optional[List[Action]], bool, float, int, int]:

        start_time = time.perf_counter()

        can_otk, otk_actions = self.naive_otk(state)
        if can_otk:
            return (
                True,
                otk_actions,
                False,
                time.perf_counter() - start_time,
                1,
                1,
            )

        init_state = state.otk_clone()
        seen: Set[tuple] = {state_encoding_for_otk(init_state)}  # 记录已经搜索过的状态
        states_stack: List[Tuple[State, List[Action]]] = [(init_state, [])]
        num_search = 1

        # --------------------------------------------------------------------
        # cut: 一开始先确定蓝牌对敌使用 (不包含不对对手使用蓝牌的可能)
        blue_actions = self._available_no_target_blue_actions(init_state)
        for actions in blue_actions:
            new_state = init_state.otk_clone()

            for action in actions:
                new_state.act(action)
                if new_state.winner is not None:
                    return (
                        True,
                        actions,
                        False,
                        time.perf_counter() - start_time,
                        len(seen) + 1,
                        num_search + 1,
                    )

            if time_limit and time.perf_counter() - start_time >= time_limit:
                return False, None, True, time.perf_counter() - start_time, len(seen), num_search

            num_search += 1
            state_encoding = state_encoding_for_otk(new_state)
            if state_encoding in seen:
                continue
            seen.add(state_encoding)

            can_otk, otk_actions = self.naive_otk(new_state)
            if can_otk:
                return (
                    True,
                    actions + otk_actions,
                    False,
                    time.perf_counter() - start_time,
                    len(seen),
                    num_search,
                )

            # 后续继续搜索
            states_stack.append((new_state, actions))

        # --------------------------------------------------------------------
        while states_stack:
            cur_state, prev_actions = states_stack.pop()

            # 执行可能达成otk的行动。保证状态已执行 state_encoding_for_otk 编码卡牌
            available_otk_actions = self._available_otk_actions(cur_state)
            for i, action in enumerate(available_otk_actions):

                if i == len(available_otk_actions) - 1:  # 最后一个可以不复制
                    new_state = cur_state
                else:
                    new_state = cur_state.otk_clone()  # 只复制需要的

                new_state.act(action)

                if new_state.winner is not None:
                    return (
                        True,
                        prev_actions + [action],
                        False,
                        time.perf_counter() - start_time,
                        len(seen) + 1,
                        num_search + 1,
                    )

                if time_limit and time.perf_counter() - start_time >= time_limit:
                    return False, None, True, time.perf_counter() - start_time, len(seen), num_search

                num_search += 1
                state_encoding = state_encoding_for_otk(new_state)
                if state_encoding in seen:
                    continue
                seen.add(state_encoding)

                can_otk, otk_actions = self.naive_otk(new_state)
                if can_otk:
                    return (
                        True,
                        prev_actions + [action] + otk_actions,
                        False,
                        time.perf_counter() - start_time,
                        len(seen),
                        num_search,
                    )

                # 后续继续搜索
                states_stack.append((new_state, prev_actions + [action]))

        return False, None, False, time.perf_counter() - start_time, len(seen), num_search

    def naive_otk(self, state: State) -> Tuple[bool, List[Action]]:

        attack_opp_actions, attack_opp_damage = state.available_attack_opp
        can_otk = self._will_attack_opp_win(state, attack_opp_damage)

        return can_otk, attack_opp_actions

    def before_pass(self, state: State) -> List[Action]:

        return self._attack_opp_actions(state)

    def _attack_opp_actions(self, state: State) -> List[Action]:

        if state._State__available_actions is not None:
            return [
                action
                for action in state.available_actions
                if action.type == ActionType.ATTACK and action.target is None
            ]
        else:
            return state.available_attack_opp[0]

    def _will_attack_opp_win(
        self, state: State, attack_opp_damage: int
    ) -> bool:
        """
        是否足以直接攻击击杀对方
        """
        cur_player_turn = state.turn
        opp_player_turn_next = (
            cur_player_turn
            if state._current_player == PlayerOrder.FIRST
            else cur_player_turn + 1
        )
        return self._will_dead(
            state.opposing_player, attack_opp_damage, opp_player_turn_next
        )

    def _will_dead(self, player: Player, damage: int, turn: int) -> bool:
        """
        计算玩家在下回合开始是否会死亡
        damage: 玩家在本回合预计还要承受的伤害
        turn: 玩家下回合的回合数
        """
        if damage >= player.health:
            return True

        # empty deck damage
        if len(player.hand) < 8:
            hand_space = 8 - len(player.hand)
            deck_remain = len(player.deck)

            if hand_space > deck_remain:
                next_draw = 1 + player.bonus_draw + (player.health_lost_this_turn + damage) // 5
                if next_draw > deck_remain:
                    damage += (next_draw - deck_remain) * EMPTY_DECK_DAMAGE

        # over turn limit damge
        if turn > PLAYER_TURNLIMIT:
            damage += EMPTY_DECK_DAMAGE

        if damage >= player.health:
            return True

        return False

    def _available_no_target_blue_actions(self, state: State) -> List[List[Action]]:
        """
        直接对对方使用蓝牌的所有可能行动组合
        """
        # 行动组合, 需要的mana数, 卡牌组合编码
        subsets: List[Tuple[List[Action], int, Tuple]] = [([], 0, tuple())]
        seen = set()  # 已有行动组合

        all_blues = [
            card
            for card in state.current_player.hand
            if isinstance(card, BlueItem) and card.cost <= state.current_player.mana
        ]
        all_blues.sort(key=lambda card: card.encoding)
        # 计算所有可能组合
        for card in all_blues:
            extend_list = []
            for item in subsets:
                encoding = item[2] + (card.encoding, )
                if encoding not in seen and item[1] + card.cost <= state.current_player.mana:
                    seen.add(encoding)
                    extend_list.append(
                        (
                            item[0] + [Action(ActionType.USE, card.instance_id, None)],
                            item[1] + card.cost,
                            encoding
                        )
                    )
            subsets.extend(extend_list)

        return [item[0] for item in subsets[1:]]  # 排除不使用蓝牌的可能

    def _available_otk_actions(self, state: State) -> List[Action]:
        """
        对otk有贡献的行动（合法行动的剪枝）：

        通用
        * 同区域属性相同卡牌去重

        攻击
        * 跳过直接攻击对方（每到一个状态已计算过场攻）
        * 允许占了格子的生物攻击对面非嘲讽，必须能送掉用于召唤生物（存在先送掉，再召唤带C或带enemy_hp生物的可能）

        法术
        * AOE法术行动目标去重
        * 不扣对面血的法术没必要搞对面非嘲讽生物

        召唤
        * 召唤LANE2属性生物目标半场去重
        * 召唤需符合以下之一：带enemy_hp、带C、能被绿牌加C、能作为带enemy_hp绿牌的目标

        """
        summon, attack, use = [], [], []
        seen = set()

        c_hand = state.current_player.hand
        c_lanes = state.current_player.lanes
        o_lanes = state.opposing_player.lanes

        # --------------------------------------------------------------------
        o_guards = ([], [])  # 对方嘲讽随从
        c_able_to_attack = ([], [])  # 我方能攻击的随从
        for lane in Lane:
            for enemy_creature in o_lanes[lane]:
                if enemy_creature.has_ability("G"):
                    o_guards[lane].append(enemy_creature)
            for friendly_creature in filter(Creature.able_to_attack, c_lanes[lane]):
                c_able_to_attack[lane].append(friendly_creature)

        o_has_guards = True if o_guards[0] + o_guards[1] else False
        c_has_able_to_attack = True if c_able_to_attack[0] + c_able_to_attack[1] else False

        # --------------------------------------------------------------------
        # 我方是否有带C绿牌，以及如果有，需要的最低费用
        has_green_with_c, green_with_c_least_cost = False, 99
        # 我方是否有带enemy_hp的绿牌，以及如果有，需要的最低费用
        has_green_with_enemy_hp, green_with_enemy_hp_least_cost = False, 99
        for card in filter(has_enough_mana(state.current_player.mana), c_hand):
            if isinstance(card, GreenItem):
                if card.has_ability("C"):
                    has_green_with_c = True
                    green_with_c_least_cost = min(green_with_c_least_cost, card.cost)
                if card.enemy_hp < 0:
                    has_green_with_enemy_hp = True
                    green_with_enemy_hp_least_cost = min(green_with_enemy_hp_least_cost, card.cost)

        has_creature_to_summon = False  # 是否有满足召唤剪枝条件的生物，不考虑是否够格子
        has_lane1_creature_to_summon = False
        has_lane2_creature_to_summon = False

        # --------------------------------------------------------------------

        for card in filter(has_enough_mana(state.current_player.mana), c_hand):
            origin = card.instance_id

            if card.encoding in seen:
                continue
            seen.add(card.encoding)

            if isinstance(card, Creature):
                # cut: 召唤需符合以下之一：
                # 带enemy_hp、带C、能被绿牌加C、能作为带enemy_hp绿牌的目标
                if (
                    card.enemy_hp < 0
                    or card.has_ability("C")
                    or (
                        has_green_with_c
                        and (
                            green_with_c_least_cost + card.cost
                            <= state.current_player.mana
                        )
                    )
                    or (
                        has_green_with_enemy_hp
                        and (
                            green_with_enemy_hp_least_cost + card.cost
                            <= state.current_player.mana
                        )
                    )
                ):
                    has_creature_to_summon = True
                    if card.area == Area.LANE1:
                        has_lane1_creature_to_summon = True
                    elif card.area == Area.LANE2:
                        has_lane2_creature_to_summon = True

                    for lane in Lane:
                        if len(c_lanes[lane]) < 3:
                            summon.append(Action(ActionType.SUMMON, origin, lane))

                            if card.area == Area.LANE2:  # cut: 相同操作
                                break

            elif isinstance(card, GreenItem):  # cut: 绿牌需满足场上有能攻击的随从或自身带enemy_hp

                if card.enemy_hp >= 0 and not c_has_able_to_attack:
                    continue

                skip = False
                for lane in Lane:

                    if not c_lanes[lane]:
                        continue

                    if c_able_to_attack[lane]:  # 优先给到能攻击的随从
                        candidate_targets = c_able_to_attack[lane]
                    elif card.enemy_hp < 0:  # 单纯打enemy_hp则随便指定一个目标
                        candidate_targets = c_lanes[lane][:1]
                    else:  # 0收益
                        continue

                    if card.area == Area.TARGET and len(candidate_targets) > 1:  # cut: TARGET法术目标去重
                        seen_cur = set()

                    for fci, friendly_creature in enumerate(candidate_targets):

                        if card.area == Area.TARGET and len(candidate_targets) > 1:
                            if fci == len(candidate_targets) - 1 and not seen_cur:
                                pass
                            else:
                                if friendly_creature.encoding in seen_cur:
                                    continue
                                seen_cur.add(friendly_creature.encoding)

                        target = friendly_creature.instance_id
                        use.append(Action(ActionType.USE, origin, target))
                        if card.area == Area.LANE1:  # cut: 相同操作
                            break
                        if card.area == Area.LANE2:  # cut: 相同操作
                            skip = True
                            break
                    if skip:
                        break

            elif isinstance(card, (RedItem, BlueItem)):
                skip = False
                for lane in Lane:

                    if card.area == Area.TARGET and len(o_lanes[lane]) > 1:  # cut: TARGET法术目标去重
                        seen_opp = set()

                    for eci, enemy_creature in enumerate(o_lanes[lane]):

                        # cut: 不扣对面血的法术没必要搞对面非嘲讽生物
                        if card.area == Area.TARGET:
                            if card.enemy_hp >= 0 and not enemy_creature.has_ability(
                                "G"
                            ):
                                continue

                            if len(o_lanes[lane]) > 1:
                                if eci == len(o_lanes[lane]) - 1 and not seen_opp:
                                    pass
                                else:
                                    if enemy_creature.encoding in seen_opp:
                                        continue
                                    seen_opp.add(enemy_creature.encoding)

                        elif card.area == Area.LANE1:
                            if card.enemy_hp >= 0 and not o_guards[lane]:
                                break
                        elif card.area == Area.LANE2:
                            if card.enemy_hp >= 0 and not o_has_guards:
                                skip = True
                                break

                        target = enemy_creature.instance_id
                        use.append(Action(ActionType.USE, origin, target))
                        if card.area == Area.LANE1:  # cut: 相同操作
                            break
                        if card.area == Area.LANE2:  # cut: 相同操作
                            skip = True
                            break
                    if skip:
                        break

                # cut: 配合 一开始先确定蓝牌对敌使用 后续不允许对敌使用蓝牌
                # if isinstance(card, BlueItem):
                #     use.append(Action(ActionType.USE, origin, None))

        for lane in Lane:

            if not o_guards[lane] and not o_lanes[lane]:
                continue

            for friendly_creature in filter(Creature.able_to_attack, c_lanes[lane]):
                creature_str = friendly_creature.encoding  # f"{lane.value}_" + friendly_creature.encoding
                if creature_str in seen:
                    continue
                seen.add(creature_str)

                if o_guards[lane]:
                    valid_targets = o_guards[lane]
                else:
                    valid_targets = []

                    # cut: 允许占了格子的生物攻击对面非嘲讽，必须能送掉用于召唤生物
                    if not has_creature_to_summon:
                        pass
                    elif friendly_creature.has_ability("W"):
                        pass
                    elif (
                        (has_creature_to_summon and len(c_lanes[lane]) >= 3)
                        or (has_lane1_creature_to_summon and len(c_lanes[lane]) >= 2)
                        or (has_lane2_creature_to_summon and len(c_lanes[lane]) >= 3)
                    ):  # 卡格子才允许送
                        if len(o_lanes[lane]) > 1:  # cut: 攻击目标去重
                            seen_opp = set()
                        for eci, enemy_creature in enumerate(o_lanes[lane]):
                            if (
                                friendly_creature.defense <= enemy_creature.attack
                                or enemy_creature.has_ability("L")
                            ):
                                if len(o_lanes[lane]) > 1:
                                    if eci == len(o_lanes[lane]) - 1 and not seen_opp:
                                        pass
                                    else:
                                        if enemy_creature.encoding in seen_opp:
                                            continue
                                        seen_opp.add(enemy_creature.encoding)
                                valid_targets.append(enemy_creature)
                    else:
                        pass

                for valid_target in valid_targets:
                    attack.append(
                        Action(
                            ActionType.ATTACK,
                            friendly_creature.instance_id,
                            valid_target.instance_id,
                        )
                    )

        # 出栈优先级
        return summon + attack + use

def state_encoding_for_otk(state: State) -> tuple:
    """
    编码战斗状态，用于otk比较两个状态是否相同
    """
    encoding = tuple()

    p, o = state.current_player, state.opposing_player

    encoding += (p.mana, o.health)  # cut: otk不关心我方血量等等

    for idx, cards in enumerate(
        (p.hand, p.lanes[0], p.lanes[1], o.lanes[0], o.lanes[1])
    ):
        if idx == 0:
            encoding_fun = hand_card_encoding_for_otk
        elif idx == 1 or idx == 2:
            encoding_fun = cur_board_card_encoding_for_otk
        else:
            encoding_fun = opp_board_card_encoding_for_otk

        # cut: 相同属性卡牌的不同次序去重
        sorted_cards_encoding = [encoding_fun(card) for card in cards]
        sorted_cards_encoding.sort()

        encoding += (idx, len(cards))
        encoding += tuple(sorted_cards_encoding)

    return encoding

def hand_card_encoding_for_otk(card: Card) -> tuple:
    # cut: 不关心instance_id, player_hp, card_draw等otk无关属性
    keywords = tuple(sorted(card.keywords))
    encoding = (
        card.type, card.cost, card.attack, card.defense,
        keywords, card.enemy_hp, card.area.value,
    )
    card.encoding = encoding
    return encoding

def cur_board_card_encoding_for_otk(card: Creature) -> tuple:
    keywords = tuple(sorted(card.keywords))
    encoding = (
        card.attack, card.defense,
        keywords, card.can_attack, card.has_attacked_this_turn,
    )
    card.encoding = encoding
    return encoding

def opp_board_card_encoding_for_otk(card: Creature) -> tuple:
    keywords = tuple(sorted(card.keywords))
    encoding = (
        card.attack, card.defense,
        keywords,
    )
    card.encoding = encoding
    return encoding

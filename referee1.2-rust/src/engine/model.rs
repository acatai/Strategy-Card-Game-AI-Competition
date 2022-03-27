use crate::engine::constants::{
    ACTIONS, DRAFT_LENGTH, HAND_SIZE, INITIAL_HEALTH, INITIAL_TURN_DRAW, LANES, LANE_SIZE,
    MAX_MANA, RUNE, SUICIDE_TURN,
};
use arrayvec::ArrayVec;
use std::convert::TryFrom;
use std::mem::swap;
use std::ops::{AddAssign, SubAssign};

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Action {
    AttackCard { id1: u8, id2: u8 },
    AttackFace { id: u8 },
    Pass,
    Summon { id: u8, lane: u8 },
    UseOnCard { id1: u8, id2: u8 },
    UseOnFace { id: u8 },
}

pub type Actions = ArrayVec<[Action; ACTIONS]>;

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum AttackState {
    AlreadyAttacked,
    CanAttack,
    NoAttack,
}

#[derive(Clone, Copy, Debug)]
pub struct Card {
    pub attack: i8,
    pub attack_state: AttackState,
    pub card_draw: i8,
    pub card_number: u8,
    pub card_type: Type,
    pub cost: u8,
    pub defense: i8,
    pub keywords: Keywords,
    pub instance_id: u8,
    pub lane: u8,
    pub location: Location,
    pub my_health_change: i8,
    pub op_health_change: i8,
}

impl Card {
    pub fn battle(mut self, target: Self) -> Self {
        if self.has(Keyword::Ward) {
            if target.attack > 0 {
                self.del(Keyword::Ward);
            }
        } else if target.has(Keyword::Lethal) {
            self.defense = 0;
        } else {
            self.defense -= target.attack;
        }

        self
    }

    pub fn del(&mut self, keyword: Keyword) {
        self.keywords.del(keyword)
    }

    pub const fn has(&self, keyword: Keyword) -> bool {
        self.keywords.has(keyword)
    }
}

pub type Deck = ArrayVec<[Card; DRAFT_LENGTH]>;

#[derive(Clone, Copy, Debug)]
pub enum Keyword {
    Breakthrough = 0b0000_0001,
    Charge = 0b0000_0010,
    Drain = 0b0000_0100,
    Guard = 0b0000_1000,
    Lethal = 0b0001_0000,
    Ward = 0b0010_0000,
}

#[derive(Clone, Copy, Debug, Default)]
pub struct Keywords {
    mask: u8,
}

impl Keywords {
    pub fn add(&mut self, keyword: Keyword) {
        self.mask |= keyword as u8;
    }

    pub fn del(&mut self, keyword: Keyword) {
        self.mask &= !(keyword as u8);
    }

    pub const fn has(self, keyword: Keyword) -> bool {
        self.mask & (keyword as u8) != 0
    }

    pub fn set(&mut self, keyword: Keyword, value: bool) {
        match (self.has(keyword), value) {
            (true, false) => self.del(keyword),
            (false, true) => self.add(keyword),
            _ => (),
        }
    }
}

impl AddAssign for Keywords {
    #[allow(clippy::suspicious_op_assign_impl)]
    fn add_assign(&mut self, other: Self) {
        self.mask |= other.mask;
    }
}

impl SubAssign for Keywords {
    fn sub_assign(&mut self, other: Self) {
        self.mask &= !other.mask;
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Location {
    InHand,
    MyBoard,
    OpBoard,
}

#[derive(Clone, Debug)]
pub struct Gamer {
    pub boards: [ArrayVec<[Card; LANE_SIZE]>; LANES],
    pub bonus_mana: bool,
    pub current_mana: u8,
    pub decksize: i8,
    pub hand: ArrayVec<[Card; HAND_SIZE]>,
    pub health: i8,
    pub max_mana: u8,
    pub next_turn_draw: i8,
    pub rune: i8,
}

impl Gamer {
    pub fn card_on_board(&self, instance_id: u8) -> (usize, usize, Card) {
        for (lane, board) in self.boards.iter().enumerate() {
            for (index, card) in board.iter().enumerate() {
                if card.instance_id == instance_id {
                    return (lane, index, *card);
                }
            }
        }

        unreachable!();
    }

    pub fn draw(&mut self, deck: &mut Deck, turn: u8) {
        for _ in 0..self.next_turn_draw {
            if self.decksize == 0 || turn > SUICIDE_TURN {
                self.modify_health(self.rune - self.health);
                if self.decksize == 0 {
                    continue;
                }
            }

            if self.hand.len() == HAND_SIZE {
                break;
            }

            self.hand.push(deck.pop().unwrap());
            self.decksize -= 1;
        }

        self.next_turn_draw = INITIAL_TURN_DRAW;
    }

    pub fn modify_health(&mut self, diff: i8) {
        self.health += diff;
        while self.health <= self.rune {
            self.next_turn_draw += 1;
            self.rune = 0.max(self.rune - RUNE);
            if self.rune == 0 {
                break;
            }
        }
    }

    pub fn update(&mut self, lane: usize, index: usize, card: Card) {
        if card.defense > 0 {
            self.boards[lane][index] = card;
        } else {
            self.boards[lane].remove(index);
        }
    }
}

impl Default for Gamer {
    fn default() -> Self {
        Self {
            boards: Default::default(),
            bonus_mana: false,
            current_mana: 0,
            decksize: 0,
            hand: ArrayVec::default(),
            health: INITIAL_HEALTH,
            max_mana: 0,
            next_turn_draw: INITIAL_TURN_DRAW,
            rune: INITIAL_HEALTH - RUNE,
        }
    }
}

#[derive(Clone, Debug)]
pub struct State {
    pub halt: bool,
    pub me: Gamer,
    pub op: Gamer,
}

impl State {
    #[allow(clippy::cognitive_complexity)]
    pub fn apply_action(&mut self, action: Action) {
        use Action::{AttackCard, AttackFace, Pass, Summon, UseOnCard, UseOnFace};
        use AttackState::{AlreadyAttacked, CanAttack, NoAttack};
        use Keyword::{Breakthrough, Charge, Drain, Ward};
        use Location::{InHand, MyBoard, OpBoard};
        use Type::{Creature, ItemBlue, ItemGreen, ItemRed};

        match action {
            AttackCard { id1, id2 } => {
                let (lane1, index1, mut creature1) = self.me.card_on_board(id1);
                debug_assert!(creature1.attack_state == CanAttack);
                debug_assert!(creature1.card_type == Creature);
                debug_assert!(creature1.location == MyBoard);

                let (lane2, index2, creature2) = self.op.card_on_board(id2);
                debug_assert!(creature2.card_type == Creature);
                debug_assert!(creature2.location == OpBoard);

                creature1.attack_state = AlreadyAttacked;

                self.me.update(lane1, index1, creature1.battle(creature2));
                self.op.update(lane2, index2, creature2.battle(creature1));

                if creature1.attack > 0 && !creature2.has(Ward) {
                    if creature1.has(Drain) {
                        self.me.modify_health(creature1.attack);
                    }
                    if creature1.has(Breakthrough) && creature1.attack > creature2.defense {
                        self.op.modify_health(creature2.defense - creature1.attack);
                    }
                }
            }
            AttackFace { id } => {
                let (lane, index, mut creature) = self.me.card_on_board(id);
                debug_assert!(creature.attack_state == CanAttack);
                debug_assert!(creature.card_type == Creature);
                debug_assert!(creature.location == MyBoard);

                creature.attack_state = AlreadyAttacked;

                self.me.update(lane, index, creature);

                if creature.has(Drain) {
                    self.me.modify_health(creature.attack)
                }
                self.op.modify_health(-creature.attack);
            }
            Pass => {
                self.halt = true;
            }
            Summon { id, lane } => {
                let mut creature = self.card_from_hand(id);
                debug_assert!(creature.card_type == Creature);
                debug_assert!(creature.location == InHand);

                creature.attack_state = if creature.has(Charge) {
                    CanAttack
                } else {
                    NoAttack
                };

                if cfg!(debug_assertions) {
                    creature.location = MyBoard;
                }

                self.me.boards[lane as usize].push(creature);
            }
            UseOnCard { id1, id2 } => {
                let item = self.card_from_hand(id1);
                debug_assert!(item.card_type != Creature);
                debug_assert!(item.location == InHand);

                let owner = if item.card_type == ItemGreen {
                    &mut self.me
                } else {
                    &mut self.op
                };

                let (lane, index, mut creature) = owner.card_on_board(id2);
                debug_assert!(creature.card_type == Creature);
                debug_assert!(creature.location != MyBoard || item.card_type == ItemGreen);
                debug_assert!(creature.location != OpBoard || item.card_type != ItemGreen);

                match item.card_type {
                    Creature => unreachable!(),
                    ItemBlue | ItemRed => {
                        creature.attack = 0.max(creature.attack - item.attack);
                        creature.keywords -= item.keywords;

                        if item.defense > 0 {
                            if creature.has(Ward) {
                                creature.del(Ward);
                            } else {
                                creature.defense -= item.defense;
                            }
                        }
                    }
                    ItemGreen => {
                        creature.attack += item.attack;
                        creature.defense += item.defense;
                        creature.keywords += item.keywords;

                        if item.has(Charge) && creature.attack_state != AlreadyAttacked {
                            creature.attack_state = CanAttack;
                        }
                    }
                }

                owner.update(lane, index, creature);
            }
            UseOnFace { id } => {
                let item = self.card_from_hand(id);
                debug_assert!(item.card_type == ItemBlue);
                debug_assert!(item.location == InHand);

                self.op.modify_health(-item.defense);
            }
        }
    }

    pub fn card_from_hand(&mut self, instance_id: u8) -> Card {
        let index = self
            .me
            .hand
            .iter()
            .position(|card| card.instance_id == instance_id)
            .unwrap();

        let card = self.me.hand.remove(index);
        self.me.current_mana -= card.cost;
        self.me.next_turn_draw += card.card_draw;
        self.me.modify_health(card.my_health_change);
        self.op.modify_health(card.op_health_change);
        card
    }

    pub fn compute_actions(&self) -> Actions {
        let mut actions = Actions::default();
        if self.halt {
            return actions;
        }

        actions.push(Action::Pass);

        let mut targets: ArrayVec<[u8; LANE_SIZE]> = ArrayVec::default();
        for (me, op) in self.me.boards.iter().zip(&self.op.boards) {
            targets.truncate(0);

            for card in op.iter() {
                if card.has(Keyword::Guard) {
                    targets.push(card.instance_id);
                }
            }

            let has_guards = !targets.is_empty();
            if !has_guards {
                for card in op.iter() {
                    targets.push(card.instance_id);
                }
            }

            for card in me.iter() {
                if card.attack_state == AttackState::CanAttack {
                    if !has_guards {
                        actions.push(Action::AttackFace {
                            id: card.instance_id,
                        });
                    }

                    for target in targets.iter().copied() {
                        actions.push(Action::AttackCard {
                            id1: card.instance_id,
                            id2: target,
                        });
                    }
                }
            }
        }

        for card in self.me.hand.iter() {
            if card.cost > self.me.current_mana {
                continue;
            }

            match card.card_type {
                Type::Creature => {
                    for (lane, board) in self.me.boards.iter().enumerate() {
                        if board.len() < LANE_SIZE {
                            actions.push(Action::Summon {
                                id: card.instance_id,
                                lane: u8::try_from(lane).unwrap(),
                            })
                        }
                    }
                }
                Type::ItemBlue | Type::ItemRed => {
                    if card.card_type == Type::ItemBlue {
                        actions.push(Action::UseOnFace {
                            id: card.instance_id,
                        });
                    }

                    for board in &self.op.boards {
                        for creature in board.iter() {
                            actions.push(Action::UseOnCard {
                                id1: card.instance_id,
                                id2: creature.instance_id,
                            });
                        }
                    }
                }
                Type::ItemGreen => {
                    for board in &self.me.boards {
                        for creature in board.iter() {
                            actions.push(Action::UseOnCard {
                                id1: card.instance_id,
                                id2: creature.instance_id,
                            });
                        }
                    }
                }
            }
        }

        actions
    }

    pub const fn is_game_over(&self) -> bool {
        self.me.health <= 0 || self.op.health <= 0
    }

    pub fn recharge_mana(&mut self, turn: u8) {
        self.me.bonus_mana = self.me.bonus_mana && (turn == 1 || self.me.current_mana > 0);
        self.me.max_mana = MAX_MANA.min(turn) + (if self.me.bonus_mana { 1 } else { 0 });
        self.me.current_mana = self.me.max_mana;
    }

    pub fn recharge_creatures(&mut self) {
        for owner in &mut [&mut self.me, &mut self.op] {
            for board in &mut owner.boards {
                for card in board.iter_mut() {
                    card.attack_state = AttackState::CanAttack;
                }
            }
        }
    }

    pub fn swap(&mut self) {
        self.halt = false;
        swap(&mut self.me, &mut self.op);

        if cfg!(debug_assertions) {
            for board in &mut self.me.boards {
                for card in board.iter_mut() {
                    card.location = Location::MyBoard;
                }
            }

            for board in &mut self.op.boards {
                for card in board.iter_mut() {
                    card.location = Location::OpBoard;
                }
            }
        }
    }
}

impl Default for State {
    fn default() -> Self {
        let mut state = Self {
            halt: false,
            me: Gamer::default(),
            op: Gamer::default(),
        };
        state.op.bonus_mana = true;
        state
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Type {
    Creature,
    ItemBlue,
    ItemGreen,
    ItemRed,
}

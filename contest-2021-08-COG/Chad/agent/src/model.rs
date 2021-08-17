use crate::parser::{parse_next, Cards, OpponentStatus, PlayerStatus};

use std::collections::{HashMap, HashSet};
use std::fmt;
use std::str::FromStr;

use bitmask::bitmask;
use derive_new::new;
use failure::Fail;
use num_enum::TryFromPrimitive;
use shrinkwraprs::Shrinkwrap;

pub const LANES_NUM: usize = 2;
pub const MAX_CREATURES: usize = 3;

#[allow(unused_macros)]
macro_rules! init_array {
    ($val:expr; $size:expr; $type:ty) => {{
        use std::mem;

        let mut array = mem::MaybeUninit::<[_; $size]>::uninit();
        let array_ptr = array.as_mut_ptr() as *mut $type;

        for i in 0..$size {
            unsafe {
                array_ptr.offset(i as _).write($val);
            }
        }

        unsafe { array.assume_init() }
    }};
}

bitmask! {
    pub mask AbilitiesMask: u8 where flags Abilities {
        Breakthrough = 0b0000_0001,
        Charge       = 0b0000_0010,
        Drain        = 0b0000_0100,
        Guard        = 0b0000_1000,
        Lethal       = 0b0001_0000,
        Ward         = 0b0010_0000,
    }
}

impl AbilitiesMask {
    #[inline]
    #[allow(dead_code)]
    pub const fn from_u8(mask: u8) -> Self {
        Self { mask }
    }
}

impl FromStr for AbilitiesMask {
    type Err = ();

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        use Abilities::*;

        let mut mask = AbilitiesMask::none();

        for c in s.chars() {
            mask |= match c {
                'B' => Breakthrough,
                'C' => Charge,
                'D' => Drain,
                'G' => Guard,
                'L' => Lethal,
                'W' => Ward,
                _ => continue,
            };
        }

        Ok(mask)
    }
}

impl fmt::Display for AbilitiesMask {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        const F: impl FnOnce(AbilitiesMask, char) -> char =
            |x, b| if x.is_none() { '-' } else { b };
        use Abilities::*;

        write!(
            f,
            "{}{}{}{}{}{}",
            F(*self & Breakthrough, 'B'),
            F(*self & Charge, 'C'),
            F(*self & Drain, 'D'),
            F(*self & Guard, 'G'),
            F(*self & Lethal, 'L'),
            F(*self & Ward, 'W'),
        )
    }
}

impl fmt::Debug for AbilitiesMask {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "AbilitiesMask({})", self)
    }
}

#[derive(Debug, PartialEq, TryFromPrimitive)]
#[repr(i8)]
pub enum CardLocation {
    PlayerHand = 0,
    PlayerBoard = 1,
    OpponentBoard = -1,
}

#[derive(Debug, Copy, Clone, PartialEq, TryFromPrimitive)]
#[repr(u8)]
pub enum CardType {
    Creature = 0,
    GreenItem = 1,
    RedItem = 2,
    BlueItem = 3,
}

#[derive(Debug, Copy, Clone, PartialEq)]
pub enum AttackState {
    Ready,
    Used,
    Hold,
}

impl AttackState {
    pub fn charge(&mut self) {
        use AttackState::*;
        if *self == Hold {
            *self = Ready;
        }
    }

    pub fn ready(self) -> bool {
        use AttackState::*;
        self == Ready
    }
}

#[derive(Debug, Copy, Clone, PartialEq)]
pub struct Card {
    pub id: usize,
    pub instance_id: isize,
    pub card_type: CardType,
    pub cost: usize,
    pub attack: isize,
    pub defense: isize,
    pub abilities: AbilitiesMask,
    pub player_hp: isize,
    pub enemy_hp: isize,
    pub card_draw: u8,
    pub attack_state: AttackState,
}

impl Card {
    // returns (drain, breakthrough)
    pub fn attack(&mut self, target: &mut Card) -> Result<(isize, isize), ActionError> {
        use Abilities::*;
        use ActionError::*;
        use CardType::*;
        if self.card_type != Creature {
            return Err(IllegalCardType {
                iid: self.instance_id,
            });
        }
        if target.card_type != Creature {
            return Err(IllegalCardType {
                iid: target.instance_id,
            });
        }

        let dmg_given = if target.abilities.contains(Ward) {
            0
        } else {
            self.attack
        };
        let dmg_taken = if self.abilities.contains(Ward) {
            0
        } else {
            target.attack
        };

        let self_dead =
            self.defense <= dmg_taken || (dmg_taken > 0 && target.abilities.contains(Lethal));
        let target_dead =
            target.defense <= dmg_given || (dmg_given > 0 && self.abilities.contains(Lethal));

        let health_gain = if dmg_given > 0 && self.abilities.contains(Drain) {
            self.attack
        } else {
            0
        };
        let health_taken = if dmg_given > target.defense && self.abilities.contains(Breakthrough) {
            dmg_given - target.defense
        } else {
            0
        };

        target.defense -= if target_dead {
            target.defense
        } else {
            dmg_given
        };
        self.defense -= if self_dead { self.defense } else { dmg_taken };

        self.attack_state = AttackState::Used;
        self.abilities.unset(Charge);
        self.abilities.unset(Ward);
        target.abilities.unset(Ward);
        Ok((health_gain, health_taken))
    }

    pub fn apply(&mut self, card: &Card) -> Result<(), ActionError> {
        use Abilities::*;
        use ActionError::*;
        use CardType::*;
        if self.card_type != Creature {
            return Err(IllegalCardType {
                iid: self.instance_id,
            });
        }
        match card.card_type {
            GreenItem => {
                self.abilities |= card.abilities;
                self.attack += card.attack;
                self.defense += card.defense;
                if self.abilities.contains(Charge) {
                    self.attack_state.charge();
                }
            }
            RedItem | BlueItem => {
                self.abilities &= !card.abilities;
                self.attack = self.attack.saturating_sub(card.attack);
                if card.defense > 0 {
                    if self.abilities.contains(Ward) {
                        self.abilities.unset(Ward);
                    } else {
                        self.defense -= card.defense;
                    }
                }
            }
            _ => {
                return Err(IllegalCardType {
                    iid: card.instance_id,
                })
            }
        }
        Ok(())
    }
}

#[derive(Debug, Default, Clone, PartialEq)]
pub struct BasePlayer {
    pub lanes: [Vec<Card>; LANES_NUM],
    pub hand: Vec<Card>,
    pub health: isize,
    pub mana: usize,
    pub extra_mana: bool,
    pub runes: u8,
    pub extra_draw: u8,
    pub player_order: u8,
}

impl BasePlayer {
    pub fn use_mana(&mut self, value: usize) -> Result<(), ()> {
        if value == self.mana + 1 && self.extra_mana {
            self.mana = 0;
            self.extra_mana = false;
            Ok(())
        } else if value <= self.mana {
            self.mana -= value;
            Ok(())
        } else {
            Err(())
        }
    }

    pub fn remove_rune(&mut self, empty_deck: bool) {
        if empty_deck {
            if self.health > self.runes as isize * 5 {
                self.health = self.runes as isize * 5;
            }
        } else {
            self.extra_draw += 1;
        }
        // should always be true...
        if self.runes > 0 {
            self.runes -= 1;
        }
    }

    pub fn all_mana(&self) -> usize {
        self.mana + if self.extra_mana { 1 } else { 0 }
    }

    pub fn recharge_lanes(&mut self) {
        for card in self.lanes.iter_mut().flatten() {
            card.attack_state = AttackState::Ready;
        }
    }

    pub fn update_battle(&mut self, stats: &PlayerStatus, board: &[(usize, Card)], round: usize) {
        const GET_LANE: impl FnOnce(&[(usize, Card)], usize) -> Vec<Card> = |vec, i| {
            vec.iter()
                .filter(|(n, _)| *n == i)
                .map(|(_, c)| *c)
                .collect()
        };

        for i in 0..LANES_NUM {
            self.lanes[i] = GET_LANE(board, i);
        }

        self.health = stats.health;
        self.mana = (round + 1).min(MAX_MANA);
        self.extra_mana = stats.mana > self.mana;
        self.runes = stats.rune;
    }

    pub fn hand(&self) -> &[Card] {
        &self.hand
    }

    pub fn get_hand(&self, iid: isize) -> Option<Card> {
        self.hand().iter().find(|c| c.instance_id == iid).cloned()
    }

    pub fn remove_hand(&mut self, iid: isize) -> Option<Card> {
        self.hand
            .iter()
            .position(|c| c.instance_id == iid)
            .map(|idx| self.hand.remove(idx))
    }

    pub fn apply_card(&mut self, card: &Card) -> Result<(), ()> {
        self.use_mana(card.cost)?;
        self.extra_draw += card.card_draw;
        self.health += card.player_hp;
        Ok(())
    }

    pub fn get_board(&self, iid: isize) -> Option<Card> {
        self.lanes
            .iter()
            .flat_map(|lane| lane.iter())
            .find(|c| c.instance_id == iid)
            .cloned()
    }

    pub fn set_board(&mut self, card: Card) -> Result<(), ()> {
        let (l, i) = self
            .lanes
            .iter()
            .enumerate()
            .find_map(|(l, lane)| {
                if let Some(i) = lane.iter().position(|c| c.instance_id == card.instance_id) {
                    Some((l, i))
                } else {
                    None
                }
            })
            .ok_or(())?;
        self.lanes[l][i] = card;
        Ok(())
    }

    pub fn add_board(&mut self, card: Card, lane: usize) -> Result<(), ()> {
        if lane >= LANES_NUM || self.lanes[lane].len() >= MAX_CREATURES {
            Err(())
        } else {
            self.lanes[lane].push(card);
            Ok(())
        }
    }

    pub fn remove_board(&mut self, iid: isize) -> Option<Card> {
        self.lanes
            .iter()
            .enumerate()
            .find_map(|(l, lane)| {
                lane.iter()
                    .position(|c| c.instance_id == iid)
                    .map(|i| (l, i))
            })
            .map(|(l, i)| self.lanes[l].remove(i))
    }
}

#[derive(Debug, Default, Clone, PartialEq)]
pub struct Player {
    pub base: BasePlayer,
    pub deck: Vec<Card>,
}

pub const DECK_SIZE: usize = 30;
pub const HAND_SIZE: usize = 8;
pub const MAX_MANA: usize = 12;

impl Player {
    pub fn new() -> Self {
        Self {
            base: BasePlayer::default(),
            deck: Vec::with_capacity(DECK_SIZE),
        }
    }

    pub fn draw_cards(&mut self) {
        let mut remove_rune = false;
        for _ in 0..=self.base.extra_draw {
            if let Some(card) = self.deck.pop() {
                if self.base.hand.len() < HAND_SIZE {
                    self.base.hand.push(card);
                }
            }
            // empty deck, remove rune
            else {
                remove_rune = true;
            }
        }
        self.base.extra_draw = 0;
        if remove_rune {
            self.base.remove_rune(self.deck.is_empty());
        }
    }

    pub fn update_draft(&mut self, cards: Cards, status: &PlayerStatus, opp_status: &PlayerStatus) {
        self.base.hand = cards.player_hand;
        self.base.player_order = if status.deck_size < opp_status.deck_size {
            2
        } else {
            1
        }
    }

    pub fn update_pick(&mut self, card: Card) {
        self.deck.push(card);
    }

    pub fn update_battle(
        &mut self,
        stats: PlayerStatus,
        hand: Vec<Card>,
        board: &[(usize, Card)],
        round: usize,
    ) {
        use std::collections::hash_map::Entry;
        self.base.update_battle(&stats, board, round);

        let hand_ids = self
            .base
            .hand
            .iter()
            .map(|card| card.instance_id)
            .collect::<HashSet<isize>>();

        if !self.deck.is_empty() {
            let mut drawn = hand
                .iter()
                .map(|card| (card.instance_id, card.id))
                .filter(|(iid, _)| !hand_ids.contains(iid))
                .fold(HashMap::<usize, usize>::new(), |mut set, (_, id)| {
                    *set.entry(id).or_insert(0) += 1;
                    set
                });

            self.deck = self
                .deck
                .iter()
                .filter(|card| {
                    if let Entry::Occupied(mut entry) = drawn.entry(card.id) {
                        if *entry.get() > 1 {
                            *entry.get_mut() -= 1;
                        } else {
                            entry.remove();
                        }
                        false
                    } else {
                        true
                    }
                })
                .copied()
                .collect::<Vec<_>>();
        }

        self.base.hand = hand;
    }

    pub fn update_battle_manual(&mut self) {
        // remove runes - set hp or add draw (if deck nonempty)
        while (self.base.health < (self.base.runes as isize * 5))
            && (self.base.health > 0)
            && (self.base.runes > 0)
        {
            self.base.remove_rune(self.deck.is_empty());
        }
        // draw cards from deck
        self.draw_cards();
    }
}

#[derive(Debug, PartialEq, Default, Clone)]
pub struct Opponent {
    pub base: BasePlayer,
    pub actions: Vec<(usize, Action)>,
    pub deck: Vec<Vec<Card>>,
    pub deck_used: Vec<usize>,
    pub deck_size: usize,
    pub hand: usize,
}

impl Opponent {
    pub fn new() -> Self {
        Self {
            base: BasePlayer::default(),
            actions: Vec::new(),
            deck: Vec::with_capacity(DECK_SIZE),
            deck_used: Vec::with_capacity(DECK_SIZE),
            deck_size: DECK_SIZE,
            hand: 0,
        }
    }

    pub fn update_draft(&mut self, cards: &[Card]) {
        self.deck.push(cards.to_vec());
    }

    pub fn update_battle(
        &mut self,
        stats: (PlayerStatus, OpponentStatus),
        board: &[(usize, Card)],
        round: usize,
    ) {
        use Action::*;
        let (base, extra) = stats;
        self.base.update_battle(&base, board, round);

        self.actions = extra.actions;

        let ids = self
            .actions
            .iter()
            .filter(|(_, action)| match action {
                Summon { .. } | Use { .. } | UseOpponent { .. } => true,
                _ => false,
            })
            .map(|(id, _)| id);

        let mut used_cards = 0;
        for id in ids {
            used_cards += 1;
            self.deck_used.push(*id);
        }

        self.deck_size -= extra.hand_size + used_cards - self.hand;
        self.hand = extra.hand_size;
    }
}

#[derive(Debug, Fail)]
pub enum ActionError {
    #[fail(display = "no card with instance id {} on hand", iid)]
    CardNotOnHand { iid: isize },
    #[fail(display = "no card with instance id {} on board", iid)]
    CardNotOnBoard { iid: isize },
    #[fail(display = "insufficient mana to preform this action")]
    InsufficientMana,
    #[fail(display = "card with instance id {} cannot perform this action", iid)]
    IllegalCardType { iid: isize },
    #[fail(display = "lane {} does not exist", idx)]
    LaneDoesNotExist { idx: usize },
    #[fail(display = "lane {} is at max capacity", idx)]
    LaneAtMaxCapacity { idx: usize },
}

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum Action {
    Summon { id: isize, lane: usize },
    Attack { id1: isize, id2: isize },
    AttackOpponent { id: isize },
    Use { id1: isize, id2: isize },
    UseOpponent { id: isize },
    Pick { idx: u8 },
    Pass,
}

impl FromStr for Action {
    type Err = ();

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        use Action::*;

        let mut splitted = s.split_whitespace();
        let action = splitted.next().ok_or(())?;

        Ok(match action {
            "SUMMON" => Summon {
                id: parse_next(splitted.by_ref()).ok_or(())?,
                lane: parse_next(splitted).ok_or(())?,
            },
            "ATTACK" => {
                let id1 = parse_next(splitted.by_ref()).ok_or(())?;
                let id2 = parse_next(splitted).ok_or(())?;

                if id2 != -1 {
                    Attack { id1, id2 }
                } else {
                    AttackOpponent { id: id1 }
                }
            }
            "USE" => {
                let id1 = parse_next(splitted.by_ref()).ok_or(())?;
                let id2 = parse_next(splitted).ok_or(())?;

                if id2 != -1 {
                    Use { id1, id2 }
                } else {
                    UseOpponent { id: id1 }
                }
            }
            "PICK" => Pick {
                idx: parse_next(splitted).ok_or(())?,
            },
            "PASS" => Pass,
            _ => return Err(()),
        })
    }
}

impl fmt::Display for Action {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        use Action::*;

        match self {
            Summon { id, lane } => write!(f, "SUMMON {} {}", id, lane),
            Attack { id1, id2 } => write!(f, "ATTACK {} {}", id1, id2),
            AttackOpponent { id } => write!(f, "ATTACK {} -1", id),
            Use { id1, id2 } => write!(f, "USE {} {}", id1, id2),
            UseOpponent { id } => write!(f, "USE {} -1", id),
            Pick { idx } => write!(f, "PICK {}", idx),
            Pass => write!(f, "PASS"),
        }
    }
}

impl Action {
    pub fn valid_actions(player: &BasePlayer, opponent: &BasePlayer) -> Vec<Action> {
        use Abilities::*;
        use Action::*;
        use CardType::*;

        let mana = player.all_mana();
        let mut actions = vec![];
        if player.health <= 0 {
            actions.push(Action::Pass);
            return actions;
        }
        // play card action
        player
            .hand
            .iter()
            .filter(|card| card.cost <= mana)
            .for_each(|card| match card.card_type {
                Creature => {
                    for i in 0..LANES_NUM {
                        if player.lanes[i].len() < MAX_CREATURES {
                            actions.push(Summon {
                                id: card.instance_id,
                                lane: i,
                            });
                        }
                    }
                }
                GreenItem => {
                    for i in 0..LANES_NUM {
                        for creature in player.lanes[i].iter() {
                            actions.push(Use {
                                id1: card.instance_id,
                                id2: creature.instance_id,
                            });
                        }
                    }
                }
                RedItem => {
                    for i in 0..LANES_NUM {
                        for creature in opponent.lanes[i].iter() {
                            actions.push(Use {
                                id1: card.instance_id,
                                id2: creature.instance_id,
                            });
                        }
                    }
                }
                BlueItem => {
                    actions.push(UseOpponent {
                        id: card.instance_id,
                    });
                    if card.defense < 0 {
                        for i in 0..LANES_NUM {
                            for creature in opponent.lanes[i].iter() {
                                actions.push(Use {
                                    id1: card.instance_id,
                                    id2: creature.instance_id,
                                });
                            }
                        }
                    }
                }
            });
        // creature attack action
        for i in 0..LANES_NUM {
            for creature in player.lanes[i].iter().filter(|c| c.attack_state.ready()) {
                if opponent.lanes[i]
                    .iter()
                    .any(|c| c.abilities.contains(Guard))
                {
                    opponent.lanes[i]
                        .iter()
                        .filter(|c| c.abilities.contains(Guard))
                        .for_each(|c| {
                            actions.push(Attack {
                                id1: creature.instance_id,
                                id2: c.instance_id,
                            });
                        });
                } else {
                    actions.push(AttackOpponent {
                        id: creature.instance_id,
                    });
                    for c in opponent.lanes[i].iter() {
                        actions.push(Attack {
                            id1: creature.instance_id,
                            id2: c.instance_id,
                        });
                    }
                }
            }
        }
        actions.push(Pass);
        actions
    }

    pub fn do_action(
        action: &Action,
        player: &mut BasePlayer,
        opponent: &mut BasePlayer,
    ) -> Result<(), ActionError> {
        use Abilities::*;
        use Action::*;
        use ActionError::*;
        use AttackState::*;
        use CardType::*;
        match *action {
            AttackOpponent { id } => {
                let mut card = player.get_board(id).ok_or(CardNotOnBoard { iid: id })?;
                card.attack_state = Used;
                if card.abilities.contains(Drain) {
                    player.health += card.attack;
                }
                opponent.health -= card.attack;
                player.set_board(card).ok();
            }
            Attack { id1, id2 } => {
                let mut source = player.get_board(id1).ok_or(CardNotOnBoard { iid: id1 })?;
                let mut target = opponent.get_board(id2).ok_or(CardNotOnBoard { iid: id2 })?;
                let (drain, breakthrough) = source.attack(&mut target)?;

                player.health += drain;
                opponent.health -= breakthrough;

                if source.defense > 0 {
                    player.set_board(source).ok();
                } else {
                    player.remove_board(source.instance_id);
                };
                if target.defense > 0 {
                    opponent.set_board(target).ok();
                } else {
                    opponent.remove_board(target.instance_id);
                }
            }
            Summon { id, lane } => {
                if lane >= LANES_NUM {
                    return Err(LaneDoesNotExist { idx: lane });
                }
                let mut card = player.remove_hand(id).ok_or(CardNotOnHand { iid: id })?;

                player.apply_card(&card).map_err(|_| InsufficientMana)?;
                opponent.health += card.enemy_hp;

                if card.abilities.contains(Charge) {
                    card.attack_state.charge();
                } else {
                    card.attack_state = Hold;
                }
                player
                    .add_board(card, lane)
                    .map_err(|_| LaneAtMaxCapacity { idx: lane })?;
            }
            UseOpponent { id } => {
                let card = player.remove_hand(id).ok_or(CardNotOnHand { iid: id })?;

                player.apply_card(&card).map_err(|_| InsufficientMana)?;
                opponent.health += card.enemy_hp - card.defense;
            }
            Use { id1, id2 } => {
                let card = player.remove_hand(id1).ok_or(CardNotOnHand { iid: id1 })?;

                player.apply_card(&card).map_err(|_| InsufficientMana)?;
                opponent.health += card.enemy_hp;

                let owner = if card.card_type == GreenItem {
                    player
                } else {
                    opponent
                };
                let mut target = owner.get_board(id2).ok_or(CardNotOnBoard { iid: id2 })?;

                target.apply(&card)?;
                if target.defense > 0 {
                    owner.set_board(target).ok();
                } else {
                    owner.remove_board(target.instance_id);
                }
            }
            _ => (),
        }
        Ok(())
    }
}

#[derive(Shrinkwrap, Default, new)]
#[shrinkwrap(mutable)]
pub struct ActionChain(pub Vec<Action>);

impl fmt::Display for ActionChain {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "{}",
            self.iter()
                .map(ToString::to_string)
                .collect::<Vec<_>>()
                .join("; ")
        )
    }
}

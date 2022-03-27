use crate::agents::AgentGreedy;
use crate::engine::{Card, Keyword, State};
use crate::evolution::constants::MUTATION;
use crate::evolution::individuals::Individual;
use lazy_static::lazy_static;
use rand::distributions::{Distribution, Standard, Uniform};
use rand::Rng;
use std::ops::{Index, IndexMut};

lazy_static! {
    static ref LITERAL: Uniform<f32> = Uniform::new(-1.0, 1.0);
}

#[derive(Clone, Debug)]
pub enum CardNode {
    FeatureAttack,
    FeatureDefense,
    FeatureHasBreakthrough,
    FeatureHasCharge,
    FeatureHasDrain,
    FeatureHasGuard,
    FeatureHasLethal,
    FeatureHasWard,
    Literal(f32),
    OperatorAdd(Box<Self>, Box<Self>),
    OperatorMax(Box<Self>, Box<Self>),
    OperatorMin(Box<Self>, Box<Self>),
    OperatorMul(Box<Self>, Box<Self>),
    OperatorSub(Box<Self>, Box<Self>),
}

impl CardNode {
    fn evaluate(&self, card: &Card) -> f32 {
        macro_rules! has {
            ($keyword:tt) => {
                if card.has(Keyword::$keyword) {
                    1.0
                } else {
                    0.0
                }
            };
        }

        match self {
            Self::FeatureAttack => f32::from(card.attack),
            Self::FeatureDefense => f32::from(card.defense),
            Self::FeatureHasBreakthrough => has!(Breakthrough),
            Self::FeatureHasCharge => has!(Charge),
            Self::FeatureHasDrain => has!(Drain),
            Self::FeatureHasGuard => has!(Guard),
            Self::FeatureHasLethal => has!(Lethal),
            Self::FeatureHasWard => has!(Ward),
            Self::Literal(value) => *value,
            Self::OperatorAdd(l, r) => l.evaluate(card) + r.evaluate(card),
            Self::OperatorMax(l, r) => l.evaluate(card).max(r.evaluate(card)),
            Self::OperatorMin(l, r) => l.evaluate(card).min(r.evaluate(card)),
            Self::OperatorMul(l, r) => l.evaluate(card) * r.evaluate(card),
            Self::OperatorSub(l, r) => l.evaluate(card) - r.evaluate(card),
        }
    }

    const fn size(&self) -> usize {
        match self {
            Self::FeatureAttack
            | Self::FeatureDefense
            | Self::FeatureHasBreakthrough
            | Self::FeatureHasCharge
            | Self::FeatureHasDrain
            | Self::FeatureHasGuard
            | Self::FeatureHasLethal
            | Self::FeatureHasWard
            | Self::Literal(_) => 1,
            Self::OperatorAdd(l, r)
            | Self::OperatorMax(l, r)
            | Self::OperatorMin(l, r)
            | Self::OperatorMul(l, r)
            | Self::OperatorSub(l, r) => 1 + l.size() + r.size(),
        }
    }
}

impl Default for CardNode {
    fn default() -> Self {
        Self::Literal(0.0)
    }
}

impl Distribution<CardNode> for Standard {
    fn sample<R: Rng + ?Sized>(&self, rng: &mut R) -> CardNode {
        match rng.gen_range(0..14) {
            0 => CardNode::FeatureAttack,
            1 => CardNode::FeatureDefense,
            2 => CardNode::FeatureHasBreakthrough,
            3 => CardNode::FeatureHasCharge,
            4 => CardNode::FeatureHasDrain,
            5 => CardNode::FeatureHasGuard,
            6 => CardNode::FeatureHasLethal,
            7 => CardNode::FeatureHasWard,
            8 => CardNode::Literal(LITERAL.sample(rng)),
            9 => CardNode::OperatorAdd(Box::new(rng.gen()), Box::new(rng.gen())),
            10 => CardNode::OperatorMax(Box::new(rng.gen()), Box::new(rng.gen())),
            11 => CardNode::OperatorMin(Box::new(rng.gen()), Box::new(rng.gen())),
            12 => CardNode::OperatorMul(Box::new(rng.gen()), Box::new(rng.gen())),
            13 => CardNode::OperatorSub(Box::new(rng.gen()), Box::new(rng.gen())),
            _ => unreachable!(),
        }
    }
}

impl Index<usize> for CardNode {
    type Output = Self;

    fn index(&self, index: usize) -> &Self::Output {
        if index == 0 {
            return self;
        }

        match self {
            Self::FeatureAttack
            | Self::FeatureDefense
            | Self::FeatureHasBreakthrough
            | Self::FeatureHasCharge
            | Self::FeatureHasDrain
            | Self::FeatureHasGuard
            | Self::FeatureHasLethal
            | Self::FeatureHasWard
            | Self::Literal(_) => unreachable!(),
            Self::OperatorAdd(l, r)
            | Self::OperatorMax(l, r)
            | Self::OperatorMin(l, r)
            | Self::OperatorMul(l, r)
            | Self::OperatorSub(l, r) => {
                if index - 1 < l.size() {
                    &l[index - 1]
                } else {
                    &r[index - 1 - l.size()]
                }
            }
        }
    }
}

impl IndexMut<usize> for CardNode {
    fn index_mut(&mut self, index: usize) -> &mut Self::Output {
        if index == 0 {
            return self;
        }

        match self {
            Self::FeatureAttack
            | Self::FeatureDefense
            | Self::FeatureHasBreakthrough
            | Self::FeatureHasCharge
            | Self::FeatureHasDrain
            | Self::FeatureHasGuard
            | Self::FeatureHasLethal
            | Self::FeatureHasWard
            | Self::Literal(_) => unreachable!(),
            Self::OperatorAdd(l, r)
            | Self::OperatorMax(l, r)
            | Self::OperatorMin(l, r)
            | Self::OperatorMul(l, r)
            | Self::OperatorSub(l, r) => {
                if index - 1 < l.size() {
                    &mut l[index - 1]
                } else {
                    &mut r[index - 1 - l.size()]
                }
            }
        }
    }
}

#[derive(Clone, Debug)]
pub enum StateNode {
    FeatureMeCurrentMana,
    FeatureMeDecksize,
    FeatureMeHealth,
    FeatureMeMaxMana,
    FeatureMeNextTurnDraw,
    FeatureMeRune,
    FeatureOpCurrentMana,
    FeatureOpDecksize,
    FeatureOpHealth,
    FeatureOpMaxMana,
    FeatureOpNextTurnDraw,
    FeatureOpRune,
    Literal(f32),
    OperatorAdd(Box<Self>, Box<Self>),
    OperatorMax(Box<Self>, Box<Self>),
    OperatorMin(Box<Self>, Box<Self>),
    OperatorMul(Box<Self>, Box<Self>),
    OperatorSub(Box<Self>, Box<Self>),
}

impl StateNode {
    fn evaluate(&self, state: &State) -> f32 {
        match self {
            Self::FeatureMeCurrentMana => f32::from(state.me.current_mana),
            Self::FeatureMeDecksize => f32::from(state.me.decksize),
            Self::FeatureMeHealth => f32::from(state.me.health),
            Self::FeatureMeMaxMana => f32::from(state.me.max_mana),
            Self::FeatureMeNextTurnDraw => f32::from(state.me.next_turn_draw),
            Self::FeatureMeRune => f32::from(state.me.rune),
            Self::FeatureOpCurrentMana => f32::from(state.op.current_mana),
            Self::FeatureOpDecksize => f32::from(state.op.decksize),
            Self::FeatureOpHealth => f32::from(state.op.health),
            Self::FeatureOpMaxMana => f32::from(state.op.max_mana),
            Self::FeatureOpNextTurnDraw => f32::from(state.op.next_turn_draw),
            Self::FeatureOpRune => f32::from(state.op.rune),
            Self::Literal(value) => *value,
            Self::OperatorAdd(l, r) => l.evaluate(state) + r.evaluate(state),
            Self::OperatorMax(l, r) => l.evaluate(state).max(r.evaluate(state)),
            Self::OperatorMin(l, r) => l.evaluate(state).min(r.evaluate(state)),
            Self::OperatorMul(l, r) => l.evaluate(state) * r.evaluate(state),
            Self::OperatorSub(l, r) => l.evaluate(state) - r.evaluate(state),
        }
    }

    const fn size(&self) -> usize {
        match self {
            Self::FeatureMeCurrentMana
            | Self::FeatureMeDecksize
            | Self::FeatureMeHealth
            | Self::FeatureMeMaxMana
            | Self::FeatureMeNextTurnDraw
            | Self::FeatureMeRune
            | Self::FeatureOpCurrentMana
            | Self::FeatureOpDecksize
            | Self::FeatureOpHealth
            | Self::FeatureOpMaxMana
            | Self::FeatureOpNextTurnDraw
            | Self::FeatureOpRune
            | Self::Literal(_) => 1,
            Self::OperatorAdd(l, r)
            | Self::OperatorMax(l, r)
            | Self::OperatorMin(l, r)
            | Self::OperatorMul(l, r)
            | Self::OperatorSub(l, r) => 1 + l.size() + r.size(),
        }
    }
}

impl Default for StateNode {
    fn default() -> Self {
        Self::Literal(0.0)
    }
}

impl Distribution<StateNode> for Standard {
    fn sample<R: Rng + ?Sized>(&self, rng: &mut R) -> StateNode {
        match rng.gen_range(0..18) {
            0 => StateNode::FeatureMeCurrentMana,
            1 => StateNode::FeatureMeDecksize,
            2 => StateNode::FeatureMeHealth,
            3 => StateNode::FeatureMeMaxMana,
            4 => StateNode::FeatureMeNextTurnDraw,
            5 => StateNode::FeatureMeRune,
            6 => StateNode::FeatureOpCurrentMana,
            7 => StateNode::FeatureOpDecksize,
            8 => StateNode::FeatureOpHealth,
            9 => StateNode::FeatureOpMaxMana,
            10 => StateNode::FeatureOpNextTurnDraw,
            11 => StateNode::FeatureOpRune,
            12 => StateNode::Literal(LITERAL.sample(rng)),
            13 => StateNode::OperatorAdd(Box::new(rng.gen()), Box::new(rng.gen())),
            14 => StateNode::OperatorMax(Box::new(rng.gen()), Box::new(rng.gen())),
            15 => StateNode::OperatorMin(Box::new(rng.gen()), Box::new(rng.gen())),
            16 => StateNode::OperatorMul(Box::new(rng.gen()), Box::new(rng.gen())),
            17 => StateNode::OperatorSub(Box::new(rng.gen()), Box::new(rng.gen())),
            _ => unreachable!(),
        }
    }
}

impl Index<usize> for StateNode {
    type Output = Self;

    fn index(&self, index: usize) -> &Self::Output {
        if index == 0 {
            return self;
        }

        match self {
            Self::FeatureMeCurrentMana
            | Self::FeatureMeDecksize
            | Self::FeatureMeHealth
            | Self::FeatureMeMaxMana
            | Self::FeatureMeNextTurnDraw
            | Self::FeatureMeRune
            | Self::FeatureOpCurrentMana
            | Self::FeatureOpDecksize
            | Self::FeatureOpHealth
            | Self::FeatureOpMaxMana
            | Self::FeatureOpNextTurnDraw
            | Self::FeatureOpRune
            | Self::Literal(_) => unreachable!(),
            Self::OperatorAdd(l, r)
            | Self::OperatorMax(l, r)
            | Self::OperatorMin(l, r)
            | Self::OperatorMul(l, r)
            | Self::OperatorSub(l, r) => {
                if index - 1 < l.size() {
                    &l[index - 1]
                } else {
                    &r[index - 1 - l.size()]
                }
            }
        }
    }
}

impl IndexMut<usize> for StateNode {
    fn index_mut(&mut self, index: usize) -> &mut Self::Output {
        if index == 0 {
            return self;
        }

        match self {
            Self::FeatureMeCurrentMana
            | Self::FeatureMeDecksize
            | Self::FeatureMeHealth
            | Self::FeatureMeMaxMana
            | Self::FeatureMeNextTurnDraw
            | Self::FeatureMeRune
            | Self::FeatureOpCurrentMana
            | Self::FeatureOpDecksize
            | Self::FeatureOpHealth
            | Self::FeatureOpMaxMana
            | Self::FeatureOpNextTurnDraw
            | Self::FeatureOpRune
            | Self::Literal(_) => unreachable!(),
            Self::OperatorAdd(l, r)
            | Self::OperatorMax(l, r)
            | Self::OperatorMin(l, r)
            | Self::OperatorMul(l, r)
            | Self::OperatorSub(l, r) => {
                if index - 1 < l.size() {
                    &mut l[index - 1]
                } else {
                    &mut r[index - 1 - l.size()]
                }
            }
        }
    }
}

#[derive(Clone, Debug, Default)]
pub struct BinaryTreeIndividual {
    pub card_node: CardNode,
    pub state_node: StateNode,
}

impl AgentGreedy for BinaryTreeIndividual {
    fn evaluate_card(&self, card: &Card) -> f32 {
        self.card_node.evaluate(card)
    }

    fn evaluate_state(&self, state: &State) -> f32 {
        let mut score = self.state_node.evaluate(state);

        for boards in &state.me.boards {
            for card in boards {
                score += self.evaluate_card(card);
            }
        }

        for boards in &state.op.boards {
            for card in boards {
                score -= self.evaluate_card(card);
            }
        }

        score
    }
}

impl Individual for BinaryTreeIndividual {
    fn crossover(parents: [&Self; 2], children: [&mut Self; 2], rng: &mut impl Rng) {
        let index0 = rng.gen_range(0..parents[0].card_node.size());
        let index1 = rng.gen_range(0..parents[1].card_node.size());
        children[0].card_node.clone_from(&parents[0].card_node);
        children[1].card_node.clone_from(&parents[1].card_node);
        children[0].card_node[index0].clone_from(&parents[1].card_node[index1]);
        children[1].card_node[index1].clone_from(&parents[0].card_node[index0]);

        let index2 = rng.gen_range(0..parents[0].state_node.size());
        let index3 = rng.gen_range(0..parents[1].state_node.size());
        children[0].state_node.clone_from(&parents[0].state_node);
        children[1].state_node.clone_from(&parents[1].state_node);
        children[0].state_node[index2].clone_from(&parents[1].state_node[index3]);
        children[1].state_node[index3].clone_from(&parents[0].state_node[index2]);
    }

    fn mutate(&mut self, rng: &mut impl Rng) {
        if MUTATION.sample(rng) {
            let index = rng.gen_range(0..self.card_node.size());
            self.card_node[index] = rng.gen();
        }

        if MUTATION.sample(rng) {
            let index = rng.gen_range(0..self.state_node.size());
            self.state_node[index] = rng.gen();
        }
    }

    fn randomize(&mut self, rng: &mut impl Rng) {
        self.card_node = rng.gen();
        self.state_node = rng.gen();
    }
}

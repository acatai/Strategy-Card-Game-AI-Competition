use crate::agents::AgentGreedy;
use crate::engine::{Card, Keyword, State};
use crate::evolution::constants::MUTATION;
use crate::evolution::individuals::Individual;
use lazy_static::lazy_static;
use rand::distributions::{Distribution, Standard, Uniform, WeightedIndex};
use rand::Rng;
use std::cmp::Ordering;
use std::ops::{Index, IndexMut};

const OPERATOR_MAX: usize = 5;
const OPERATOR_MIN: usize = 2;

lazy_static! {
    static ref LITERAL: Uniform<f32> = Uniform::new(-1.0, 1.0);
    static ref OPERATOR: WeightedIndex<f32> =
        WeightedIndex::new((1..=OPERATOR_MAX - OPERATOR_MIN).map(|n| 1.0 / n as f32)).unwrap();
}

macro_rules! gen_operator_vec {
    ($rng:expr) => {
        (0..OPERATOR_MIN + OPERATOR.sample($rng))
            .map(|_| $rng.gen())
            .collect()
    };
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
    OperatorAdd(Vec<Self>),
    OperatorMax(Vec<Self>),
    OperatorMin(Vec<Self>),
    OperatorMul(Vec<Self>),
    OperatorNeg(Box<Self>),
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
            Self::OperatorAdd(xs) => xs.iter().map(|x| x.evaluate(card)).sum(),
            Self::OperatorMax(xs) => xs
                .iter()
                .map(|x| x.evaluate(card))
                .max_by(|x, y| x.partial_cmp(y).unwrap_or(Ordering::Equal))
                .unwrap(),
            Self::OperatorMin(xs) => xs
                .iter()
                .map(|x| x.evaluate(card))
                .min_by(|x, y| x.partial_cmp(y).unwrap_or(Ordering::Equal))
                .unwrap(),
            Self::OperatorMul(xs) => xs.iter().map(|x| x.evaluate(card)).product(),
            Self::OperatorNeg(x) => -x.evaluate(card),
        }
    }

    fn size(&self) -> usize {
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
            Self::OperatorAdd(xs)
            | Self::OperatorMax(xs)
            | Self::OperatorMin(xs)
            | Self::OperatorMul(xs) => 1 + xs.iter().map(Self::size).sum::<usize>(),
            Self::OperatorNeg(x) => 1 + x.size(),
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
            9 => CardNode::OperatorAdd(gen_operator_vec!(rng)),
            10 => CardNode::OperatorMax(gen_operator_vec!(rng)),
            11 => CardNode::OperatorMin(gen_operator_vec!(rng)),
            12 => CardNode::OperatorMul(gen_operator_vec!(rng)),
            13 => CardNode::OperatorNeg(Box::new(rng.gen())),
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
            Self::OperatorAdd(xs)
            | Self::OperatorMax(xs)
            | Self::OperatorMin(xs)
            | Self::OperatorMul(xs) => {
                let mut index = index - 1;
                for x in xs {
                    let size = x.size();
                    if index < size {
                        return &x[index];
                    }
                    index -= size;
                }
                unreachable!()
            }
            Self::OperatorNeg(x) => &x[index - 1],
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
            Self::OperatorAdd(xs)
            | Self::OperatorMax(xs)
            | Self::OperatorMin(xs)
            | Self::OperatorMul(xs) => {
                let mut index = index - 1;
                for x in xs {
                    let size = x.size();
                    if index < size {
                        return &mut x[index];
                    }
                    index -= size;
                }
                unreachable!()
            }
            Self::OperatorNeg(x) => &mut x[index - 1],
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
    OperatorAdd(Vec<Self>),
    OperatorMax(Vec<Self>),
    OperatorMin(Vec<Self>),
    OperatorMul(Vec<Self>),
    OperatorNeg(Box<Self>),
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
            Self::OperatorAdd(xs) => xs.iter().map(|x| x.evaluate(state)).sum(),
            Self::OperatorMax(xs) => xs
                .iter()
                .map(|x| x.evaluate(state))
                .max_by(|x, y| x.partial_cmp(y).unwrap_or(Ordering::Equal))
                .unwrap(),
            Self::OperatorMin(xs) => xs
                .iter()
                .map(|x| x.evaluate(state))
                .min_by(|x, y| x.partial_cmp(y).unwrap_or(Ordering::Equal))
                .unwrap(),
            Self::OperatorMul(xs) => xs.iter().map(|x| x.evaluate(state)).product(),
            Self::OperatorNeg(x) => -x.evaluate(state),
        }
    }

    fn size(&self) -> usize {
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
            Self::OperatorAdd(xs)
            | Self::OperatorMax(xs)
            | Self::OperatorMin(xs)
            | Self::OperatorMul(xs) => 1 + xs.iter().map(Self::size).sum::<usize>(),
            Self::OperatorNeg(x) => 1 + x.size(),
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
            13 => StateNode::OperatorAdd(gen_operator_vec!(rng)),
            14 => StateNode::OperatorMax(gen_operator_vec!(rng)),
            15 => StateNode::OperatorMin(gen_operator_vec!(rng)),
            16 => StateNode::OperatorMul(gen_operator_vec!(rng)),
            17 => StateNode::OperatorNeg(Box::new(rng.gen())),
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
            Self::OperatorAdd(xs)
            | Self::OperatorMax(xs)
            | Self::OperatorMin(xs)
            | Self::OperatorMul(xs) => {
                let mut index = index - 1;
                for x in xs {
                    let size = x.size();
                    if index < size {
                        return &x[index];
                    }
                    index -= size;
                }
                unreachable!()
            }
            Self::OperatorNeg(x) => &x[index - 1],
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
            Self::OperatorAdd(xs)
            | Self::OperatorMax(xs)
            | Self::OperatorMin(xs)
            | Self::OperatorMul(xs) => {
                let mut index = index - 1;
                for x in xs {
                    let size = x.size();
                    if index < size {
                        return &mut x[index];
                    }
                    index -= size;
                }
                unreachable!()
            }
            Self::OperatorNeg(x) => &mut x[index - 1],
        }
    }
}

#[derive(Clone, Debug, Default)]
pub struct TreeIndividual {
    pub card_node: CardNode,
    pub state_node: StateNode,
}

impl TreeIndividual {
    pub fn from_weights(weights: &[f32; 20]) -> Self {
        macro_rules! card_feature {
            ($feature:ident, $index:expr) => {
                CardNode::OperatorMul(vec![CardNode::$feature, CardNode::Literal(weights[$index])])
            };
        }

        macro_rules! state_feature {
            ($feature:ident, $index:expr) => {
                StateNode::OperatorMul(vec![
                    StateNode::$feature,
                    StateNode::Literal(weights[$index]),
                ])
            };
        }

        Self {
            card_node: CardNode::OperatorAdd(vec![
                card_feature!(FeatureAttack, 12),
                card_feature!(FeatureDefense, 13),
                card_feature!(FeatureHasBreakthrough, 14),
                card_feature!(FeatureHasCharge, 15),
                card_feature!(FeatureHasDrain, 16),
                card_feature!(FeatureHasGuard, 17),
                card_feature!(FeatureHasLethal, 18),
                card_feature!(FeatureHasWard, 19),
            ]),
            state_node: StateNode::OperatorAdd(vec![
                state_feature!(FeatureMeCurrentMana, 0),
                state_feature!(FeatureMeDecksize, 1),
                state_feature!(FeatureMeHealth, 2),
                state_feature!(FeatureMeMaxMana, 3),
                state_feature!(FeatureMeNextTurnDraw, 4),
                state_feature!(FeatureMeRune, 5),
                state_feature!(FeatureOpCurrentMana, 6),
                state_feature!(FeatureOpDecksize, 7),
                state_feature!(FeatureOpHealth, 8),
                state_feature!(FeatureOpMaxMana, 9),
                state_feature!(FeatureOpNextTurnDraw, 10),
                state_feature!(FeatureOpRune, 11),
            ]),
        }
    }
}

impl AgentGreedy for TreeIndividual {
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

impl Individual for TreeIndividual {
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

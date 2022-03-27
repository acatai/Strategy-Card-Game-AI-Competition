use crate::agents::AgentGreedy;
use crate::engine::{Card, Keyword, State};
use crate::evolution::constants::MUTATION;
use crate::evolution::individuals::Individual;
use lazy_static::lazy_static;
use rand::distributions::{Distribution, Uniform};
use rand::Rng;

lazy_static! {
    static ref GENE: Uniform<f32> = Uniform::new(-1.0, 1.0);
}

#[derive(Clone, Debug, Default)]
pub struct LinearIndividual {
    pub weights: [f32; 20],
}

fn dot(xs: &[f32], ys: &[f32]) -> f32 {
    debug_assert_eq!(xs.len(), ys.len());
    xs.iter().zip(ys).map(|(x, y)| x * y).sum()
}

impl AgentGreedy for LinearIndividual {
    fn evaluate_card(&self, card: &Card) -> f32 {
        use Keyword::{Breakthrough, Charge, Drain, Guard, Lethal, Ward};

        dot(
            &self.weights[12..20],
            &[
                f32::from(card.attack),
                f32::from(card.defense),
                if card.has(Breakthrough) { 1.0 } else { 0.0 },
                if card.has(Charge) { 1.0 } else { 0.0 },
                if card.has(Drain) { 1.0 } else { 0.0 },
                if card.has(Guard) { 1.0 } else { 0.0 },
                if card.has(Lethal) { 1.0 } else { 0.0 },
                if card.has(Ward) { 1.0 } else { 0.0 },
            ],
        )
    }

    fn evaluate_state(&self, state: &State) -> f32 {
        let mut score = dot(
            &self.weights[0..12],
            &[
                f32::from(state.me.current_mana),
                f32::from(state.me.decksize),
                f32::from(state.me.health),
                f32::from(state.me.max_mana),
                f32::from(state.me.next_turn_draw),
                f32::from(state.me.rune),
                f32::from(state.op.current_mana),
                f32::from(state.op.decksize),
                f32::from(state.op.health),
                f32::from(state.op.max_mana),
                f32::from(state.op.next_turn_draw),
                f32::from(state.op.rune),
            ],
        );

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

impl Individual for LinearIndividual {
    fn crossover(parents: [&Self; 2], children: [&mut Self; 2], rng: &mut impl Rng) {
        for gene in 0..20 {
            let parent_a = if rng.gen() { 0 } else { 1 };
            let parent_b = 1 - parent_a;
            children[0].weights[gene] = parents[parent_a].weights[gene];
            children[1].weights[gene] = parents[parent_b].weights[gene];
        }
    }

    fn mutate(&mut self, rng: &mut impl Rng) {
        for weight in &mut self.weights {
            if MUTATION.sample(rng) {
                *weight = GENE.sample(rng);
            }
        }
    }

    fn randomize(&mut self, rng: &mut impl Rng) {
        for weight in &mut self.weights {
            *weight = GENE.sample(rng);
        }
    }
}

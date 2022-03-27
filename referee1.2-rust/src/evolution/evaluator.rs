use crate::agents::Agent;
use crate::engine::constants::CARDS;
use crate::evolution::constants::{EVALUATOR_DRAFTS, EVALUATOR_ROUNDS};
use crate::evolution::individuals::Individual;
use crate::referee::{play, Draft};
use rand::Rng;
use std::iter::repeat;

#[derive(Default)]
pub struct Evaluator<I: Agent + Individual> {
    agents: Vec<I>,
}

impl<I: Agent + Individual> Evaluator<I> {
    pub fn add(&mut self, agent: I) {
        self.agents.push(agent);
    }

    pub fn score(&self, rng: &mut impl Rng) {
        let plays_round = EVALUATOR_DRAFTS * EVALUATOR_ROUNDS;
        let plays_total = plays_round * (self.agents.len() - 1);
        let drafts = Draft::new_n(&CARDS, EVALUATOR_DRAFTS, rng);
        for (index_a, agent_a) in self.agents.iter().enumerate() {
            let mut wins_total = 0;
            for (index_b, agent_b) in self.agents.iter().enumerate() {
                if index_a == index_b {
                    print!("------ ");
                    continue;
                }

                let wins_round = repeat(drafts.iter())
                    .take(EVALUATOR_ROUNDS)
                    .flatten()
                    .filter(|draft| play(agent_a, agent_b, draft, rng, false))
                    .count();

                print!("{:5.2}% ", 100.0 * wins_round as f32 / plays_round as f32);
                wins_total += wins_round;
            }
            println!("{:5.2}%", 100.0 * wins_total as f32 / plays_total as f32);
        }
    }
}

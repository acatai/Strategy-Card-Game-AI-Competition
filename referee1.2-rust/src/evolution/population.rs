use crate::agents::Agent;
use crate::engine::constants::CARDS;
use crate::evolution::constants::{ELITISM, EVOLUTION_DRAFTS, EVOLUTION_ROUNDS, POPULATION};
use crate::evolution::individuals::Individual;
use crate::referee::{play, Draft};
use arrayvec::ArrayVec;
use rand::distributions::WeightedIndex;
use rand::rngs::SmallRng;
use rand::{Rng, SeedableRng};
use rayon::prelude::*;
use std::iter::repeat;
use std::ops::{Index, IndexMut};
use std::sync::mpsc::channel;

#[derive(Clone)]
pub struct Population<I: Agent + Individual> {
    // `ArrayVec` wrapper to let `I` not be `Copy`.
    pub agents: ArrayVec<[I; POPULATION]>,
    pub scores: [usize; POPULATION],
}

impl<I: Agent + Individual> Population<I> {
    pub fn evolve(&mut self, rng: &mut impl Rng) {
        let agents = self.agents.clone();
        let sampler = &WeightedIndex::new(&self.scores).unwrap();
        for index in 0..POPULATION / 2 {
            let (xs, ys) = self.agents.split_at_mut(1 + 2 * index);
            I::crossover(
                [&agents[rng.sample(sampler)], &agents[rng.sample(sampler)]],
                [xs.last_mut().unwrap(), ys.first_mut().unwrap()],
                rng,
            );
        }

        self.agents.iter_mut().for_each(|agent| agent.mutate(rng));
        self.scores.iter_mut().for_each(|score| *score = 0);

        for index in 0..ELITISM {
            self[index].clone_from(&agents[index]);
        }
    }

    pub fn randomize(&mut self, rng: &mut impl Rng) {
        for agent in &mut self.agents {
            agent.randomize(rng);
        }
    }

    pub fn score(&mut self, rng: &mut impl Rng) {
        let seed = rng.gen();
        let drafts = Draft::new_n(&CARDS, EVOLUTION_DRAFTS, rng);
        let (sender, receiver) = channel();
        (0..POPULATION * POPULATION)
            .into_par_iter()
            .filter_map(|index| match (index % POPULATION, index / POPULATION) {
                (a, b) if a != b => Some((a, b)),
                _ => None,
            })
            .map(|(a, b)| {
                let mut rng = SmallRng::seed_from_u64(seed);
                let (agent_a, agent_b) = (&self[a], &self[b]);
                repeat(drafts.iter())
                    .take(EVOLUTION_ROUNDS)
                    .flatten()
                    .map(move |draft| {
                        if play(agent_a, agent_b, draft, &mut rng, false) {
                            a
                        } else {
                            b
                        }
                    })
                    .par_bridge()
            })
            .flatten()
            .for_each_with(sender, |sender, winner| sender.send(winner).unwrap());

        for winner in receiver {
            self.scores[winner] += 1;
        }

        for index in 0..POPULATION {
            let position = self
                .scores
                .iter()
                .enumerate()
                .skip(index)
                .max_by_key(|(_, score)| *score)
                .map(|(position, _)| position)
                .unwrap();
            self.agents.swap(index, position);
            self.scores.swap(index, position);
        }
    }

    pub fn score_against(&mut self, rng: &mut impl Rng, target: &(impl Agent + Sync)) {
        let seed = rng.gen();
        let drafts = Draft::new_n(&CARDS, EVOLUTION_DRAFTS, rng);
        let (sender, receiver) = channel();
        (0..2 * POPULATION)
            .into_par_iter()
            .map(|index| {
                let mut rng = SmallRng::seed_from_u64(seed);
                let (index, is_first) = (index / 2, index % 2 == 0);
                let agent = &self[index];
                repeat(drafts.iter())
                    .take(EVOLUTION_ROUNDS * POPULATION)
                    .flatten()
                    .filter_map(move |draft| {
                        let has_won = if is_first {
                            play(agent, target, draft, &mut rng, false)
                        } else {
                            !play(target, agent, draft, &mut rng, false)
                        };

                        if has_won {
                            Some(index)
                        } else {
                            None
                        }
                    })
                    .par_bridge()
            })
            .flatten()
            .for_each_with(sender, |sender, winner| sender.send(winner).unwrap());

        for winner in receiver {
            self.scores[winner] += 1;
        }

        for index in 0..POPULATION {
            let position = self
                .scores
                .iter()
                .enumerate()
                .skip(index)
                .max_by_key(|(_, score)| *score)
                .map(|(position, _)| position)
                .unwrap();
            self.agents.swap(index, position);
            self.scores.swap(index, position);
        }
    }
}

impl<I: Agent + Individual> Default for Population<I> {
    fn default() -> Self {
        let mut agents = ArrayVec::default();
        for _ in 0..POPULATION {
            agents.push(I::default());
        }

        Self {
            agents,
            scores: [1; POPULATION],
        }
    }
}

impl<I: Agent + Individual> Index<usize> for Population<I> {
    type Output = I;

    fn index(&self, index: usize) -> &Self::Output {
        &self.agents[index]
    }
}

impl<I: Agent + Individual> IndexMut<usize> for Population<I> {
    fn index_mut(&mut self, index: usize) -> &mut Self::Output {
        &mut self.agents[index]
    }
}

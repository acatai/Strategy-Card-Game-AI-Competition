use lazy_static::lazy_static;
use rand::distributions::Bernoulli;

pub const ELITISM: usize = 5;
pub const EVALUATOR_DRAFTS: usize = 10;
pub const EVALUATOR_ROUNDS: usize = 10;
pub const EVOLUTION_DRAFTS: usize = 10;
pub const EVOLUTION_ROUNDS: usize = 10;
pub const GENERATIONS: usize = 50;
pub const MUTATION_RATE: f64 = 0.05;
pub const POPULATION: usize = 50;

lazy_static! {
    pub static ref MUTATION: Bernoulli = Bernoulli::new(MUTATION_RATE).unwrap();
}

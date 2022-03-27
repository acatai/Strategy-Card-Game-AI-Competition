mod baseline2;
mod greedy;
mod noop;
mod random;

pub use crate::agents::baseline2::AgentBaseline2;
pub use crate::agents::greedy::AgentGreedy;
pub use crate::agents::noop::AgentNoop;
pub use crate::agents::random::AgentRandom;
use crate::engine::{Action, Actions, State};
use rand::Rng;
use std::fmt;

pub trait Agent {
    fn draw(&self, state: &State, rng: &mut impl Rng) -> DrawResult;
    fn play(&self, state: &State, rng: &mut impl Rng) -> PlayResult;
}

#[derive(Default)]
pub struct DrawResult {
    pub index: usize,
    pub score: f32,
}

impl fmt::Display for DrawResult {
    fn fmt(&self, fmt: &mut fmt::Formatter<'_>) -> fmt::Result {
        format!("PICK {} # score: {}", self.index, self.score).fmt(fmt)
    }
}

#[derive(Default)]
pub struct PlayResult {
    pub actions: Actions,
    pub score: f32,
}

impl fmt::Display for PlayResult {
    fn fmt(&self, fmt: &mut fmt::Formatter<'_>) -> fmt::Result {
        debug_assert!(self.actions.last() == Some(&Action::Pass));
        format!(
            "{} # score: {}",
            self.actions
                .iter()
                .map(Action::to_string)
                .collect::<Vec<String>>()
                .join(";"),
            self.score
        )
        .fmt(fmt)
    }
}

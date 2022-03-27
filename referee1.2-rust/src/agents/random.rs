use crate::agents::{Agent, DrawResult, PlayResult};
use crate::engine::State;
use rand::seq::SliceRandom;
use rand::Rng;

#[derive(Debug)]
pub struct AgentRandom;

impl Agent for AgentRandom {
    fn draw(&self, state: &State, rng: &mut impl Rng) -> DrawResult {
        let mut result = DrawResult::default();
        result.index = rng.gen_range(0..state.me.hand.len());
        result
    }

    fn play(&self, state: &State, rng: &mut impl Rng) -> PlayResult {
        let mut result = PlayResult::default();
        let mut state = (*state).clone();

        while let Some(action) = state.compute_actions().choose(rng).copied() {
            result.actions.push(action);
            state.apply_action(action);
        }

        result
    }
}

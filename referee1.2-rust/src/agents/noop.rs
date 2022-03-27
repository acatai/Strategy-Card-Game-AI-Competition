use crate::agents::{Agent, DrawResult, PlayResult};
use crate::engine::{Action, State};
use rand::Rng;

#[derive(Debug)]
pub struct AgentNoop;

impl Agent for AgentNoop {
    fn draw(&self, _state: &State, _rng: &mut impl Rng) -> DrawResult {
        DrawResult::default()
    }

    fn play(&self, _state: &State, _rng: &mut impl Rng) -> PlayResult {
        let mut result = PlayResult::default();
        result.actions.push(Action::Pass);
        result
    }
}

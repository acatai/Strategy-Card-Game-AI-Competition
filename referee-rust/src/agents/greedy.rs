use crate::agents::{Agent, DrawResult, PlayResult};
use crate::engine::{Card, State};
use rand::Rng;
use std::cmp::Ordering;

pub trait AgentGreedy {
    fn evaluate_card(&self, card: &Card) -> f32;
    fn evaluate_state(&self, state: &State) -> f32;
}

impl<H: AgentGreedy> Agent for H {
    fn draw(&self, state: &State, _rng: &mut impl Rng) -> DrawResult {
        let (index, score) = state
            .me
            .hand
            .iter()
            .map(|card| self.evaluate_card(card))
            .enumerate()
            .max_by(|x, y| x.1.partial_cmp(&y.1).unwrap_or(Ordering::Equal))
            .unwrap();

        DrawResult { index, score }
    }

    fn play(&self, state: &State, _rng: &mut impl Rng) -> PlayResult {
        let mut result = PlayResult::default();
        let mut state = (*state).clone();

        let mut scratch = State::default();
        while let Some((best_action, best_score)) = state
            .compute_actions()
            .into_iter()
            .map(|action| {
                scratch.clone_from(&state);
                scratch.apply_action(action);
                (action, self.evaluate_state(&scratch))
            })
            .max_by(|x, y| x.1.partial_cmp(&y.1).unwrap_or(Ordering::Equal))
        {
            result.actions.push(best_action);
            result.score = best_score;
            state.apply_action(best_action);
        }

        result
    }
}

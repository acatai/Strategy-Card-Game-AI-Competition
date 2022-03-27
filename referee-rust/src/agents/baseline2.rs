use crate::agents::{Agent, DrawResult, PlayResult};
use crate::engine::constants::LANES;
use crate::engine::{Action, State, Type};
use rand::Rng;
use std::convert::TryFrom;

#[derive(Debug)]
pub struct AgentBaseline2;

impl Agent for AgentBaseline2 {
    fn draw(&self, state: &State, _rng: &mut impl Rng) -> DrawResult {
        let mut result = DrawResult::default();
        for (index, card) in state.me.hand.iter().enumerate() {
            if card.card_type == Type::Creature && card.attack > state.me.hand[result.index].attack
            {
                result.index = index;
            }
        }
        result
    }

    fn play(&self, state: &State, _rng: &mut impl Rng) -> PlayResult {
        let mut actions = vec![];

        let mut my_board: Vec<_> = state.me.boards.iter().flatten().collect();
        let mut op_guards: Vec<_> = state.op.boards.iter().flatten().collect();
        my_board.sort_unstable_by_key(|card| -card.attack);
        op_guards.sort_unstable_by_key(|card| -card.defense);
        for card in &my_board {
            actions.push(Action::AttackFace {
                id: card.instance_id,
            });

            for guard in &op_guards {
                actions.push(Action::AttackCard {
                    id1: card.instance_id,
                    id2: guard.instance_id,
                });
            }
        }

        let mut my_hand: Vec<_> = state.me.hand.iter().collect();
        my_hand.sort_unstable_by_key(|card| -card.attack);
        for card in &my_hand {
            for lane in 0..LANES {
                actions.push(Action::Summon {
                    id: card.instance_id,
                    lane: u8::try_from(lane).unwrap(),
                });
            }
        }

        let mut result = PlayResult::default();
        let mut state = (*state).clone();
        for action in actions {
            if state.compute_actions().contains(&action) {
                result.actions.push(action);
                state.apply_action(action);
            }
        }

        result
    }
}

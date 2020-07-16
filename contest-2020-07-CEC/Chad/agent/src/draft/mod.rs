use crate::model::{Action, Card, Opponent, Player};

use failure::*;
use std::time::Duration;

pub mod hs_weights;
pub use hs_weights::HSWeightsPicker;

pub trait CardPicker {
    fn pick(&mut self, player: &Player, opponent: &Opponent, time_left: Duration)
        -> (Card, Action);
}

#[derive(Debug, Fail)]
pub enum DraftError {
    #[fail(display = "Could not parse input")]
    ParseError,
}

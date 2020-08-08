pub mod predict_mcts;
pub mod utils;

use crate::model::{ActionChain, Opponent, Player};
use crate::predictors::Predictor;

use failure::*;
use std::time::Duration;

pub use predict_mcts::PredictMCTSActioner;

pub trait BattleActioner {
    fn actions<P: Predictor>(
        &mut self,
        player: &mut Player,
        opponent: &mut Opponent,
        predictor: &P,
        time_left: Duration,
    ) -> ActionChain;
}

#[derive(Debug, Fail)]
pub enum BattleError {
    #[fail(display = "Could not parse input")]
    ParseError,
}

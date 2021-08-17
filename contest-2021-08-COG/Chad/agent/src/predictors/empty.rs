use crate::model::{Card, Opponent, Player};

#[derive(Default)]
pub struct EmptyPredictor;

impl super::Predictor for EmptyPredictor {
    fn refresh(&mut self, _player: &Player, _opponent: &Opponent) {}

    fn predict(&self, _opponent: &Opponent) -> Option<Vec<Card>> {
        None
    }
}

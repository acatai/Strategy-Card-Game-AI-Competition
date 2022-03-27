use crate::model::{Card, Opponent, Player};

mod empty;
pub use empty::EmptyPredictor;

pub trait Predictor {
    fn refresh(&mut self, player: &Player, opponent: &Opponent);
    fn predict(&self, opponent: &Opponent) -> Option<Vec<Card>>;
}

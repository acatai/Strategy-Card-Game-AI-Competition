pub mod rave_mcts;

pub trait GameState: Sized {
    type Action;

    fn eval(&self) -> f32;
    fn children(&self) -> Vec<(Self::Action, Self)>;
}

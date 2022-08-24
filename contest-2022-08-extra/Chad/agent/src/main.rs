#![feature(impl_trait_in_bindings)]
#![feature(box_syntax)]

use crate::parser::parse;
use battle::{BattleActioner, BattleError, PredictMCTSActioner};
use draft::{CardPicker, DraftError, HSWeightsPicker};
use model::{Opponent, Player, DECK_SIZE};
use predictors::{EmptyPredictor, Predictor};

use std::time::{Duration, Instant};

use failure::*;

mod algorithms;
mod battle;
mod draft;
mod model;
mod parser;
mod predictors;

fn draft<T: CardPicker + Default>(
    player: &mut Player,
    opponent: &mut Opponent,
    first_delay: Duration,
    turn_delay: Duration,
) -> Result<(), DraftError> {
    let stdin = std::io::stdin();
    let mut delay = first_delay;
    let mut picker = T::default();
    let mut iid = 2000;
    for _i in 0..DECK_SIZE {
        let (player_status, opponent_status, cards) =
            parse(stdin.lock()).ok_or(DraftError::ParseError)?;
        let now = Instant::now();

        opponent.update_draft(&cards.player_hand);
        player.update_draft(cards, &player_status, &opponent_status.0);

        delay -= now.elapsed();
        let (mut card, action) = picker.pick(&player, &opponent, delay);
        card.instance_id = iid;
        iid += 1;
        player.update_pick(card);

        println!("{}", action);
        delay = turn_delay;
    }
    Ok(())
}

fn battle<B: BattleActioner + Default, P: Predictor + Default>(
    mut player: &mut Player,
    mut opponent: &mut Opponent,
    first_delay: Duration,
    turn_delay: Duration,
) -> Result<(), BattleError> {
    let stdin = std::io::stdin();
    let mut actioner = B::default();
    let mut predictor = P::default();
    let mut delay = first_delay;

    for round in 0.. {
        let (player_status, opponent_status, cards) =
            parse(stdin.lock()).ok_or(BattleError::ParseError)?;
        let now = Instant::now();

        player.update_battle(player_status, cards.player_hand, &cards.player_board, round);
        opponent.update_battle(opponent_status, &cards.opponent_board, round);
        predictor.refresh(&player, &opponent);

        delay = delay.checked_sub(now.elapsed()).unwrap_or_default();
        let actions = actioner.actions(&mut player, &mut opponent, &predictor, delay);

        println!("{}", actions);
        delay = turn_delay;
    }
    Ok(())
}

fn main() -> Result<(), Error> {
    let mut player = Player::new();
    let mut opponent = Opponent::new();

    draft::<HSWeightsPicker>(
        &mut player,
        &mut opponent,
        Duration::from_millis(1000),
        Duration::from_millis(100),
    )?;
    battle::<PredictMCTSActioner, EmptyPredictor>(
        &mut player,
        &mut opponent,
        Duration::from_millis(1000),
        Duration::from_millis(200),
    )?;

    Ok(())
}

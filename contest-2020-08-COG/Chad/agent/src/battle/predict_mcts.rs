#![allow(clippy::unreadable_literal, clippy::excessive_precision)]

use std::time::{Duration, Instant};

use rand::prelude::*;

use super::utils;
use super::BattleActioner;
use crate::algorithms::rave_mcts::*;
use crate::algorithms::GameState;
use crate::model::{Abilities, Action, ActionChain, Card, Opponent, Player, HAND_SIZE, LANES_NUM};
use crate::predictors::Predictor;

pub struct State<'p, P: Predictor> {
    player: Player,
    opponent: Opponent,
    passed: bool,
    predictor: &'p P,
}

impl<'p, P: Predictor> std::clone::Clone for State<'p, P> {
    fn clone(&self) -> Self {
        Self {
            player: self.player.clone(),
            opponent: self.opponent.clone(),
            passed: self.passed,
            predictor: self.predictor,
        }
    }
}

impl<'p, P: Predictor> State<'p, P> {
    fn with_action(&self, action: &Action) -> Option<Self> {
        let mut new_state = self.clone();

        let (player, opponent) = (&mut new_state.player.base, &mut new_state.opponent.base);
        if Action::do_action(action, player, opponent).is_ok() {
            if *action == Action::Pass {
                new_state.passed = true;
            }
            Some(new_state)
        } else {
            None
        }
    }

    fn card_heuristic(&self, card: &Card) -> f32 {
        const WEIGHTS: [[f32; 7]; 2] = [
            [
                7.4502552133355415,
                2.4573553163248296,
                0.5399126139507171,
                2.2130523012708805,
                0.02291714400593503,
                1.31549606133466,
                7.608806279636039,
            ],
            [
                8.747196234553206,
                4.03893115850313,
                0.5399126139507171,
                3.5457001041619027,
                0.01786346713859803,
                7.48781598401788,
                8.870647129927152,
            ],
        ];
        let mut score = 0.0;
        let order = self.player.base.player_order as usize - 1;

        score += WEIGHTS[order][0] * card.attack as f32;
        score += card.defense as f32;

        if card.abilities.contains(Abilities::Breakthrough) {
            score += WEIGHTS[order][1] * card.attack as f32;
        }

        if card.abilities.contains(Abilities::Charge) {
            score += WEIGHTS[order][2] * card.attack as f32;
        }

        if card.abilities.contains(Abilities::Guard) {
            score += WEIGHTS[order][3] * card.defense as f32;
        }

        if card.abilities.contains(Abilities::Lethal) && card.attack > 0 {
            score += 100. * WEIGHTS[order][4];
        }

        if card.abilities.contains(Abilities::Ward) {
            score += WEIGHTS[order][5] * card.attack as f32;
        }

        if card.abilities.contains(Abilities::Drain) {
            score += WEIGHTS[order][6] * card.attack as f32;
        }

        score / (WEIGHTS[order].iter().sum::<f32>() * 0.8 * 12.0)
    }

    fn heuristic(&self) -> f32 {
        let mut score = 0.0;
        let run_new_heu = true;
        let order = self.player.base.player_order as usize - 1;
        const NHEU: [[f32; 7]; 2] = [[1.3, 12.45, 8.5, 1.0, 1.0, 0.8, 1.3], [
            1.3, 14.45, 9.5, 1.0, 1.0, 0.8, 1.3,
        ]];
        let (player, opponent) = (&self.player.base, &self.opponent.base);

        if self.passed {
            score -= 250.0;
        }

        if opponent.health <= 0 {
            score += 55000.0;
        } else if player.health <= 0 {
            score -= 55000.0;
        } else {
            score += NHEU[order][1] * (30 - opponent.health).pow(2) as f32;
            score -= NHEU[order][2] * (30 - player.health).pow(2) as f32;
        }

        score /= 5500.;

        const PLAYER_CARD_MULT: f32 = 1.6;
        const OPPONENT_CARD_MULT: f32 = -1.8;

        for i in 0..LANES_NUM {
            score += player.lanes[i]
                .iter()
                .zip(std::iter::repeat(PLAYER_CARD_MULT))
                .map(|(card, coeff)| {
                    let mut res = coeff * self.card_heuristic(card);
                    if run_new_heu {
                        if card.abilities.contains(Abilities::Guard)
                            && opponent.lanes[i].is_empty()
                            && opponent.lanes.iter().map(|c| c.len()).sum::<usize>() != 0
                        {
                            res *= NHEU[order][0];
                        }

                        if card.defense > 5
                            && opponent.lanes[i]
                                .iter()
                                .any(|c| c.abilities.contains(Abilities::Lethal))
                        {
                            res *= NHEU[order][5];
                        }
                        if card.abilities.contains(Abilities::Lethal)
                            && opponent.lanes[i]
                                .iter()
                                .any(|c| c.abilities.contains(Abilities::Guard))
                        {
                            res *= NHEU[order][6];
                        }
                    }
                    res
                })
                .sum::<f32>();
            score += opponent.lanes[i]
                .iter()
                .zip(std::iter::repeat(OPPONENT_CARD_MULT))
                .map(|(card, coeff)| coeff * self.card_heuristic(card))
                .sum::<f32>();
        }
        if opponent.lanes.iter().map(|c| c.len()).sum::<usize>() == 0 {
            score *= NHEU[order][3];
        }
        if player.lanes.iter().map(|c| c.len()).sum::<usize>() > 0 {
            score *= NHEU[order][4];
        }
        score
    }
}

impl<'p, P: Predictor> State<'p, P> {
    const ALPHA_BLEND: f32 = 0.75;

    fn eval_single(&self, mut deck: Option<Vec<Card>>) -> f32 {
        let mut rng = rand::thread_rng();

        let mut new_state = self.clone();
        if let Some(mut prediction) = deck.take() {
            prediction.shuffle(&mut rng);
            new_state.opponent.base.hand = prediction
                .into_iter()
                .take((new_state.opponent.hand + 1).min(HAND_SIZE))
                .collect();
        }

        let mut enemy_score = new_state.heuristic();
        let mut actions = Action::valid_actions(&new_state.opponent.base, &new_state.player.base);

        while actions.len() > 2 {
            let idx = rng.gen_range(0, actions.len() - 2);
            let _ = Action::do_action(
                &actions[idx],
                &mut new_state.opponent.base,
                &mut new_state.player.base,
            );

            enemy_score = enemy_score.min(new_state.heuristic());
            actions = Action::valid_actions(&new_state.opponent.base, &new_state.player.base);
        }
        let _ = Action::do_action(
            &actions[0],
            &mut new_state.opponent.base,
            &mut new_state.player.base,
        );
        enemy_score = enemy_score.min(new_state.heuristic());

        let mut player_score = new_state.heuristic();
        new_state.player.update_battle_manual();
        new_state.player.base.recharge_lanes();

        actions = Action::valid_actions(&new_state.player.base, &new_state.opponent.base);
        while actions.len() > 2 {
            let idx = rng.gen_range(0, actions.len() - 2);
            let _ = Action::do_action(
                &actions[idx],
                &mut new_state.player.base,
                &mut new_state.opponent.base,
            );

            player_score = player_score.max(new_state.heuristic());
            actions = Action::valid_actions(&new_state.player.base, &new_state.opponent.base);
        }

        let _ = Action::do_action(
            &actions[0],
            &mut new_state.player.base,
            &mut new_state.opponent.base,
        );
        player_score = player_score.max(new_state.heuristic());

        (1.0 - Self::ALPHA_BLEND) * player_score + Self::ALPHA_BLEND * enemy_score
    }
}

impl<'p, P: Predictor> GameState for State<'p, P> {
    type Action = Action;

    fn eval(&self) -> f32 {
        const ITERS: usize = 16;

        let mut score = self.heuristic();
        let deck = self.predictor.predict(&self.opponent);

        for _ in 0..ITERS {
            score = score.min(self.eval_single(deck.clone()));
        }

        score
    }

    fn children(&self) -> Vec<(Self::Action, Self)> {
        if self.passed {
            return vec![];
        }

        Action::valid_actions(&self.player.base, &self.opponent.base)
            .into_iter()
            .filter_map(|action| self.with_action(&action).map(|state| (action, state)))
            .collect()
    }
}

#[derive(Default)]
pub struct PredictMCTSActioner;

impl BattleActioner for PredictMCTSActioner {
    fn actions<P: Predictor>(
        &mut self,
        player: &mut Player,
        opponent: &mut Opponent,
        predictor: &P,
        time_left: Duration,
    ) -> ActionChain {
        const T: Duration = Duration::from_millis(15); // XXX(MarWit): This delay is way too much
        let start = Instant::now();

        let killchain = utils::killchain(player.base.clone(), opponent.base.clone());
        if let Ok(Some(chain)) = killchain {
            return chain;
        }
        if let Err(e) = killchain {
            eprintln!("{}", e);
        }

        let mut mcts = RaveMCTS::new(
            State {
                player: player.clone(),
                opponent: opponent.clone(),
                passed: false,
                predictor,
            },
            20.0,
            None,
        );

        while time_left > start.elapsed() + T {
            mcts.eval(mcts.root);
        }

        let mut best_chain = ActionChain(mcts.get_best_action_chain());
        let (new_player, new_opponent) = {
            let mut base_player = player.base.clone();
            let mut base_opponent = player.base.clone();

            for action in best_chain.iter() {
                Action::do_action(action, &mut base_player, &mut base_opponent).ok();
            }

            (base_player, base_opponent)
        };
        best_chain.extend(utils::all_attack_opponent(&new_player, &new_opponent));

        best_chain
    }
}

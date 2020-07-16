use crate::model::{Abilities, Action, ActionChain, BasePlayer};

use failure::Error;

pub fn all_attack_opponent(player: &BasePlayer, opponent: &BasePlayer) -> Vec<Action> {
    Action::valid_actions(player, opponent)
        .into_iter()
        .filter(|action| match action {
            Action::AttackOpponent { id } => match player.get_board(*id) {
                Some(card) if card.attack > 0 => true,
                _ => false,
            },
            _ => false,
        })
        .collect::<Vec<_>>()
}

pub fn killchain(
    mut player: BasePlayer,
    mut opponent: BasePlayer,
) -> Result<Option<ActionChain>, Error> {
    const DMG_SCALER: isize = 100;
    let mut chain = ActionChain(all_attack_opponent(&player, &opponent));

    for action in chain.iter() {
        Action::do_action(action, &mut player, &mut opponent)?;
        if opponent.health <= 0 {
            return Ok(Some(chain));
        }
    }

    while let Some(action) = Action::valid_actions(&player, &opponent)
        .into_iter()
        .min_by_key(|action| match action {
            Action::AttackOpponent { id } => match player.get_board(*id) {
                Some(card) if card.attack > 0 => (0, -card.attack),
                _ => (10, 0),
            },
            Action::UseOpponent { id } => match player.get_hand(*id) {
                Some(card) => (
                    1,
                    (-card.defense + card.enemy_hp) * DMG_SCALER / (card.cost + 1) as isize,
                ),
                _ => (10, 0),
            },
            Action::Attack { id1, id2 } => match opponent.get_board(*id2) {
                Some(target) if target.abilities.contains(Abilities::Guard) => {
                    if let Some(card) = player.get_board(*id1) {
                        (2, (card.attack * 2 - target.defense * 2 - 1).abs())
                    } else {
                        (10, 0)
                    }
                }
                _ => (10, 0),
            },
            Action::Pass => (9, 0),
            _ => (10, 0),
        })
    {
        if action == Action::Pass {
            break;
        }
        Action::do_action(&action, &mut player, &mut opponent)?;
        chain.push(action);
        if opponent.health <= 0 {
            return Ok(Some(chain));
        }
    }

    Ok(None)
}

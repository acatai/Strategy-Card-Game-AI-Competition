use crate::model::{
    AbilitiesMask, Action, Card, CardLocation, CardType, HAND_SIZE, LANES_NUM, MAX_CREATURES,
};

use std::convert::TryFrom;
use std::str::FromStr;

macro_rules! try_opt {
    ($val:expr) => {
        match $val {
            Some(value) => value,
            None => return None,
        }
    };
}

pub fn parse_next<'a, V: FromStr>(mut iter: impl Iterator<Item = &'a str>) -> Option<V> {
    iter.next().and_then(|c| c.parse::<V>().ok())
}

#[derive(Debug, PartialEq)]
pub struct PlayerStatus {
    pub health: isize,
    pub mana: usize,
    pub deck_size: usize,
    pub rune: u8,
    pub draw: usize,
}

#[derive(Debug, PartialEq)]
pub struct OpponentStatus {
    pub hand_size: usize,
    pub actions: Vec<(usize, Action)>,
}

#[derive(Debug, PartialEq)]
pub struct Cards {
    pub player_hand: Vec<Card>,
    pub player_board: Vec<(usize, Card)>,
    pub opponent_board: Vec<(usize, Card)>,
}

fn parse_player_status<I: AsRef<str>>(input: I) -> Option<PlayerStatus> {
    let mut splitted = input.as_ref().split_whitespace();

    Some(PlayerStatus {
        health: try_opt!(parse_next(splitted.by_ref())),
        mana: try_opt!(parse_next(splitted.by_ref())),
        deck_size: try_opt!(parse_next(splitted.by_ref())),
        rune: try_opt!(parse_next(splitted.by_ref())),
        draw: try_opt!(parse_next(splitted)),
    })
}

fn parse_action<I: AsRef<str>>(input: I) -> Option<(usize, Action)> {
    let mut splitted = input.as_ref().splitn(2, ' ');

    Some((
        try_opt!(parse_next(splitted.by_ref())),
        try_opt!(parse_next(splitted)),
    ))
}

fn parse_opponent_status_head<I: AsRef<str>>(input: I) -> Option<(usize, usize)> {
    let mut splitted = input.as_ref().split_whitespace();

    Some((
        try_opt!(parse_next(splitted.by_ref())),
        try_opt!(parse_next(splitted)),
    ))
}

fn parse_opponent_status(mut lines: impl Iterator<Item = String>) -> Option<OpponentStatus> {
    let (hand_size, actions_len) = try_opt!(parse_opponent_status_head(try_opt!(lines.next())));
    let mut actions = Vec::with_capacity(actions_len);
    for line in lines.take(actions_len) {
        actions.push(try_opt!(parse_action(line)));
    }

    Some(OpponentStatus { hand_size, actions })
}

fn parse_card<I: AsRef<str>>(input: I) -> Option<(Card, CardLocation, isize)> {
    use crate::model::AttackState::*;
    let mut splitted = input.as_ref().split_whitespace();

    let id = try_opt!(parse_next(splitted.by_ref()));
    let instance_id = try_opt!(parse_next(splitted.by_ref()));
    let location_i8: i8 = try_opt!(parse_next(splitted.by_ref()));
    let location = try_opt!(CardLocation::try_from(location_i8).ok());
    let card_type_u8: u8 = try_opt!(parse_next(splitted.by_ref()));
    let card_type = try_opt!(CardType::try_from(card_type_u8).ok());
    let cost = try_opt!(parse_next(splitted.by_ref()));
    let attack = try_opt!(parse_next(splitted.by_ref()));
    let defense = try_opt!(parse_next(splitted.by_ref()));
    let abilities: AbilitiesMask = try_opt!(parse_next(splitted.by_ref()));
    let player_hp = try_opt!(parse_next(splitted.by_ref()));
    let enemy_hp = try_opt!(parse_next(splitted.by_ref()));
    let card_draw = try_opt!(parse_next(splitted.by_ref()));
    let lane = try_opt!(parse_next(splitted.by_ref()));
    let attack_state = Ready;

    Some((
        Card {
            id,
            instance_id,
            card_type,
            cost,
            attack,
            defense,
            abilities,
            player_hp,
            enemy_hp,
            card_draw,
            attack_state,
        },
        location,
        lane,
    ))
}

fn parse_cards(mut lines: impl Iterator<Item = String>) -> Option<Cards> {
    use CardLocation::*;

    let cards_len = try_opt!(lines.next().and_then(|c| c.parse().ok()));

    let mut player_hand = Vec::with_capacity(HAND_SIZE);
    let mut player_board = Vec::with_capacity(LANES_NUM * MAX_CREATURES);
    let mut opponent_board = Vec::with_capacity(LANES_NUM * MAX_CREATURES);

    for line in lines.take(cards_len) {
        let (card, loc, lane) = try_opt!(parse_card(line));
        match loc {
            PlayerHand => player_hand.push(card),
            PlayerBoard if lane >= 0 => player_board.push((lane as usize, card)),
            OpponentBoard if lane >= 0 => opponent_board.push((lane as usize, card)),
            _ => return None,
        }
    }

    Some(Cards {
        player_hand,
        player_board,
        opponent_board,
    })
}

pub fn parse(
    input: impl std::io::BufRead,
) -> Option<(PlayerStatus, (PlayerStatus, OpponentStatus), Cards)> {
    let mut lines = input.lines().filter_map(|l| l.ok());

    Some((
        try_opt!(parse_player_status(try_opt!(lines.next()))),
        (
            try_opt!(parse_player_status(try_opt!(lines.next()))),
            try_opt!(parse_opponent_status(lines.by_ref())),
        ),
        try_opt!(parse_cards(lines)),
    ))
}

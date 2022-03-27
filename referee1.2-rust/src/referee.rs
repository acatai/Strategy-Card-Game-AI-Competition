use crate::agents::Agent;
use crate::engine::constants::{DRAFT_CARDS, DRAFT_LENGTH, INITIAL_DRAW};
use crate::engine::{Card, Deck, State};
use rand::distributions::{Distribution, Uniform};
use rand::seq::SliceRandom;
use rand::Rng;
use std::convert::TryInto;
use std::slice;

pub struct Draft<'cards>([[&'cards Card; DRAFT_CARDS]; DRAFT_LENGTH]);

impl<'cards> Draft<'cards> {
    pub fn iter(&self) -> slice::Iter<'_, [&'cards Card; DRAFT_CARDS]> {
        self.0.iter()
    }

    pub fn new(cards: &'cards [Card], rng: &mut impl Rng) -> Self {
        let mut draft = [[&cards[0]; DRAFT_CARDS]; DRAFT_LENGTH];
        let cards_len = Uniform::new(0, cards.len());
        for draft_turn in &mut draft {
            for draft_card in draft_turn.iter_mut() {
                *draft_card = &cards[cards_len.sample(rng)];
            }
        }

        Draft(draft)
    }

    pub fn new_n(cards: &'cards [Card], n: usize, rng: &mut impl Rng) -> Vec<Self> {
        (0..n).map(|_| Self::new(cards, rng)).collect()
    }
}

pub fn play(
    agent_a: &impl Agent,
    agent_b: &impl Agent,
    draft: &Draft<'_>,
    rng: &mut impl Rng,
    verbose: bool,
) -> bool {
    let mut state = State::default();
    let mut deck1 = Deck::default();
    let mut deck2 = Deck::default();

    for (turn, cards) in draft.iter().enumerate() {
        for &&card in cards.iter() {
            state.me.hand.push(card);
        }

        let pick1 = agent_a.draw(&state, rng);
        let pick2 = agent_b.draw(&state, rng);

        deck1.push(state.me.hand[pick1.index]);
        deck2.push(state.me.hand[pick2.index]);

        state.me.decksize += 1;
        state.op.decksize += 1;

        if verbose {
            println!("Draft {}", turn);
            println!("1? {}", state.me.hand[0]);
            println!("2? {}", state.me.hand[1]);
            println!("3? {}", state.me.hand[2]);
            println!("1! {}", pick1);
            println!("2! {}", pick2);
        }

        state.me.hand.clear();
    }

    deck1.shuffle(rng);
    deck2.shuffle(rng);

    for (id, card) in deck1.iter_mut().enumerate() {
        card.instance_id = ((DRAFT_LENGTH - id) * 2 - 1).try_into().unwrap();
    }

    for (id, card) in deck2.iter_mut().enumerate() {
        card.instance_id = ((DRAFT_LENGTH - id) * 2).try_into().unwrap();
    }

    if verbose {
        println!("Cards");
        for index in (1..=2 * DRAFT_LENGTH).rev() {
            let player = (index - 1) % 2;
            let deck = if player == 1 { &deck1 } else { &deck2 };
            let card = &deck[(index - 1) / 2];
            println!("{}? {}", 2 - player, card);
        }
    }

    for _ in 0..INITIAL_DRAW {
        state.me.draw(&mut deck1, 0);
        state.op.draw(&mut deck2, 0);
    }
    state.op.draw(&mut deck2, 0);

    'game: for turn in 1.. {
        state.recharge_creatures();

        if verbose {
            println!("Turn {:<12} # [{}] [{}]", turn, state.me, state.op);
        }

        state.recharge_mana(turn);
        state.me.draw(&mut deck1, turn);

        for action in agent_a.play(&state, rng).actions {
            state.apply_action(action);
            if verbose {
                println!("1! {:14} # [{}] [{}]", action, state.me, state.op);
            }
            if state.is_game_over() {
                break 'game;
            }
        }

        state.swap();
        state.recharge_mana(turn);
        state.me.draw(&mut deck2, turn);

        for action in agent_b.play(&state, rng).actions {
            state.apply_action(action);
            if verbose {
                println!("2! {:14} # [{}] [{}]", action, state.me, state.op);
            }
            if state.is_game_over() {
                state.swap();
                break 'game;
            }
        }

        state.swap();
    }

    if verbose {
        println!("End               # [{}] [{}]", state.me, state.op);
    }

    state.me.health > 0
}

pub fn run(
    agent: &impl Agent,
    lines: &mut impl Iterator<Item = String>,
    rng: &mut impl Rng,
) -> Result<(), ()> {
    for turn in 0.. {
        let state = State::from_lines(lines)?;
        if turn < DRAFT_LENGTH {
            println!("{}", agent.draw(&state, rng));
        } else {
            println!("{}", agent.play(&state, rng));
        }
    }

    Ok(())
}

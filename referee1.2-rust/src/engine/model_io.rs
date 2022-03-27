use crate::engine::{Action, AttackState, Card, Gamer, Keyword, Keywords, Location, State, Type};
use std::convert::TryFrom;
use std::fmt;
use std::str;

impl fmt::Display for Action {
    fn fmt(&self, fmt: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::AttackCard { id1, id2 } => format!("ATTACK {} {}", id1, id2),
            Self::AttackFace { id } => format!("ATTACK {} -1", id),
            Self::Pass => "PASS".to_string(),
            Self::Summon { id, lane } => format!("SUMMON {} {}", id, lane),
            Self::UseOnCard { id1, id2 } => format!("USE {} {}", id1, id2),
            Self::UseOnFace { id } => format!("USE {} -1", id),
        }
        .fmt(fmt)
    }
}

impl fmt::Display for Card {
    fn fmt(&self, fmt: &mut fmt::Formatter<'_>) -> fmt::Result {
        format!(
            "{:2} (#{:3}:{:9}) {:2}/{:2} [{:2}] {}",
            self.instance_id,
            self.card_number,
            self.card_type,
            self.attack,
            self.defense,
            self.cost,
            self.keywords,
        )
        .fmt(fmt)
    }
}

impl fmt::Display for Gamer {
    fn fmt(&self, fmt: &mut fmt::Formatter<'_>) -> fmt::Result {
        format!(
            "HP{:2}({:2}) MP{:2}/{:2}{} D{:2} H{:2}+{}",
            self.health,
            self.rune,
            self.current_mana,
            self.max_mana,
            if self.bonus_mana { '+' } else { ' ' },
            self.decksize,
            self.hand.len(),
            self.next_turn_draw
        )
        .fmt(fmt)
    }
}

impl fmt::Display for Keywords {
    fn fmt(&self, fmt: &mut fmt::Formatter<'_>) -> fmt::Result {
        format!(
            "{}{}{}{}{}{}",
            if self.has(Keyword::Breakthrough) {
                '-'
            } else {
                'B'
            },
            if self.has(Keyword::Charge) { '-' } else { 'C' },
            if self.has(Keyword::Drain) { '-' } else { 'D' },
            if self.has(Keyword::Guard) { '-' } else { 'G' },
            if self.has(Keyword::Lethal) { '-' } else { 'L' },
            if self.has(Keyword::Ward) { '-' } else { 'W' }
        )
        .fmt(fmt)
    }
}

impl fmt::Display for Type {
    fn fmt(&self, fmt: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Creature => "creature",
            Self::ItemBlue => "itemBlue",
            Self::ItemGreen => "itemGreen",
            Self::ItemRed => "itemRed",
        }
        .fmt(fmt)
    }
}

macro_rules! parser {
    ($expr:expr) => ($expr.split_whitespace().peekable());
    (N $expr:expr) => (parser!(c parser!(n $expr)));
    (P $expr:expr) => (parser!(c parser!(p $expr)));
    (c $expr:expr) => ($expr.parse().ok().ok_or(())?);
    (n $expr:expr) => ($expr.next().ok_or(())?);
    (p $expr:expr) => ($expr.peek().ok_or(())?);
}

impl str::FromStr for Action {
    type Err = ();

    fn from_str(input: &str) -> Result<Self, Self::Err> {
        let mut tokens = parser!(input);
        match parser!(n tokens) {
            "ATTACK" => Ok(match (parser!(N tokens), parser!(N tokens)) {
                (id, -1) => Self::AttackFace { id },
                (id1, id2) => Self::AttackCard {
                    id1,
                    id2: u8::try_from(id2).ok().ok_or(())?,
                },
            }),
            "PASS" => Ok(Self::Pass),
            "SUMMON" => Ok(Self::Summon {
                id: parser!(N tokens),
                lane: parser!(N tokens),
            }),
            "USE" => Ok(match (parser!(N tokens), parser!(N tokens)) {
                (id, -1) => Self::UseOnFace { id },
                (id1, id2) => Self::UseOnCard {
                    id1,
                    id2: u8::try_from(id2).ok().ok_or(())?,
                },
            }),
            _ => Err(()),
        }
    }
}

impl str::FromStr for Card {
    type Err = ();

    fn from_str(input: &str) -> Result<Self, Self::Err> {
        let mut tokens = parser!(input);
        Ok(Self {
            attack_state: AttackState::NoAttack,
            card_number: parser!(N tokens),
            // NOTE: instance_id == -1 during draft.
            instance_id: match parser!(N tokens) {
                -1 => 0,
                id => u8::try_from(id).ok().ok_or(())?,
            },
            location: parser!(N tokens),
            card_type: parser!(N tokens),
            cost: parser!(N tokens),
            attack: parser!(N tokens),
            defense: parser!(N tokens),
            keywords: parser!(N tokens),
            my_health_change: parser!(N tokens),
            op_health_change: parser!(N tokens),
            card_draw: parser!(N tokens),
            // NOTE: lane == -1 during draft.
            lane: match parser!(N tokens) {
                -1 => 0,
                id => u8::try_from(id).ok().ok_or(())?,
            },
        })
    }
}

impl str::FromStr for Gamer {
    type Err = ();

    fn from_str(input: &str) -> Result<Self, Self::Err> {
        let mut tokens = parser!(input);
        Ok(Self {
            health: parser!(N tokens),
            current_mana: parser!(P tokens),
            max_mana: parser!(N tokens),
            decksize: parser!(N tokens),
            rune: parser!(N tokens),
            next_turn_draw: parser!(N tokens),
            ..Self::default()
        })
    }
}

impl str::FromStr for Keywords {
    type Err = ();

    fn from_str(input: &str) -> Result<Self, Self::Err> {
        let mut mask = Self::default();
        let mut chars = input.chars();
        mask.set(Keyword::Breakthrough, chars.next().ok_or(())? == 'B');
        mask.set(Keyword::Charge, chars.next().ok_or(())? == 'C');
        mask.set(Keyword::Drain, chars.next().ok_or(())? == 'D');
        mask.set(Keyword::Guard, chars.next().ok_or(())? == 'G');
        mask.set(Keyword::Lethal, chars.next().ok_or(())? == 'L');
        mask.set(Keyword::Ward, chars.next().ok_or(())? == 'W');
        Ok(mask)
    }
}

impl str::FromStr for Location {
    type Err = ();

    fn from_str(input: &str) -> Result<Self, Self::Err> {
        match parser!(c input) {
            -1 => Ok(Self::OpBoard),
            0 => Ok(Self::InHand),
            1 => Ok(Self::MyBoard),
            _ => Err(()),
        }
    }
}

impl str::FromStr for Type {
    type Err = ();

    fn from_str(input: &str) -> Result<Self, Self::Err> {
        match parser!(c input) {
            0 => Ok(Self::Creature),
            1 => Ok(Self::ItemGreen),
            2 => Ok(Self::ItemRed),
            3 => Ok(Self::ItemBlue),
            _ => Err(()),
        }
    }
}

impl State {
    pub fn from_lines(lines: &mut impl Iterator<Item = String>) -> Result<Self, ()> {
        let mut me: Gamer = parser!(N lines);
        let mut op: Gamer = parser!(N lines);

        // Ignore opponent hand size and actions.
        for _ in 0..parser!(c parser!(n lines)
            .split_whitespace()
            .last()
            .ok_or(())?)
        {
            parser!(n lines);
        }

        for _ in 0..parser!(N lines) {
            let mut card: Card = parser!(N lines);
            match card.location {
                Location::InHand => {
                    me.hand.push(card);
                }
                Location::MyBoard => {
                    card.attack_state = AttackState::CanAttack;
                    me.boards[card.lane as usize].push(card);
                }
                Location::OpBoard => {
                    card.attack_state = AttackState::CanAttack;
                    op.boards[card.lane as usize].push(card);
                }
            }
        }

        Ok(Self {
            halt: false,
            me,
            op,
        })
    }
}

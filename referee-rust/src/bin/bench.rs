use locm::agents::{Agent, AgentNoop, AgentRandom};
use locm::engine::constants::CARDS;
use locm::referee::{play, Draft};
use rand::rngs::SmallRng;
use rand::{Rng, SeedableRng};
use std::fmt::Debug;
use std::time::Instant;

const TIME: u128 = 1_000_000;

fn bench(a: &(impl Agent + Debug), b: &(impl Agent + Debug), rng: &mut impl Rng) {
    let now = Instant::now();
    let mut plays = 0;
    let mut a_won = 0;
    while now.elapsed().as_micros() < TIME {
        plays += 1;
        if play(a, b, &Draft::new(&CARDS, rng), rng, false) {
            a_won += 1;
        }
    }

    println!(
        "{:?} vs {:?}: {:.2}% {:.2?}/game",
        a,
        b,
        100.0 * (a_won as f32) / (plays as f32),
        now.elapsed() / plays
    );
}

fn main() {
    let mut rng = SmallRng::from_entropy();

    bench(&AgentNoop, &AgentNoop, &mut rng);
    bench(&AgentNoop, &AgentRandom, &mut rng);
    bench(&AgentRandom, &AgentNoop, &mut rng);
    bench(&AgentRandom, &AgentRandom, &mut rng);
}

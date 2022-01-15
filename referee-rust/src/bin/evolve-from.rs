use locm::evolution::constants::{
    ELITISM, EVALUATOR_DRAFTS, EVALUATOR_ROUNDS, EVOLUTION_DRAFTS, EVOLUTION_ROUNDS, GENERATIONS,
    MUTATION_RATE, POPULATION,
};
use locm::evolution::evaluator::Evaluator;
use locm::evolution::individuals::{Individual, LinearIndividual};
use locm::evolution::population::Population;
use rand::rngs::SmallRng;
use rand::SeedableRng;
use std::time::Instant;

fn run(seed: &[f32; 20]) {
    let mut rng = SmallRng::from_entropy();
    let mut evaluator = Evaluator::default();
    let mut population = Population::<LinearIndividual>::default();

    for agent in &mut population.agents {
        agent.weights.clone_from(seed);
        // agent.clone_from(&TreeIndividual::from_weights(seed));
        for _ in 0..5 {
            agent.mutate(&mut rng);
        }
    }

    for generation in 0..GENERATIONS {
        let now = Instant::now();

        population.evolve(&mut rng);
        population.score(&mut rng);
        evaluator.add(population[0].clone());

        println!(
            "generation {:3}: {:7.2?} // best: {:?}",
            generation + 1,
            now.elapsed(),
            population[0]
        );
    }

    evaluator.score(&mut rng);
}

fn main() {
    const SEEDS: [[f32; 20]; 5] = [
        [
            -0.68858814,
            -0.6736405,
            0.30891037,
            -0.87661433,
            -0.718837,
            -0.2777505,
            0.3361919,
            0.8163147,
            -0.6853397,
            -0.7775893,
            -0.14760733,
            0.079236984,
            0.107727766,
            -0.07205725,
            -0.09459996,
            -0.7070575,
            0.93497086,
            0.95310736,
            0.7168217,
            0.59879327,
        ],
        [
            -0.65507054,
            -0.27521205,
            0.4332714,
            0.46793103,
            -0.9381685,
            0.29115748,
            -0.29476237,
            -0.44043612,
            -0.27158856,
            0.58203864,
            0.029629707,
            -0.96088076,
            0.08753133,
            -0.057546377,
            0.2871089,
            -0.20521617,
            0.9566674,
            0.96502376,
            0.5996754,
            0.0856266,
        ],
        [
            -0.9301307,
            0.40433717,
            0.35297656,
            -0.63147354,
            -0.3260188,
            0.4400499,
            -0.8443084,
            -0.3989172,
            -0.31141996,
            -0.33245778,
            0.83642316,
            -0.02224636,
            0.16987157,
            -0.13909411,
            -0.37186933,
            -0.4590733,
            0.8792534,
            0.8682606,
            0.2644744,
            0.3099084,
        ],
        [
            -0.7309079,
            -0.07216716,
            0.2573557,
            -0.09480262,
            0.23570824,
            0.048369884,
            0.41788054,
            0.40940738,
            -0.028533459,
            0.8400798,
            0.86868167,
            -0.9591818,
            0.19604897,
            -0.103866816,
            -0.45361257,
            -0.21116996,
            0.7029624,
            0.70167494,
            0.35807967,
            0.53820753,
        ],
        [
            -0.774174,
            0.058378935,
            0.45359635,
            -0.04020405,
            -0.8860364,
            -0.88844466,
            0.7644248,
            0.03536582,
            -0.53132224,
            0.4131961,
            0.45292902,
            0.37116742,
            0.16640496,
            0.064481735,
            0.17975211,
            -0.25319147,
            0.90268564,
            0.793082,
            0.7690182,
            0.9492855,
        ],
    ];

    for seed in &SEEDS {
        println!("Parameters:");
        println!("  ELITISM {}", ELITISM);
        println!("  EVALUATOR_DRAFTS {}", EVALUATOR_DRAFTS);
        println!("  EVALUATOR_ROUNDS {}", EVALUATOR_ROUNDS);
        println!("  EVOLUTION_DRAFTS {}", EVOLUTION_DRAFTS);
        println!("  EVOLUTION_ROUNDS {}", EVOLUTION_ROUNDS);
        println!("  GENERATIONS {}", GENERATIONS);
        println!("  MUTATION_RATE {}", MUTATION_RATE);
        println!("  POPULATION {}", POPULATION);
        println!("  SEED {:?}", seed);
        println!();
        run(&seed);
    }
}

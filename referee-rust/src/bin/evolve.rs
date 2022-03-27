use locm::agents::{Agent, AgentBaseline2};
use locm::evolution::constants::{
    ELITISM, EVALUATOR_DRAFTS, EVALUATOR_ROUNDS, EVOLUTION_DRAFTS, EVOLUTION_ROUNDS, GENERATIONS,
    MUTATION_RATE, POPULATION,
};
use locm::evolution::evaluator::Evaluator;
use locm::evolution::individuals::{
    tree, BinaryTreeIndividual, Individual, LinearIndividual, TreeIndividual,
};
use locm::evolution::population::Population;
use rand::rngs::SmallRng;
use rand::SeedableRng;
use std::fmt::Debug;
use std::time::Instant;

enum Scoring {
    Baseline,
    FromBest,
    Standard,
}

fn run<I: Agent + Debug + Individual>(scoring: Scoring) {
    let mut rng = SmallRng::from_entropy();
    let mut evaluator = Evaluator::default();
    let mut population = Population::<I>::default();

    population.randomize(&mut rng);
    for generation in 0..GENERATIONS {
        let now = Instant::now();

        population.evolve(&mut rng);
        match scoring {
            Scoring::Baseline => population.score_against(&mut rng, &AgentBaseline2),
            Scoring::FromBest => population.score_against(
                &mut rng,
                &TreeIndividual {
                    card_node: {
                        use tree::CardNode::*;
                        OperatorAdd(vec![
                            OperatorMul(vec![FeatureAttack, FeatureHasDrain]),
                            Literal(0.96502376),
                            FeatureHasLethal,
                            OperatorMul(vec![FeatureHasCharge, Literal(-0.20521617)]),
                            OperatorMul(vec![FeatureHasDrain, Literal(0.9566674)]),
                            Literal(0.96502376),
                            OperatorAdd(vec![
                                OperatorMul(vec![
                                    FeatureAttack,
                                    OperatorAdd(vec![
                                        OperatorMul(vec![
                                            FeatureAttack,
                                            OperatorMul(vec![
                                                FeatureHasCharge,
                                                Literal(-0.20521617),
                                            ]),
                                        ]),
                                        OperatorMul(vec![
                                            Literal(0.96502376),
                                            Literal(-0.057546377),
                                        ]),
                                        Literal(0.2871089),
                                        OperatorMul(vec![
                                            FeatureHasCharge,
                                            OperatorMul(vec![FeatureHasDrain, Literal(0.9566674)]),
                                        ]),
                                        OperatorMul(vec![
                                            Literal(0.0856266),
                                            OperatorMul(vec![
                                                FeatureHasCharge,
                                                OperatorMul(vec![
                                                    OperatorAdd(vec![
                                                        OperatorMul(vec![
                                                            FeatureAttack,
                                                            Literal(0.08753133),
                                                        ]),
                                                        OperatorMul(vec![
                                                            FeatureDefense,
                                                            Literal(-0.057546377),
                                                        ]),
                                                        OperatorMul(vec![
                                                            FeatureDefense,
                                                            FeatureHasCharge,
                                                        ]),
                                                        OperatorMul(vec![
                                                            FeatureHasCharge,
                                                            Literal(-0.20521617),
                                                        ]),
                                                        OperatorMul(vec![
                                                            FeatureHasDrain,
                                                            Literal(0.9566674),
                                                        ]),
                                                        OperatorMul(vec![
                                                            FeatureHasGuard,
                                                            Literal(0.96502376),
                                                        ]),
                                                        Literal(-0.20521617),
                                                        OperatorMul(vec![
                                                            FeatureHasWard,
                                                            OperatorMul(vec![
                                                                FeatureHasBreakthrough,
                                                                Literal(0.2871089),
                                                            ]),
                                                        ]),
                                                    ]),
                                                    FeatureHasDrain,
                                                ]),
                                            ]),
                                        ]),
                                        OperatorMul(vec![FeatureHasGuard, Literal(0.96502376)]),
                                        OperatorMul(vec![
                                            FeatureHasBreakthrough,
                                            Literal(-0.20521617),
                                        ]),
                                        FeatureHasWard,
                                    ]),
                                ]),
                                OperatorMul(vec![FeatureHasLethal, Literal(0.5996754)]),
                                OperatorMul(vec![FeatureHasBreakthrough, Literal(0.2871089)]),
                                OperatorMul(vec![
                                    Literal(0.9566674),
                                    OperatorMul(vec![FeatureHasLethal, Literal(0.5996754)]),
                                ]),
                                Literal(0.9566674),
                                FeatureHasCharge,
                                OperatorMul(vec![Literal(0.9566674), Literal(0.5996754)]),
                                OperatorMul(vec![FeatureHasWard, Literal(0.0856266)]),
                            ]),
                            FeatureHasWard,
                        ])
                    },
                    state_node: {
                        use tree::StateNode::*;
                        OperatorAdd(vec![
                            OperatorMul(vec![FeatureMeDecksize, Literal(-0.27521205)]),
                            OperatorMul(vec![FeatureOpCurrentMana, Literal(-0.27521205)]),
                            Literal(0.029629707),
                            FeatureMeMaxMana,
                            Literal(-0.65507054),
                            OperatorAdd(vec![
                                OperatorMul(vec![FeatureMeCurrentMana, Literal(-0.65507054)]),
                                FeatureOpCurrentMana,
                                Literal(0.029629707),
                                OperatorMul(vec![FeatureMeMaxMana, FeatureMeRune]),
                                OperatorMul(vec![Literal(0.46793103), Literal(-0.96088076)]),
                                OperatorMul(vec![FeatureMeRune, Literal(0.29115748)]),
                                OperatorMul(vec![Literal(0.029629707), Literal(-0.29476237)]),
                                OperatorMul(vec![
                                    Literal(-0.27521205),
                                    OperatorMul(vec![
                                        OperatorMul(vec![FeatureMeMaxMana, Literal(0.58203864)]),
                                        Literal(-0.44043612),
                                    ]),
                                ]),
                                OperatorNeg(Box::new(OperatorMul(vec![
                                    FeatureMeNextTurnDraw,
                                    Literal(-0.9381685),
                                ]))),
                                OperatorMul(vec![FeatureMeMaxMana, Literal(0.58203864)]),
                                OperatorMul(vec![FeatureOpNextTurnDraw, FeatureMeHealth]),
                                OperatorMul(vec![Literal(0.46793103), Literal(-0.96088076)]),
                            ]),
                            FeatureOpNextTurnDraw,
                            OperatorMul(vec![
                                OperatorNeg(Box::new(OperatorMul(vec![
                                    FeatureMeRune,
                                    Literal(-0.9381685),
                                ]))),
                                Literal(-0.44043612),
                            ]),
                            OperatorMul(vec![FeatureOpHealth, Literal(-0.29476237)]),
                            OperatorMul(vec![FeatureMeNextTurnDraw, Literal(0.29115748)]),
                            OperatorMul(vec![
                                OperatorMul(vec![
                                    FeatureMeRune,
                                    OperatorMul(vec![FeatureMeCurrentMana, Literal(-0.65507054)]),
                                ]),
                                Literal(0.029629707),
                            ]),
                            OperatorMul(vec![FeatureOpCurrentMana, Literal(-0.44043612)]),
                        ])
                    },
                },
            ),
            Scoring::Standard => population.score(&mut rng),
        }
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
    println!("Parameters:");
    println!("  ELITISM {}", ELITISM);
    println!("  EVALUATOR_DRAFTS {}", EVALUATOR_DRAFTS);
    println!("  EVALUATOR_ROUNDS {}", EVALUATOR_ROUNDS);
    println!("  EVOLUTION_DRAFTS {}", EVOLUTION_DRAFTS);
    println!("  EVOLUTION_ROUNDS {}", EVOLUTION_ROUNDS);
    println!("  GENERATIONS {}", GENERATIONS);
    println!("  INDIVIDUAL {}", option_env!("INDIVIDUAL").unwrap());
    println!("  MUTATION_RATE {}", MUTATION_RATE);
    println!("  POPULATION {}", POPULATION);
    println!("  SCORING {}", option_env!("SCORING").unwrap());
    println!();

    let scoring = match option_env!("SCORING").unwrap() {
        "baseline" => Scoring::Baseline,
        "frombest" => Scoring::FromBest,
        "standard" => Scoring::Standard,
        _ => unimplemented!(),
    };

    match option_env!("INDIVIDUAL").unwrap() {
        "BinaryTree" => run::<BinaryTreeIndividual>(scoring),
        "Linear" => run::<LinearIndividual>(scoring),
        "Tree" => run::<TreeIndividual>(scoring),
        _ => unimplemented!(),
    };
}

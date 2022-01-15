use locm::agents::{Agent, AgentRandom};
use locm::evolution::individuals::{binarytree, linear, tree};
use locm::referee::run;
use rand::rngs::SmallRng;
use rand::SeedableRng;
use std::io::{self, BufRead};

fn play(agent: impl Agent) -> Result<(), ()> {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines().filter_map(Result::ok);
    let mut rng = SmallRng::from_entropy();
    run(&agent, &mut lines, &mut rng)
}

fn main() -> Result<(), ()> {
    match option_env!("AGENT") {
        Some("BinaryTree-baseline-1") => play(binarytree::BinaryTreeIndividual {
            card_node: {
                use binarytree::CardNode::*;
                OperatorSub(Box::new(OperatorSub(Box::new(OperatorSub(Box::new(OperatorSub(Box::new(FeatureAttack), Box::new(OperatorSub(Box::new(OperatorSub(Box::new(FeatureAttack), Box::new(OperatorSub(Box::new(OperatorSub(Box::new(OperatorSub(Box::new(FeatureAttack), Box::new(OperatorSub(Box::new(OperatorSub(Box::new(FeatureHasWard), Box::new(OperatorSub(Box::new(FeatureHasGuard), Box::new(OperatorSub(Box::new(OperatorSub(Box::new(FeatureDefense), Box::new(FeatureHasDrain))), Box::new(OperatorSub(Box::new(OperatorSub(Box::new(OperatorSub(Box::new(OperatorSub(Box::new(FeatureAttack), Box::new(OperatorSub(Box::new(OperatorSub(Box::new(FeatureAttack), Box::new(FeatureDefense))), Box::new(FeatureAttack))))), Box::new(OperatorSub(Box::new(FeatureAttack), Box::new(FeatureAttack))))), Box::new(FeatureHasBreakthrough))), Box::new(OperatorSub(Box::new(OperatorSub(Box::new(FeatureAttack), Box::new(OperatorSub(Box::new(FeatureAttack), Box::new(FeatureAttack))))), Box::new(OperatorSub(Box::new(OperatorSub(Box::new(FeatureAttack), Box::new(OperatorSub(Box::new(FeatureAttack), Box::new(OperatorSub(Box::new(OperatorSub(Box::new(OperatorSub(Box::new(OperatorSub(Box::new(FeatureAttack), Box::new(OperatorSub(Box::new(OperatorSub(Box::new(FeatureAttack), Box::new(FeatureDefense))), Box::new(FeatureAttack))))), Box::new(FeatureDefense))), Box::new(FeatureHasBreakthrough))), Box::new(OperatorSub(Box::new(OperatorSub(Box::new(FeatureHasWard), Box::new(FeatureHasGuard))), Box::new(FeatureHasDrain))))))))), Box::new(FeatureAttack))))))))))))), Box::new(FeatureDefense))))), Box::new(OperatorMax(Box::new(FeatureDefense), Box::new(FeatureDefense))))), Box::new(FeatureDefense))))), Box::new(FeatureAttack))))), Box::new(OperatorSub(Box::new(FeatureAttack), Box::new(FeatureAttack))))), Box::new(FeatureHasBreakthrough))), Box::new(FeatureAttack))
            },
            state_node: {
                use binarytree::StateNode::*;
                FeatureOpNextTurnDraw
            },
        }),
        Some("BinaryTree-baseline-3") => play(binarytree::BinaryTreeIndividual {
            card_node: {
                use binarytree::CardNode::*;
                OperatorAdd(
                    Box::new(FeatureAttack),
                    Box::new(OperatorMul(
                        Box::new(FeatureAttack),
                        Box::new(OperatorMul(
                            Box::new(OperatorSub(
                                Box::new(FeatureAttack),
                                Box::new(Literal(-0.19096828)),
                            )),
                            Box::new(OperatorMul(
                                Box::new(OperatorMul(
                                    Box::new(OperatorSub(
                                        Box::new(FeatureHasDrain),
                                        Box::new(FeatureHasBreakthrough),
                                    )),
                                    Box::new(OperatorAdd(
                                        Box::new(FeatureAttack),
                                        Box::new(OperatorMul(
                                            Box::new(OperatorMul(
                                                Box::new(OperatorMul(
                                                    Box::new(OperatorMul(
                                                        Box::new(FeatureAttack),
                                                        Box::new(FeatureAttack),
                                                    )),
                                                    Box::new(FeatureAttack),
                                                )),
                                                Box::new(OperatorSub(
                                                    Box::new(FeatureAttack),
                                                    Box::new(FeatureAttack),
                                                )),
                                            )),
                                            Box::new(OperatorMul(
                                                Box::new(FeatureAttack),
                                                Box::new(OperatorMul(
                                                    Box::new(OperatorMul(
                                                        Box::new(FeatureAttack),
                                                        Box::new(FeatureAttack),
                                                    )),
                                                    Box::new(FeatureAttack),
                                                )),
                                            )),
                                        )),
                                    )),
                                )),
                                Box::new(FeatureAttack),
                            )),
                        )),
                    )),
                )
            },
            state_node: {
                use binarytree::StateNode::*;
                OperatorAdd(
                    Box::new(OperatorMul(
                        Box::new(FeatureOpNextTurnDraw),
                        Box::new(FeatureOpMaxMana),
                    )),
                    Box::new(OperatorMax(
                        Box::new(OperatorAdd(
                            Box::new(FeatureOpNextTurnDraw),
                            Box::new(FeatureOpNextTurnDraw),
                        )),
                        Box::new(OperatorMax(
                            Box::new(FeatureOpNextTurnDraw),
                            Box::new(FeatureOpNextTurnDraw),
                        )),
                    )),
                )
            },
        }),
        Some("BinaryTree-baseline-4") => play(binarytree::BinaryTreeIndividual {
            card_node: {
                use binarytree::CardNode::*;
                OperatorMax(
                    Box::new(OperatorMul(
                        Box::new(OperatorMax(
                            Box::new(OperatorMin(
                                Box::new(FeatureHasWard),
                                Box::new(FeatureHasDrain),
                            )),
                            Box::new(Literal(0.030317307)),
                        )),
                        Box::new(FeatureAttack),
                    )),
                    Box::new(OperatorMul(
                        Box::new(OperatorMax(
                            Box::new(OperatorMul(
                                Box::new(OperatorMax(
                                    Box::new(OperatorMax(
                                        Box::new(Literal(0.030317307)),
                                        Box::new(OperatorMax(
                                            Box::new(OperatorMul(
                                                Box::new(OperatorMul(
                                                    Box::new(OperatorMin(
                                                        Box::new(OperatorAdd(
                                                            Box::new(FeatureHasDrain),
                                                            Box::new(FeatureHasGuard),
                                                        )),
                                                        Box::new(FeatureHasWard),
                                                    )),
                                                    Box::new(FeatureHasBreakthrough),
                                                )),
                                                Box::new(OperatorMul(
                                                    Box::new(OperatorMax(
                                                        Box::new(OperatorMax(
                                                            Box::new(Literal(0.34609485)),
                                                            Box::new(FeatureHasDrain),
                                                        )),
                                                        Box::new(OperatorMax(
                                                            Box::new(Literal(0.34609485)),
                                                            Box::new(FeatureAttack),
                                                        )),
                                                    )),
                                                    Box::new(OperatorMax(
                                                        Box::new(Literal(0.34609485)),
                                                        Box::new(FeatureHasDrain),
                                                    )),
                                                )),
                                            )),
                                            Box::new(FeatureHasDrain),
                                        )),
                                    )),
                                    Box::new(OperatorMax(
                                        Box::new(OperatorMin(
                                            Box::new(FeatureHasDrain),
                                            Box::new(FeatureHasDrain),
                                        )),
                                        Box::new(FeatureHasDrain),
                                    )),
                                )),
                                Box::new(FeatureAttack),
                            )),
                            Box::new(FeatureHasDrain),
                        )),
                        Box::new(OperatorMax(
                            Box::new(FeatureHasDrain),
                            Box::new(FeatureAttack),
                        )),
                    )),
                )
            },
            state_node: {
                use binarytree::StateNode::*;
                FeatureOpNextTurnDraw
            },
        }),
        Some("BinaryTree-baseline-5") => play(binarytree::BinaryTreeIndividual {
            card_node: {
                use binarytree::CardNode::*;
                OperatorMax(
                    Box::new(OperatorMax(
                        Box::new(OperatorSub(
                            Box::new(OperatorSub(
                                Box::new(FeatureAttack),
                                Box::new(OperatorSub(
                                    Box::new(FeatureDefense),
                                    Box::new(OperatorMax(
                                        Box::new(OperatorSub(
                                            Box::new(OperatorSub(
                                                Box::new(FeatureAttack),
                                                Box::new(OperatorMax(
                                                    Box::new(FeatureDefense),
                                                    Box::new(FeatureDefense),
                                                )),
                                            )),
                                            Box::new(OperatorMax(
                                                Box::new(FeatureHasBreakthrough),
                                                Box::new(OperatorSub(
                                                    Box::new(Literal(0.12208748)),
                                                    Box::new(OperatorMax(
                                                        Box::new(FeatureDefense),
                                                        Box::new(FeatureDefense),
                                                    )),
                                                )),
                                            )),
                                        )),
                                        Box::new(Literal(0.12208748)),
                                    )),
                                )),
                            )),
                            Box::new(OperatorMax(
                                Box::new(FeatureHasBreakthrough),
                                Box::new(OperatorMax(
                                    Box::new(Literal(0.12208748)),
                                    Box::new(FeatureHasBreakthrough),
                                )),
                            )),
                        )),
                        Box::new(OperatorSub(
                            Box::new(FeatureHasCharge),
                            Box::new(FeatureAttack),
                        )),
                    )),
                    Box::new(Literal(0.12208748)),
                )
            },
            state_node: {
                use binarytree::StateNode::*;
                FeatureOpNextTurnDraw
            },
        }),
        Some("BinaryTree-frombest-1") => play(binarytree::BinaryTreeIndividual {
            card_node: {
                use binarytree::CardNode::*;
                OperatorMax(
                    Box::new(FeatureHasCharge),
                    Box::new(OperatorAdd(
                        Box::new(OperatorSub(
                            Box::new(OperatorMax(
                                Box::new(OperatorSub(
                                    Box::new(FeatureHasWard),
                                    Box::new(OperatorMax(
                                        Box::new(OperatorAdd(
                                            Box::new(FeatureAttack),
                                            Box::new(FeatureHasLethal),
                                        )),
                                        Box::new(FeatureAttack),
                                    )),
                                )),
                                Box::new(OperatorAdd(
                                    Box::new(OperatorSub(
                                        Box::new(OperatorAdd(
                                            Box::new(FeatureAttack),
                                            Box::new(OperatorSub(
                                                Box::new(FeatureHasWard),
                                                Box::new(FeatureHasCharge),
                                            )),
                                        )),
                                        Box::new(FeatureHasCharge),
                                    )),
                                    Box::new(OperatorMul(
                                        Box::new(FeatureHasGuard),
                                        Box::new(FeatureAttack),
                                    )),
                                )),
                            )),
                            Box::new(FeatureHasCharge),
                        )),
                        Box::new(OperatorMul(
                            Box::new(FeatureHasGuard),
                            Box::new(FeatureAttack),
                        )),
                    )),
                )
            },
            state_node: {
                use binarytree::StateNode::*;
                OperatorMax(
                    Box::new(OperatorAdd(
                        Box::new(FeatureOpMaxMana),
                        Box::new(FeatureOpDecksize),
                    )),
                    Box::new(OperatorAdd(
                        Box::new(OperatorAdd(
                            Box::new(OperatorMul(
                                Box::new(OperatorMul(
                                    Box::new(FeatureOpNextTurnDraw),
                                    Box::new(FeatureOpMaxMana),
                                )),
                                Box::new(FeatureOpMaxMana),
                            )),
                            Box::new(OperatorMul(
                                Box::new(FeatureOpDecksize),
                                Box::new(FeatureOpNextTurnDraw),
                            )),
                        )),
                        Box::new(Literal(-0.37973142)),
                    )),
                )
            },
        }),
        Some("BinaryTree-frombest-2") => play(binarytree::BinaryTreeIndividual {
            card_node: {
                use binarytree::CardNode::*;
                OperatorMin(
                    Box::new(OperatorMin(
                        Box::new(FeatureAttack),
                        Box::new(OperatorMax(
                            Box::new(FeatureAttack),
                            Box::new(OperatorMul(
                                Box::new(OperatorAdd(
                                    Box::new(OperatorMul(
                                        Box::new(OperatorMax(
                                            Box::new(OperatorMax(
                                                Box::new(FeatureHasCharge),
                                                Box::new(FeatureHasBreakthrough),
                                            )),
                                            Box::new(FeatureHasCharge),
                                        )),
                                        Box::new(FeatureAttack),
                                    )),
                                    Box::new(FeatureHasGuard),
                                )),
                                Box::new(FeatureHasGuard),
                            )),
                        )),
                    )),
                    Box::new(OperatorSub(
                        Box::new(Literal(0.07360673)),
                        Box::new(OperatorSub(
                            Box::new(FeatureDefense),
                            Box::new(FeatureDefense),
                        )),
                    )),
                )
            },
            state_node: {
                use binarytree::StateNode::*;
                OperatorMul(
                    Box::new(FeatureOpMaxMana),
                    Box::new(OperatorSub(
                        Box::new(FeatureOpNextTurnDraw),
                        Box::new(FeatureMeCurrentMana),
                    )),
                )
            },
        }),
        Some("BinaryTree-frombest-3") => play(binarytree::BinaryTreeIndividual {
            card_node: {
                use binarytree::CardNode::*;
                OperatorMax(
                    Box::new(OperatorSub(
                        Box::new(FeatureAttack),
                        Box::new(OperatorMax(
                            Box::new(OperatorMul(
                                Box::new(FeatureAttack),
                                Box::new(OperatorMin(
                                    Box::new(FeatureDefense),
                                    Box::new(OperatorAdd(
                                        Box::new(FeatureDefense),
                                        Box::new(FeatureHasLethal),
                                    )),
                                )),
                            )),
                            Box::new(FeatureDefense),
                        )),
                    )),
                    Box::new(OperatorAdd(
                        Box::new(OperatorAdd(
                            Box::new(OperatorMax(
                                Box::new(FeatureAttack),
                                Box::new(OperatorMin(
                                    Box::new(FeatureDefense),
                                    Box::new(OperatorMul(
                                        Box::new(OperatorMin(
                                            Box::new(FeatureDefense),
                                            Box::new(OperatorAdd(
                                                Box::new(OperatorAdd(
                                                    Box::new(OperatorSub(
                                                        Box::new(OperatorMax(
                                                            Box::new(FeatureHasCharge),
                                                            Box::new(OperatorMin(
                                                                Box::new(FeatureHasWard),
                                                                Box::new(OperatorAdd(
                                                                    Box::new(
                                                                        FeatureHasBreakthrough,
                                                                    ),
                                                                    Box::new(FeatureHasLethal),
                                                                )),
                                                            )),
                                                        )),
                                                        Box::new(FeatureHasWard),
                                                    )),
                                                    Box::new(FeatureHasLethal),
                                                )),
                                                Box::new(FeatureHasLethal),
                                            )),
                                        )),
                                        Box::new(OperatorAdd(
                                            Box::new(FeatureDefense),
                                            Box::new(FeatureHasLethal),
                                        )),
                                    )),
                                )),
                            )),
                            Box::new(FeatureHasGuard),
                        )),
                        Box::new(FeatureHasGuard),
                    )),
                )
            },
            state_node: {
                use binarytree::StateNode::*;
                FeatureOpNextTurnDraw
            },
        }),
        Some("BinaryTree-frombest-4") => play(binarytree::BinaryTreeIndividual {
            card_node: {
                use binarytree::CardNode::*;
                OperatorAdd(
                    Box::new(OperatorMul(
                        Box::new(OperatorAdd(
                            Box::new(OperatorMul(
                                Box::new(FeatureHasGuard),
                                Box::new(FeatureHasGuard),
                            )),
                            Box::new(OperatorAdd(
                                Box::new(FeatureAttack),
                                Box::new(OperatorMin(
                                    Box::new(FeatureAttack),
                                    Box::new(FeatureHasCharge),
                                )),
                            )),
                        )),
                        Box::new(OperatorMul(
                            Box::new(FeatureHasGuard),
                            Box::new(OperatorMul(
                                Box::new(FeatureHasGuard),
                                Box::new(OperatorMul(
                                    Box::new(FeatureHasCharge),
                                    Box::new(FeatureAttack),
                                )),
                            )),
                        )),
                    )),
                    Box::new(OperatorAdd(
                        Box::new(OperatorMul(
                            Box::new(FeatureHasGuard),
                            Box::new(FeatureAttack),
                        )),
                        Box::new(FeatureAttack),
                    )),
                )
            },
            state_node: {
                use binarytree::StateNode::*;
                OperatorAdd(
                    Box::new(OperatorAdd(
                        Box::new(FeatureOpNextTurnDraw),
                        Box::new(OperatorAdd(
                            Box::new(FeatureOpNextTurnDraw),
                            Box::new(FeatureOpNextTurnDraw),
                        )),
                    )),
                    Box::new(OperatorAdd(
                        Box::new(FeatureOpNextTurnDraw),
                        Box::new(FeatureOpCurrentMana),
                    )),
                )
            },
        }),
        Some("BinaryTree-frombest-5") => play(binarytree::BinaryTreeIndividual {
            card_node: {
                use binarytree::CardNode::*;
                OperatorSub(Box::new(OperatorSub(Box::new(FeatureHasGuard), Box::new(OperatorSub(Box::new(Literal(-0.96907663)), Box::new(FeatureAttack))))), Box::new(OperatorSub(Box::new(OperatorSub(Box::new(Literal(-0.96907663)), Box::new(OperatorSub(Box::new(OperatorMul(Box::new(OperatorMin(Box::new(OperatorAdd(Box::new(Literal(-0.96907663)), Box::new(FeatureAttack))), Box::new(FeatureHasLethal))), Box::new(FeatureHasGuard))), Box::new(OperatorSub(Box::new(Literal(-0.96907663)), Box::new(FeatureHasGuard))))))), Box::new(OperatorSub(Box::new(OperatorMax(Box::new(FeatureAttack), Box::new(OperatorSub(Box::new(FeatureAttack), Box::new(OperatorSub(Box::new(FeatureAttack), Box::new(OperatorSub(Box::new(OperatorSub(Box::new(Literal(-0.96907663)), Box::new(FeatureAttack))), Box::new(OperatorSub(Box::new(OperatorMul(Box::new(OperatorMin(Box::new(OperatorAdd(Box::new(FeatureHasBreakthrough), Box::new(FeatureAttack))), Box::new(FeatureHasLethal))), Box::new(FeatureHasGuard))), Box::new(OperatorSub(Box::new(OperatorSub(Box::new(OperatorMul(Box::new(FeatureHasGuard), Box::new(FeatureAttack))), Box::new(OperatorSub(Box::new(Literal(-0.96907663)), Box::new(FeatureAttack))))), Box::new(OperatorSub(Box::new(OperatorSub(Box::new(Literal(-0.96907663)), Box::new(OperatorSub(Box::new(Literal(-0.96907663)), Box::new(FeatureAttack))))), Box::new(OperatorSub(Box::new(Literal(-0.96907663)), Box::new(OperatorSub(Box::new(OperatorSub(Box::new(OperatorSub(Box::new(OperatorSub(Box::new(OperatorMul(Box::new(FeatureHasGuard), Box::new(FeatureAttack))), Box::new(OperatorSub(Box::new(FeatureHasGuard), Box::new(FeatureAttack))))), Box::new(OperatorSub(Box::new(Literal(-0.96907663)), Box::new(OperatorSub(Box::new(OperatorMax(Box::new(OperatorSub(Box::new(OperatorMax(Box::new(FeatureAttack), Box::new(OperatorSub(Box::new(FeatureAttack), Box::new(FeatureHasBreakthrough))))), Box::new(OperatorSub(Box::new(Literal(-0.96907663)), Box::new(OperatorSub(Box::new(Literal(-0.96907663)), Box::new(FeatureAttack))))))), Box::new(OperatorSub(Box::new(FeatureAttack), Box::new(FeatureHasBreakthrough))))), Box::new(OperatorSub(Box::new(FeatureAttack), Box::new(OperatorSub(Box::new(OperatorSub(Box::new(Literal(-0.96907663)), Box::new(OperatorSub(Box::new(OperatorMax(Box::new(OperatorSub(Box::new(Literal(-0.96907663)), Box::new(FeatureAttack))), Box::new(FeatureAttack))), Box::new(OperatorSub(Box::new(Literal(-0.96907663)), Box::new(FeatureAttack))))))), Box::new(Literal(-0.96907663)))))))))))), Box::new(FeatureHasWard))), Box::new(FeatureAttack))))))))))))))))))), Box::new(OperatorSub(Box::new(FeatureAttack), Box::new(FeatureHasGuard))))))))
            },
            state_node: {
                use binarytree::StateNode::*;
                FeatureOpNextTurnDraw
            },
        }),
        Some("BinaryTree-standard-1") => play(binarytree::BinaryTreeIndividual {
            card_node: {
                use binarytree::CardNode::*;
                OperatorAdd(
                    Box::new(OperatorAdd(
                        Box::new(OperatorMul(
                            Box::new(OperatorAdd(
                                Box::new(FeatureHasLethal),
                                Box::new(OperatorMul(
                                    Box::new(OperatorMul(
                                        Box::new(OperatorMul(
                                            Box::new(FeatureAttack),
                                            Box::new(OperatorMul(
                                                Box::new(FeatureHasGuard),
                                                Box::new(FeatureAttack),
                                            )),
                                        )),
                                        Box::new(OperatorMul(
                                            Box::new(FeatureAttack),
                                            Box::new(FeatureHasLethal),
                                        )),
                                    )),
                                    Box::new(FeatureAttack),
                                )),
                            )),
                            Box::new(OperatorAdd(
                                Box::new(OperatorAdd(
                                    Box::new(OperatorMul(
                                        Box::new(FeatureHasGuard),
                                        Box::new(FeatureAttack),
                                    )),
                                    Box::new(FeatureAttack),
                                )),
                                Box::new(FeatureAttack),
                            )),
                        )),
                        Box::new(OperatorAdd(
                            Box::new(OperatorAdd(
                                Box::new(OperatorMul(
                                    Box::new(FeatureAttack),
                                    Box::new(FeatureHasGuard),
                                )),
                                Box::new(OperatorMul(
                                    Box::new(FeatureHasLethal),
                                    Box::new(OperatorMul(
                                        Box::new(FeatureAttack),
                                        Box::new(FeatureHasGuard),
                                    )),
                                )),
                            )),
                            Box::new(FeatureHasDrain),
                        )),
                    )),
                    Box::new(FeatureAttack),
                )
            },
            state_node: {
                use binarytree::StateNode::*;
                FeatureOpNextTurnDraw
            },
        }),
        Some("BinaryTree-standard-2") => play(binarytree::BinaryTreeIndividual {
            card_node: {
                use binarytree::CardNode::*;
                OperatorMax(
                    Box::new(OperatorMul(
                        Box::new(OperatorMax(
                            Box::new(FeatureAttack),
                            Box::new(OperatorSub(
                                Box::new(FeatureAttack),
                                Box::new(Literal(0.36962914)),
                            )),
                        )),
                        Box::new(OperatorMax(
                            Box::new(OperatorMul(
                                Box::new(OperatorMax(
                                    Box::new(FeatureHasGuard),
                                    Box::new(FeatureHasDrain),
                                )),
                                Box::new(FeatureAttack),
                            )),
                            Box::new(OperatorMul(
                                Box::new(OperatorMul(
                                    Box::new(FeatureAttack),
                                    Box::new(FeatureHasLethal),
                                )),
                                Box::new(OperatorMax(
                                    Box::new(FeatureAttack),
                                    Box::new(OperatorMul(
                                        Box::new(FeatureAttack),
                                        Box::new(FeatureHasLethal),
                                    )),
                                )),
                            )),
                        )),
                    )),
                    Box::new(OperatorMul(
                        Box::new(OperatorMax(
                            Box::new(OperatorMul(
                                Box::new(OperatorMax(
                                    Box::new(Literal(0.36962914)),
                                    Box::new(OperatorMul(
                                        Box::new(OperatorSub(
                                            Box::new(FeatureAttack),
                                            Box::new(FeatureHasLethal),
                                        )),
                                        Box::new(FeatureHasLethal),
                                    )),
                                )),
                                Box::new(FeatureAttack),
                            )),
                            Box::new(OperatorMul(
                                Box::new(OperatorSub(
                                    Box::new(OperatorSub(
                                        Box::new(Literal(0.36962914)),
                                        Box::new(FeatureAttack),
                                    )),
                                    Box::new(FeatureHasLethal),
                                )),
                                Box::new(FeatureHasDrain),
                            )),
                        )),
                        Box::new(Literal(0.36962914)),
                    )),
                )
            },
            state_node: {
                use binarytree::StateNode::*;
                OperatorAdd(
                    Box::new(OperatorAdd(
                        Box::new(OperatorAdd(
                            Box::new(OperatorAdd(
                                Box::new(FeatureOpNextTurnDraw),
                                Box::new(FeatureOpDecksize),
                            )),
                            Box::new(FeatureOpNextTurnDraw),
                        )),
                        Box::new(OperatorAdd(
                            Box::new(OperatorAdd(
                                Box::new(FeatureOpNextTurnDraw),
                                Box::new(OperatorAdd(
                                    Box::new(OperatorAdd(
                                        Box::new(FeatureOpNextTurnDraw),
                                        Box::new(FeatureOpNextTurnDraw),
                                    )),
                                    Box::new(FeatureOpNextTurnDraw),
                                )),
                            )),
                            Box::new(FeatureOpNextTurnDraw),
                        )),
                    )),
                    Box::new(FeatureOpNextTurnDraw),
                )
            },
        }),
        Some("BinaryTree-standard-3") => play(binarytree::BinaryTreeIndividual {
            card_node: {
                use binarytree::CardNode::*;
                OperatorMax(
                    Box::new(OperatorAdd(
                        Box::new(FeatureHasWard),
                        Box::new(OperatorAdd(
                            Box::new(FeatureHasWard),
                            Box::new(OperatorMax(
                                Box::new(FeatureAttack),
                                Box::new(FeatureAttack),
                            )),
                        )),
                    )),
                    Box::new(OperatorAdd(
                        Box::new(OperatorMax(
                            Box::new(OperatorAdd(
                                Box::new(OperatorAdd(
                                    Box::new(FeatureHasWard),
                                    Box::new(OperatorMax(
                                        Box::new(FeatureHasWard),
                                        Box::new(FeatureHasCharge),
                                    )),
                                )),
                                Box::new(OperatorAdd(
                                    Box::new(FeatureHasWard),
                                    Box::new(OperatorMax(
                                        Box::new(FeatureHasWard),
                                        Box::new(FeatureHasCharge),
                                    )),
                                )),
                            )),
                            Box::new(FeatureHasLethal),
                        )),
                        Box::new(OperatorMax(
                            Box::new(Literal(-0.117366314)),
                            Box::new(OperatorAdd(
                                Box::new(OperatorMax(
                                    Box::new(FeatureAttack),
                                    Box::new(FeatureAttack),
                                )),
                                Box::new(FeatureHasGuard),
                            )),
                        )),
                    )),
                )
            },
            state_node: {
                use binarytree::StateNode::*;
                OperatorMul(
                    Box::new(FeatureOpNextTurnDraw),
                    Box::new(FeatureOpNextTurnDraw),
                )
            },
        }),
        Some("BinaryTree-standard-4") => play(binarytree::BinaryTreeIndividual {
            card_node: {
                use binarytree::CardNode::*;
                OperatorAdd(
                    Box::new(FeatureHasBreakthrough),
                    Box::new(OperatorAdd(
                        Box::new(FeatureHasWard),
                        Box::new(OperatorAdd(
                            Box::new(OperatorMax(
                                Box::new(OperatorAdd(
                                    Box::new(FeatureAttack),
                                    Box::new(FeatureHasGuard),
                                )),
                                Box::new(OperatorSub(
                                    Box::new(OperatorMul(
                                        Box::new(FeatureHasGuard),
                                        Box::new(OperatorAdd(
                                            Box::new(OperatorMax(
                                                Box::new(FeatureHasBreakthrough),
                                                Box::new(OperatorAdd(
                                                    Box::new(FeatureHasLethal),
                                                    Box::new(FeatureHasLethal),
                                                )),
                                            )),
                                            Box::new(FeatureHasGuard),
                                        )),
                                    )),
                                    Box::new(FeatureHasCharge),
                                )),
                            )),
                            Box::new(OperatorAdd(
                                Box::new(OperatorAdd(
                                    Box::new(FeatureHasWard),
                                    Box::new(FeatureHasGuard),
                                )),
                                Box::new(OperatorAdd(
                                    Box::new(OperatorAdd(
                                        Box::new(FeatureHasLethal),
                                        Box::new(FeatureHasDrain),
                                    )),
                                    Box::new(FeatureHasWard),
                                )),
                            )),
                        )),
                    )),
                )
            },
            state_node: {
                use binarytree::StateNode::*;
                OperatorMul(
                    Box::new(FeatureOpNextTurnDraw),
                    Box::new(FeatureOpNextTurnDraw),
                )
            },
        }),
        Some("BinaryTree-standard-5") => play(binarytree::BinaryTreeIndividual {
            card_node: {
                use binarytree::CardNode::*;
                OperatorAdd(
                    Box::new(OperatorAdd(
                        Box::new(OperatorAdd(
                            Box::new(FeatureAttack),
                            Box::new(OperatorAdd(
                                Box::new(OperatorAdd(
                                    Box::new(OperatorAdd(
                                        Box::new(FeatureHasWard),
                                        Box::new(OperatorAdd(
                                            Box::new(FeatureHasLethal),
                                            Box::new(OperatorAdd(
                                                Box::new(OperatorAdd(
                                                    Box::new(FeatureAttack),
                                                    Box::new(FeatureHasGuard),
                                                )),
                                                Box::new(Literal(0.09350729)),
                                            )),
                                        )),
                                    )),
                                    Box::new(OperatorAdd(
                                        Box::new(Literal(0.09350729)),
                                        Box::new(FeatureHasWard),
                                    )),
                                )),
                                Box::new(FeatureHasWard),
                            )),
                        )),
                        Box::new(OperatorAdd(
                            Box::new(OperatorAdd(
                                Box::new(FeatureHasGuard),
                                Box::new(OperatorAdd(
                                    Box::new(FeatureHasLethal),
                                    Box::new(OperatorAdd(
                                        Box::new(Literal(0.09350729)),
                                        Box::new(OperatorAdd(
                                            Box::new(FeatureHasWard),
                                            Box::new(FeatureHasCharge),
                                        )),
                                    )),
                                )),
                            )),
                            Box::new(FeatureHasLethal),
                        )),
                    )),
                    Box::new(OperatorAdd(
                        Box::new(FeatureHasGuard),
                        Box::new(OperatorAdd(
                            Box::new(FeatureHasWard),
                            Box::new(OperatorAdd(
                                Box::new(OperatorAdd(
                                    Box::new(OperatorAdd(
                                        Box::new(FeatureHasWard),
                                        Box::new(OperatorAdd(
                                            Box::new(FeatureHasLethal),
                                            Box::new(FeatureHasLethal),
                                        )),
                                    )),
                                    Box::new(OperatorAdd(
                                        Box::new(OperatorAdd(
                                            Box::new(FeatureHasGuard),
                                            Box::new(OperatorAdd(
                                                Box::new(FeatureHasLethal),
                                                Box::new(OperatorAdd(
                                                    Box::new(Literal(0.09350729)),
                                                    Box::new(OperatorAdd(
                                                        Box::new(FeatureHasWard),
                                                        Box::new(FeatureHasCharge),
                                                    )),
                                                )),
                                            )),
                                        )),
                                        Box::new(FeatureHasLethal),
                                    )),
                                )),
                                Box::new(FeatureHasLethal),
                            )),
                        )),
                    )),
                )
            },
            state_node: {
                use binarytree::StateNode::*;
                FeatureOpNextTurnDraw
            },
        }),
        Some("Linear-baseline-1") => play(linear::LinearIndividual {
            weights: [
                -0.9914408,
                0.48191237,
                0.27632642,
                0.49518847,
                -0.88672733,
                0.2417996,
                -0.18142676,
                0.29621196,
                -0.99890447,
                -0.090878725,
                -0.5726924,
                0.2008555,
                0.7538433,
                -0.9968109,
                -0.3569255,
                0.41354895,
                0.7779305,
                0.98392034,
                -0.86545444,
                -0.804219,
            ],
        }),
        Some("Linear-baseline-2") => play(linear::LinearIndividual {
            weights: [
                -0.9268501,
                0.465621,
                0.30171847,
                0.3396914,
                -0.56572056,
                0.5510144,
                -0.6808655,
                -0.3581078,
                -0.8693981,
                0.2826562,
                0.26644683,
                0.34619927,
                0.5186608,
                -0.5469911,
                -0.68822503,
                0.2625761,
                0.64611006,
                0.8412905,
                -0.665977,
                -0.33358788,
            ],
        }),
        Some("Linear-baseline-4") => play(linear::LinearIndividual {
            weights: [
                -0.9924607,
                -0.07412481,
                0.310719,
                -0.022636175,
                -0.8256254,
                0.49253726,
                -0.88705206,
                0.5804422,
                -0.5688572,
                0.897243,
                0.955076,
                0.070161104,
                0.27413988,
                -0.29707742,
                -0.91536474,
                0.19773746,
                0.82912445,
                0.62041473,
                -0.03225708,
                -0.6935835,
            ],
        }),
        Some("Linear-baseline-5") => play(linear::LinearIndividual {
            weights: [
                -0.91266084,
                -0.19417644,
                0.595911,
                0.84301996,
                -0.6300826,
                0.82299304,
                0.119294405,
                0.6808765,
                -0.6821277,
                -0.28616643,
                0.6218264,
                0.373106,
                0.45804405,
                -0.6144929,
                -0.7217703,
                0.65779424,
                0.9859097,
                0.80655646,
                -0.693913,
                -0.5341661,
            ],
        }),
        Some("Linear-frombest-1") => play(linear::LinearIndividual {
            weights: [
                -0.7495322,
                0.1279583,
                0.47800398,
                -0.7440007,
                -0.53148794,
                0.34050536,
                -0.07757878,
                -0.9616492,
                -0.1776681,
                0.7470195,
                0.5324547,
                -0.93877745,
                0.16838288,
                -0.046010017,
                -0.46574116,
                -0.21833014,
                0.9295049,
                0.7927754,
                0.0729146,
                0.66085243,
            ],
        }),
        Some("Linear-frombest-2") => play(linear::LinearIndividual {
            weights: [
                -0.6183841,
                -0.42042637,
                0.5747731,
                -0.30233216,
                -0.4006772,
                -0.9306209,
                0.30638337,
                -0.9708252,
                -0.2788844,
                0.3583603,
                0.5066242,
                -0.007246256,
                0.24404073,
                0.047723055,
                -0.4432273,
                -0.31782317,
                0.8450155,
                0.82757354,
                0.8028593,
                0.6857898,
            ],
        }),
        Some("Linear-frombest-3") => play(linear::LinearIndividual {
            weights: [
                -0.0661695,
                0.5997577,
                0.5333538,
                -0.8657551,
                -0.88595057,
                -0.7980411,
                -0.30587912,
                -0.20585442,
                -0.022340775,
                -0.12919307,
                0.9883442,
                0.12560439,
                0.2897725,
                0.059717655,
                0.0092766285,
                0.0105896,
                0.9258003,
                0.7907591,
                0.8126998,
                0.5651901,
            ],
        }),
        Some("Linear-frombest-4") => play(linear::LinearIndividual {
            weights: [
                -0.6846416,
                0.330662,
                0.182554,
                0.6485925,
                -0.63315296,
                -0.57602143,
                0.20733213,
                0.44430614,
                -0.16679025,
                0.5414133,
                0.8380289,
                -0.31793427,
                0.2985065,
                -0.11319947,
                0.22750163,
                -0.13576674,
                0.9521904,
                0.9914582,
                0.9590087,
                0.93824744,
            ],
        }),
        Some("Linear-frombest-5") => play(linear::LinearIndividual {
            weights: [
                -0.33056068,
                0.5577786,
                0.28601527,
                -0.48330522,
                -0.29995131,
                0.5889578,
                -0.7547457,
                -0.6267164,
                -0.3841455,
                0.26617622,
                0.6943009,
                0.1379013,
                0.8374431,
                -0.110625505,
                0.45397615,
                -0.7913523,
                0.88636374,
                0.9751437,
                0.94349647,
                0.7093625,
            ],
        }),
        Some("Linear-standard-1") => play(linear::LinearIndividual {
            weights: [
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
        }),
        Some("Linear-standard-2") => play(linear::LinearIndividual {
            weights: [
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
        }),
        Some("Linear-standard-3") => play(linear::LinearIndividual {
            weights: [
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
        }),
        Some("Linear-standard-4") => play(linear::LinearIndividual {
            weights: [
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
        }),
        Some("Linear-standard-5") => play(linear::LinearIndividual {
            weights: [
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
        }),
        Some("Tree-baseline-1") => play(tree::TreeIndividual {
            card_node: {
                use tree::CardNode::*;
                OperatorMax(vec![
                    FeatureHasDrain,
                    OperatorMul(vec![
                        FeatureHasDrain,
                        FeatureAttack,
                        OperatorNeg(Box::new(OperatorMin(vec![
                            FeatureHasLethal,
                            OperatorNeg(Box::new(FeatureAttack)),
                            FeatureHasBreakthrough,
                        ]))),
                    ]),
                    Literal(0.6839812),
                ])
            },
            state_node: {
                use tree::StateNode::*;
                FeatureOpDecksize
            },
        }),
        Some("Tree-baseline-2") => play(tree::TreeIndividual {
            card_node: {
                use tree::CardNode::*;
                OperatorAdd(vec![
                    FeatureHasLethal,
                    OperatorMin(vec![
                        OperatorNeg(Box::new(OperatorMax(vec![
                            OperatorNeg(Box::new(FeatureHasBreakthrough)),
                            OperatorMax(vec![
                                FeatureDefense,
                                FeatureHasLethal,
                                FeatureHasBreakthrough,
                            ]),
                            OperatorMin(vec![FeatureHasGuard, FeatureHasCharge]),
                        ]))),
                        FeatureDefense,
                        Literal(-0.7795334),
                    ]),
                    OperatorMul(vec![
                        OperatorAdd(vec![
                            FeatureHasLethal,
                            FeatureAttack,
                            FeatureAttack,
                            OperatorMul(vec![
                                FeatureHasLethal,
                                OperatorAdd(vec![
                                    FeatureDefense,
                                    OperatorAdd(vec![
                                        FeatureDefense,
                                        OperatorAdd(vec![
                                            FeatureDefense,
                                            FeatureHasCharge,
                                            FeatureHasLethal,
                                            FeatureHasDrain,
                                        ]),
                                        FeatureAttack,
                                        OperatorMin(vec![
                                            OperatorNeg(Box::new(OperatorMul(vec![
                                                OperatorAdd(vec![
                                                    FeatureAttack,
                                                    OperatorAdd(vec![
                                                        FeatureDefense,
                                                        FeatureDefense,
                                                        FeatureHasLethal,
                                                        FeatureAttack,
                                                    ]),
                                                    FeatureDefense,
                                                    FeatureHasDrain,
                                                ]),
                                                FeatureAttack,
                                                FeatureAttack,
                                                FeatureHasCharge,
                                            ]))),
                                            FeatureDefense,
                                            Literal(-0.7795334),
                                        ]),
                                    ]),
                                    FeatureHasLethal,
                                    FeatureAttack,
                                ]),
                                FeatureAttack,
                                FeatureHasCharge,
                            ]),
                        ]),
                        FeatureAttack,
                        FeatureAttack,
                        FeatureHasDrain,
                    ]),
                    FeatureAttack,
                ])
            },
            state_node: {
                use tree::StateNode::*;
                FeatureOpNextTurnDraw
            },
        }),
        Some("Tree-baseline-3") => play(tree::TreeIndividual {
            card_node: {
                use tree::CardNode::*;
                OperatorAdd(vec![
                    FeatureHasDrain,
                    OperatorMul(vec![
                        OperatorMul(vec![
                            OperatorMul(vec![FeatureHasDrain, FeatureAttack]),
                            FeatureAttack,
                        ]),
                        OperatorMax(vec![FeatureAttack, FeatureAttack, FeatureHasDrain]),
                    ]),
                    OperatorMul(vec![
                        OperatorMul(vec![FeatureHasBreakthrough, Literal(-0.8113849)]),
                        FeatureAttack,
                    ]),
                    OperatorMax(vec![
                        Literal(-0.8113849),
                        FeatureAttack,
                        FeatureHasLethal,
                        FeatureAttack,
                    ]),
                ])
            },
            state_node: {
                use tree::StateNode::*;
                FeatureMeNextTurnDraw
            },
        }),
        Some("Tree-baseline-4") => play(tree::TreeIndividual {
            card_node: {
                use tree::CardNode::*;
                OperatorMax(vec![OperatorMax(vec![FeatureAttack, Literal(0.7104695), FeatureHasWard, OperatorAdd(vec![FeatureHasLethal, OperatorAdd(vec![OperatorMax(vec![FeatureHasDrain, Literal(0.7104695), FeatureHasWard, OperatorMax(vec![FeatureHasCharge, OperatorMax(vec![OperatorMax(vec![OperatorAdd(vec![FeatureHasLethal, OperatorAdd(vec![FeatureHasGuard, OperatorMul(vec![FeatureHasDrain, FeatureAttack, OperatorMax(vec![OperatorMax(vec![FeatureHasDrain, Literal(0.7104695), FeatureHasWard, OperatorMax(vec![FeatureHasDrain, Literal(0.7104695), FeatureHasWard, OperatorMax(vec![OperatorNeg(Box::new(OperatorMax(vec![FeatureHasGuard, FeatureHasGuard]))), OperatorMul(vec![FeatureAttack, OperatorMax(vec![OperatorMax(vec![FeatureHasDrain, OperatorMax(vec![FeatureHasDrain, OperatorMin(vec![FeatureHasWard, FeatureHasGuard]), FeatureHasWard, OperatorMul(vec![FeatureHasGuard, FeatureAttack, FeatureHasDrain])]), FeatureHasLethal, OperatorAdd(vec![OperatorMax(vec![FeatureHasDrain, Literal(0.7104695), FeatureHasWard, OperatorMax(vec![OperatorMax(vec![OperatorMax(vec![FeatureAttack, OperatorMax(vec![OperatorMax(vec![OperatorNeg(Box::new(FeatureHasGuard)), OperatorMul(vec![OperatorMax(vec![Literal(0.18378186), FeatureHasGuard]), FeatureHasLethal]), FeatureAttack]), FeatureHasDrain])]), Literal(0.7104695), FeatureHasWard, FeatureHasLethal]), OperatorMax(vec![OperatorMax(vec![FeatureHasDrain, Literal(0.7104695), FeatureHasWard, OperatorAdd(vec![FeatureHasLethal, OperatorAdd(vec![FeatureAttack, OperatorMul(vec![FeatureHasDrain, OperatorMul(vec![FeatureAttack, FeatureAttack]), OperatorMax(vec![OperatorMax(vec![FeatureHasDrain, Literal(0.7104695), FeatureHasWard, OperatorMax(vec![FeatureHasDrain, Literal(0.7104695), OperatorMax(vec![FeatureHasDrain, Literal(0.7104695), FeatureHasWard, FeatureHasLethal]), OperatorMax(vec![OperatorNeg(Box::new(OperatorMax(vec![FeatureHasGuard, FeatureHasGuard]))), OperatorMul(vec![FeatureAttack, OperatorMax(vec![FeatureHasDrain, FeatureHasGuard])]), FeatureAttack])])]), OperatorMax(vec![FeatureHasDrain, FeatureAttack])])]), FeatureAttack, FeatureHasDrain])])]), FeatureHasWard]), FeatureAttack])]), FeatureHasGuard])]), FeatureHasGuard])]), FeatureAttack])])]), OperatorMax(vec![FeatureHasDrain, FeatureHasGuard])])]), FeatureAttack, FeatureHasDrain])]), Literal(0.7104695), FeatureHasDrain, FeatureHasWard]), FeatureAttack]), FeatureAttack])]), OperatorMul(vec![FeatureHasDrain, FeatureAttack, OperatorMax(vec![OperatorMax(vec![FeatureHasDrain, Literal(0.7104695), FeatureHasWard, OperatorMax(vec![FeatureHasDrain, Literal(0.7104695), FeatureHasWard, OperatorMax(vec![FeatureHasDrain, Literal(0.7104695), FeatureHasWard, FeatureHasDrain])])]), OperatorMax(vec![FeatureHasWard, OperatorAdd(vec![OperatorMax(vec![FeatureHasDrain, OperatorMax(vec![FeatureHasWard, FeatureHasGuard]), Literal(0.7104695), OperatorMax(vec![Literal(0.7104695), FeatureHasDrain])]), OperatorMul(vec![OperatorMul(vec![OperatorMax(vec![FeatureHasLethal, FeatureHasDrain]), FeatureAttack]), OperatorMax(vec![FeatureHasDrain, FeatureHasGuard, FeatureHasWard, FeatureAttack]), OperatorMax(vec![FeatureHasDrain, FeatureAttack, FeatureHasDrain])]), FeatureHasCharge, FeatureHasDrain])])])]), OperatorMax(vec![FeatureAttack, OperatorMax(vec![OperatorMax(vec![OperatorNeg(Box::new(FeatureHasGuard)), OperatorMul(vec![OperatorMax(vec![Literal(0.18378186), FeatureHasGuard]), FeatureHasLethal]), FeatureAttack]), FeatureHasDrain])]), FeatureHasDrain])])]), FeatureAttack])
            },
            state_node: {
                use tree::StateNode::*;
                FeatureOpNextTurnDraw
            },
        }),
        Some("Tree-baseline-5") => play(tree::TreeIndividual {
            card_node: {
                use tree::CardNode::*;
                OperatorMin(vec![
                    FeatureAttack,
                    OperatorAdd(vec![
                        OperatorMin(vec![
                            FeatureAttack,
                            OperatorMin(vec![
                                OperatorMin(vec![FeatureAttack, FeatureAttack]),
                                OperatorAdd(vec![
                                    OperatorAdd(vec![
                                        FeatureHasDrain,
                                        OperatorMin(vec![
                                            OperatorMin(vec![
                                                OperatorAdd(vec![
                                                    FeatureAttack,
                                                    OperatorMin(vec![
                                                        FeatureAttack,
                                                        OperatorAdd(vec![
                                                            FeatureHasDrain,
                                                            Literal(0.70448303),
                                                        ]),
                                                    ]),
                                                ]),
                                                OperatorAdd(vec![
                                                    FeatureHasDrain,
                                                    OperatorMin(vec![
                                                        FeatureAttack,
                                                        Literal(0.70448303),
                                                    ]),
                                                ]),
                                            ]),
                                            FeatureAttack,
                                        ]),
                                    ]),
                                    FeatureHasDrain,
                                ]),
                            ]),
                        ]),
                        FeatureHasDrain,
                    ]),
                ])
            },
            state_node: {
                use tree::StateNode::*;
                FeatureMeHealth
            },
        }),
        Some("Tree-frombest-1") => play(tree::TreeIndividual {
            card_node: {
                use tree::CardNode::*;
                OperatorMin(vec![
                    Literal(0.5360143),
                    OperatorMax(vec![
                        OperatorMax(vec![
                            OperatorMax(vec![
                                Literal(-0.99617505),
                                FeatureHasDrain,
                                FeatureAttack,
                                FeatureAttack,
                            ]),
                            FeatureHasCharge,
                            FeatureHasDrain,
                        ]),
                        OperatorMax(vec![
                            Literal(-0.99617505),
                            FeatureHasDrain,
                            Literal(-0.99617505),
                            OperatorMax(vec![
                                OperatorMax(vec![
                                    Literal(-0.99617505),
                                    FeatureHasDrain,
                                    FeatureAttack,
                                    FeatureHasCharge,
                                ]),
                                FeatureHasDrain,
                                OperatorMin(vec![
                                    FeatureHasLethal,
                                    FeatureHasCharge,
                                    OperatorAdd(vec![
                                        OperatorMax(vec![
                                            Literal(-0.99617505),
                                            Literal(0.93088746),
                                            OperatorNeg(Box::new(FeatureHasDrain)),
                                        ]),
                                        OperatorAdd(vec![
                                            Literal(0.5360143),
                                            OperatorMax(vec![
                                                FeatureAttack,
                                                OperatorMin(vec![
                                                    Literal(-0.5005424),
                                                    OperatorNeg(Box::new(OperatorMax(vec![
                                                        Literal(-0.99617505),
                                                        FeatureHasDrain,
                                                        FeatureAttack,
                                                        FeatureAttack,
                                                    ]))),
                                                ]),
                                            ]),
                                        ]),
                                        FeatureHasLethal,
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ])
            },
            state_node: {
                use tree::StateNode::*;
                OperatorMin(vec![OperatorAdd(vec![OperatorNeg(Box::new(FeatureMeCurrentMana)), OperatorNeg(Box::new(OperatorAdd(vec![FeatureMeMaxMana, FeatureOpHealth])))]), FeatureOpHealth, OperatorAdd(vec![OperatorNeg(Box::new(OperatorNeg(Box::new(OperatorAdd(vec![FeatureMeMaxMana, OperatorMin(vec![OperatorAdd(vec![OperatorAdd(vec![OperatorMin(vec![FeatureMeRune, FeatureMeDecksize]), OperatorMin(vec![FeatureMeRune, FeatureMeDecksize])]), OperatorNeg(Box::new(OperatorMin(vec![OperatorAdd(vec![OperatorNeg(Box::new(FeatureMeCurrentMana)), OperatorNeg(Box::new(OperatorAdd(vec![OperatorAdd(vec![OperatorNeg(Box::new(FeatureMeCurrentMana)), OperatorNeg(Box::new(OperatorAdd(vec![FeatureMeMaxMana, FeatureOpHealth])))]), FeatureOpHealth])))]), OperatorNeg(Box::new(FeatureMeCurrentMana)), OperatorMin(vec![OperatorNeg(Box::new(OperatorAdd(vec![FeatureMeMaxMana, OperatorMin(vec![OperatorAdd(vec![OperatorAdd(vec![OperatorMin(vec![FeatureMeRune, FeatureMeDecksize]), OperatorMin(vec![FeatureMeRune, FeatureMeDecksize])]), OperatorNeg(Box::new(OperatorMin(vec![OperatorAdd(vec![OperatorNeg(Box::new(FeatureMeCurrentMana)), OperatorNeg(Box::new(OperatorAdd(vec![OperatorNeg(Box::new(FeatureMeCurrentMana)), OperatorNeg(Box::new(OperatorAdd(vec![OperatorAdd(vec![OperatorNeg(Box::new(FeatureMeCurrentMana)), OperatorNeg(Box::new(OperatorAdd(vec![FeatureMeMaxMana, FeatureOpHealth])))]), FeatureOpHealth])))])))]), OperatorNeg(Box::new(FeatureMeCurrentMana)), OperatorMin(vec![OperatorAdd(vec![OperatorMin(vec![OperatorAdd(vec![OperatorNeg(Box::new(FeatureMeCurrentMana)), OperatorNeg(Box::new(OperatorAdd(vec![OperatorMin(vec![FeatureMeRune, FeatureMeDecksize]), OperatorMin(vec![FeatureMeRune, FeatureMeDecksize])])))]), FeatureOpHealth, FeatureMeCurrentMana]), OperatorNeg(Box::new(FeatureOpHealth))]), FeatureOpHealth, FeatureOpRune])])))]), FeatureMeCurrentMana, OperatorAdd(vec![FeatureMeDecksize, FeatureMeDecksize])])]))), FeatureOpHealth, OperatorAdd(vec![OperatorMin(vec![OperatorAdd(vec![OperatorNeg(Box::new(FeatureMeCurrentMana)), OperatorNeg(Box::new(OperatorAdd(vec![OperatorAdd(vec![OperatorNeg(Box::new(FeatureMeCurrentMana)), OperatorNeg(Box::new(OperatorAdd(vec![FeatureMeMaxMana, FeatureOpHealth])))]), FeatureOpHealth])))]), OperatorNeg(Box::new(FeatureMeCurrentMana)), OperatorMin(vec![OperatorAdd(vec![OperatorMin(vec![OperatorAdd(vec![OperatorNeg(Box::new(FeatureMeCurrentMana)), OperatorNeg(Box::new(OperatorAdd(vec![OperatorMin(vec![FeatureMeRune, FeatureMeDecksize]), OperatorNeg(Box::new(FeatureOpNextTurnDraw))])))]), FeatureMeMaxMana, FeatureMeCurrentMana]), OperatorNeg(Box::new(OperatorAdd(vec![FeatureMeMaxMana, FeatureOpHealth])))]), FeatureOpHealth, FeatureOpRune])]), FeatureOpHealth])])])))]), FeatureMeCurrentMana, OperatorAdd(vec![FeatureMeDecksize, FeatureMeDecksize])])]))))), OperatorNeg(Box::new(FeatureMeCurrentMana))])])
            },
        }),
        Some("Tree-frombest-2") => play(tree::TreeIndividual {
            card_node: {
                use tree::CardNode::*;
                OperatorMax(vec![
                    FeatureAttack,
                    OperatorMax(vec![
                        OperatorMul(vec![
                            FeatureHasLethal,
                            OperatorMax(vec![
                                OperatorAdd(vec![
                                    OperatorMax(vec![
                                        FeatureHasCharge,
                                        FeatureAttack,
                                        FeatureDefense,
                                    ]),
                                    FeatureAttack,
                                    FeatureHasCharge,
                                ]),
                                FeatureAttack,
                                FeatureAttack,
                            ]),
                        ]),
                        OperatorAdd(vec![
                            Literal(-0.89339733),
                            OperatorMul(vec![
                                FeatureDefense,
                                OperatorMax(vec![
                                    OperatorAdd(vec![
                                        OperatorMax(vec![
                                            FeatureAttack,
                                            OperatorMax(vec![
                                                OperatorMul(vec![
                                                    FeatureHasLethal,
                                                    OperatorMax(vec![
                                                        OperatorAdd(vec![
                                                            OperatorMax(vec![
                                                                FeatureHasCharge,
                                                                OperatorMax(vec![
                                                                    FeatureAttack,
                                                                    FeatureHasBreakthrough,
                                                                ]),
                                                                FeatureDefense,
                                                            ]),
                                                            FeatureHasWard,
                                                            FeatureHasCharge,
                                                        ]),
                                                        FeatureHasBreakthrough,
                                                        FeatureAttack,
                                                    ]),
                                                ]),
                                                OperatorAdd(vec![
                                                    FeatureHasLethal,
                                                    OperatorMax(vec![FeatureAttack, FeatureAttack]),
                                                ]),
                                            ]),
                                        ]),
                                        FeatureHasWard,
                                        FeatureHasCharge,
                                    ]),
                                    FeatureHasLethal,
                                    FeatureAttack,
                                ]),
                                FeatureDefense,
                                FeatureHasGuard,
                            ]),
                        ]),
                    ]),
                ])
            },
            state_node: {
                use tree::StateNode::*;
                OperatorNeg(Box::new(OperatorAdd(vec![
                    FeatureOpHealth,
                    OperatorMul(vec![
                        FeatureMeCurrentMana,
                        FeatureOpMaxMana,
                        FeatureOpDecksize,
                    ]),
                    OperatorNeg(Box::new(OperatorNeg(Box::new(FeatureMeCurrentMana)))),
                ])))
            },
        }),
        Some("Tree-frombest-3") => play(tree::TreeIndividual {
            card_node: {
                use tree::CardNode::*;
                OperatorMax(vec![
                    FeatureHasWard,
                    OperatorAdd(vec![
                        OperatorAdd(vec![
                            OperatorAdd(vec![FeatureHasWard, FeatureAttack]),
                            FeatureHasGuard,
                            FeatureHasWard,
                            FeatureHasWard,
                        ]),
                        FeatureHasBreakthrough,
                        OperatorAdd(vec![FeatureHasLethal, FeatureHasGuard]),
                        OperatorMax(vec![
                            FeatureHasDrain,
                            FeatureHasGuard,
                            OperatorNeg(Box::new(OperatorMax(vec![
                                OperatorNeg(Box::new(FeatureHasLethal)),
                                OperatorAdd(vec![FeatureHasWard, FeatureHasDrain]),
                            ]))),
                            FeatureHasDrain,
                        ]),
                    ]),
                    Literal(0.6180668),
                ])
            },
            state_node: {
                use tree::StateNode::*;
                OperatorMin(vec![
                    FeatureOpNextTurnDraw,
                    FeatureOpNextTurnDraw,
                    FeatureMeMaxMana,
                    FeatureMeMaxMana,
                ])
            },
        }),
        Some("Tree-frombest-4") => play(tree::TreeIndividual {
            card_node: {
                use tree::CardNode::*;
                OperatorMax(vec![
                    OperatorAdd(vec![
                        FeatureHasLethal,
                        FeatureHasLethal,
                        FeatureHasWard,
                        OperatorAdd(vec![
                            OperatorAdd(vec![FeatureHasWard, FeatureHasDrain]),
                            OperatorAdd(vec![
                                OperatorAdd(vec![
                                    FeatureHasLethal,
                                    OperatorMax(vec![
                                        OperatorAdd(vec![FeatureHasLethal, FeatureHasDrain]),
                                        FeatureAttack,
                                        OperatorAdd(vec![FeatureHasLethal, FeatureHasDrain]),
                                    ]),
                                    FeatureHasWard,
                                    OperatorAdd(vec![
                                        OperatorAdd(vec![FeatureHasLethal, FeatureHasWard]),
                                        FeatureDefense,
                                    ]),
                                ]),
                                FeatureHasWard,
                            ]),
                        ]),
                    ]),
                    FeatureHasWard,
                    FeatureHasWard,
                ])
            },
            state_node: {
                use tree::StateNode::*;
                FeatureOpNextTurnDraw
            },
        }),
        Some("Tree-frombest-5") => play(tree::TreeIndividual {
            card_node: {
                use tree::CardNode::*;
                OperatorAdd(vec![
                    OperatorMax(vec![
                        FeatureAttack,
                        OperatorAdd(vec![
                            OperatorMax(vec![FeatureHasLethal, FeatureAttack]),
                            FeatureHasLethal,
                        ]),
                    ]),
                    OperatorMul(vec![
                        FeatureHasGuard,
                        OperatorMax(vec![FeatureAttack, FeatureAttack]),
                    ]),
                ])
            },
            state_node: {
                use tree::StateNode::*;
                OperatorNeg(Box::new(OperatorMin(vec![
                    OperatorMax(vec![
                        FeatureMeNextTurnDraw,
                        OperatorMin(vec![
                            OperatorNeg(Box::new(OperatorMin(vec![
                                OperatorMul(vec![FeatureMeMaxMana, FeatureOpHealth]),
                                OperatorNeg(Box::new(FeatureMeRune)),
                            ]))),
                            FeatureOpHealth,
                        ]),
                        OperatorMax(vec![
                            FeatureMeNextTurnDraw,
                            FeatureMeCurrentMana,
                            FeatureMeCurrentMana,
                            OperatorAdd(vec![
                                OperatorAdd(vec![
                                    OperatorMin(vec![FeatureOpDecksize, FeatureOpDecksize]),
                                    FeatureMeMaxMana,
                                ]),
                                OperatorAdd(vec![
                                    FeatureOpNextTurnDraw,
                                    OperatorMin(vec![
                                        OperatorAdd(vec![
                                            OperatorMin(vec![
                                                FeatureMeCurrentMana,
                                                FeatureMeNextTurnDraw,
                                            ]),
                                            FeatureMeMaxMana,
                                        ]),
                                        FeatureMeDecksize,
                                        FeatureMeCurrentMana,
                                    ]),
                                ]),
                                Literal(0.87255025),
                            ]),
                        ]),
                        OperatorAdd(vec![
                            OperatorAdd(vec![
                                OperatorMin(vec![FeatureOpDecksize, FeatureOpDecksize]),
                                FeatureMeMaxMana,
                            ]),
                            OperatorAdd(vec![
                                FeatureOpNextTurnDraw,
                                OperatorMin(vec![
                                    Literal(-0.14474416),
                                    FeatureMeDecksize,
                                    FeatureOpHealth,
                                ]),
                            ]),
                            OperatorMin(vec![Literal(-0.14474416), FeatureOpHealth]),
                        ]),
                    ]),
                    OperatorMin(vec![
                        OperatorMax(vec![
                            FeatureMeNextTurnDraw,
                            OperatorMin(vec![
                                OperatorMin(vec![FeatureOpDecksize, FeatureOpDecksize]),
                                FeatureOpHealth,
                            ]),
                            FeatureMeCurrentMana,
                            OperatorMin(vec![
                                OperatorMax(vec![
                                    FeatureMeNextTurnDraw,
                                    FeatureMeCurrentMana,
                                    FeatureMeCurrentMana,
                                    OperatorAdd(vec![
                                        OperatorAdd(vec![
                                            OperatorMin(vec![FeatureOpDecksize, FeatureOpDecksize]),
                                            FeatureMeMaxMana,
                                        ]),
                                        FeatureOpHealth,
                                        Literal(0.87255025),
                                    ]),
                                ]),
                                FeatureOpHealth,
                            ]),
                        ]),
                        FeatureOpHealth,
                    ]),
                ])))
            },
        }),
        Some("Tree-standard-1") => play(tree::TreeIndividual {
            card_node: {
                use tree::CardNode::*;
                OperatorAdd(vec![
                    FeatureHasWard,
                    FeatureHasLethal,
                    OperatorMax(vec![
                        FeatureHasWard,
                        FeatureHasWard,
                        OperatorAdd(vec![
                            FeatureHasWard,
                            OperatorMax(vec![
                                FeatureHasGuard,
                                FeatureHasWard,
                                OperatorMax(vec![
                                    FeatureAttack,
                                    OperatorAdd(vec![
                                        FeatureHasWard,
                                        FeatureAttack,
                                        OperatorAdd(vec![
                                            FeatureHasWard,
                                            FeatureHasGuard,
                                            FeatureHasGuard,
                                        ]),
                                    ]),
                                    FeatureAttack,
                                    FeatureAttack,
                                ]),
                                FeatureAttack,
                            ]),
                            FeatureHasGuard,
                        ]),
                        OperatorMax(vec![
                            OperatorMin(vec![FeatureAttack, FeatureAttack]),
                            FeatureHasWard,
                        ]),
                    ]),
                ])
            },
            state_node: {
                use tree::StateNode::*;
                FeatureOpNextTurnDraw
            },
        }),
        Some("Tree-standard-2") => play(tree::TreeIndividual {
            card_node: {
                use tree::CardNode::*;
                OperatorAdd(vec![
                    FeatureHasLethal,
                    FeatureHasWard,
                    OperatorAdd(vec![
                        OperatorAdd(vec![FeatureAttack, FeatureHasWard]),
                        OperatorMul(vec![
                            OperatorAdd(vec![
                                FeatureHasGuard,
                                FeatureHasWard,
                                OperatorAdd(vec![
                                    FeatureHasLethal,
                                    OperatorMul(vec![
                                        FeatureHasGuard,
                                        OperatorMax(vec![
                                            FeatureHasGuard,
                                            OperatorMin(vec![
                                                FeatureHasWard,
                                                FeatureAttack,
                                                OperatorMul(vec![
                                                    OperatorMax(vec![
                                                        OperatorAdd(vec![
                                                            FeatureHasDrain,
                                                            FeatureHasDrain,
                                                        ]),
                                                        OperatorAdd(vec![
                                                            FeatureAttack,
                                                            Literal(0.19453096),
                                                        ]),
                                                    ]),
                                                    OperatorMax(vec![
                                                        FeatureHasGuard,
                                                        OperatorMin(vec![
                                                            FeatureAttack,
                                                            FeatureHasGuard,
                                                            FeatureHasGuard,
                                                            OperatorMax(vec![
                                                                FeatureHasGuard,
                                                                FeatureHasLethal,
                                                            ]),
                                                        ]),
                                                    ]),
                                                ]),
                                                OperatorMax(vec![
                                                    FeatureHasGuard,
                                                    OperatorMin(vec![
                                                        FeatureHasGuard,
                                                        OperatorMax(vec![
                                                            FeatureHasGuard,
                                                            OperatorMul(vec![
                                                                FeatureHasGuard,
                                                                OperatorNeg(Box::new(
                                                                    FeatureHasBreakthrough,
                                                                )),
                                                                FeatureDefense,
                                                            ]),
                                                        ]),
                                                        OperatorMin(vec![
                                                            FeatureAttack,
                                                            FeatureHasGuard,
                                                        ]),
                                                        OperatorAdd(vec![
                                                            FeatureAttack,
                                                            FeatureHasWard,
                                                        ]),
                                                    ]),
                                                ]),
                                            ]),
                                        ]),
                                    ]),
                                    OperatorMax(vec![
                                        FeatureHasGuard,
                                        OperatorMin(vec![
                                            FeatureHasGuard,
                                            OperatorMax(vec![
                                                FeatureHasGuard,
                                                FeatureHasBreakthrough,
                                            ]),
                                            OperatorMin(vec![FeatureAttack, FeatureHasGuard]),
                                            FeatureHasGuard,
                                        ]),
                                    ]),
                                    OperatorMul(vec![
                                        OperatorMin(vec![
                                            FeatureHasWard,
                                            FeatureAttack,
                                            OperatorMul(vec![
                                                OperatorAdd(vec![FeatureAttack, FeatureHasWard]),
                                                OperatorMax(vec![
                                                    FeatureHasGuard,
                                                    OperatorMin(vec![
                                                        FeatureHasWard,
                                                        FeatureHasGuard,
                                                        FeatureHasGuard,
                                                        OperatorMax(vec![
                                                            FeatureHasWard,
                                                            FeatureHasGuard,
                                                        ]),
                                                    ]),
                                                ]),
                                            ]),
                                            OperatorMax(vec![
                                                FeatureHasGuard,
                                                FeatureHasBreakthrough,
                                            ]),
                                        ]),
                                        FeatureHasGuard,
                                    ]),
                                ]),
                            ]),
                            OperatorMax(vec![FeatureHasGuard, FeatureHasGuard]),
                        ]),
                        FeatureHasWard,
                        OperatorMul(vec![
                            OperatorMax(vec![FeatureHasLethal, FeatureHasDrain]),
                            FeatureDefense,
                        ]),
                    ]),
                ])
            },
            state_node: {
                use tree::StateNode::*;
                FeatureMeMaxMana
            },
        }),
        Some("Tree-standard-3") => play(tree::TreeIndividual {
            card_node: {
                use tree::CardNode::*;
                OperatorAdd(vec![
                    OperatorMax(vec![
                        Literal(0.9466922),
                        FeatureHasLethal,
                        Literal(0.04422593),
                    ]),
                    FeatureHasGuard,
                    FeatureHasWard,
                ])
            },
            state_node: {
                use tree::StateNode::*;
                FeatureOpNextTurnDraw
            },
        }),
        Some("Tree-standard-4") => play(tree::TreeIndividual {
            card_node: {
                use tree::CardNode::*;
                OperatorMax(vec![
                    OperatorAdd(vec![
                        OperatorAdd(vec![
                            OperatorAdd(vec![
                                FeatureHasWard,
                                OperatorAdd(vec![
                                    FeatureHasLethal,
                                    FeatureAttack,
                                    FeatureHasGuard,
                                    FeatureHasLethal,
                                ]),
                                OperatorAdd(vec![
                                    OperatorAdd(vec![
                                        OperatorAdd(vec![
                                            OperatorMax(vec![
                                                OperatorAdd(vec![FeatureHasWard, FeatureHasGuard]),
                                                FeatureHasDrain,
                                            ]),
                                            FeatureHasWard,
                                        ]),
                                        FeatureHasGuard,
                                    ]),
                                    OperatorMul(vec![
                                        FeatureHasLethal,
                                        OperatorAdd(vec![
                                            OperatorAdd(vec![
                                                FeatureHasLethal,
                                                FeatureAttack,
                                                FeatureHasGuard,
                                                FeatureHasLethal,
                                            ]),
                                            FeatureHasGuard,
                                        ]),
                                    ]),
                                ]),
                                FeatureHasLethal,
                            ]),
                            FeatureHasWard,
                            FeatureHasDrain,
                        ]),
                        OperatorAdd(vec![
                            FeatureHasWard,
                            FeatureAttack,
                            FeatureHasGuard,
                            FeatureHasWard,
                        ]),
                    ]),
                    FeatureAttack,
                ])
            },
            state_node: {
                use tree::StateNode::*;
                OperatorMin(vec![
                    FeatureOpNextTurnDraw,
                    OperatorMin(vec![
                        FeatureOpNextTurnDraw,
                        FeatureMeDecksize,
                        FeatureOpNextTurnDraw,
                    ]),
                    OperatorAdd(vec![FeatureMeRune, FeatureOpNextTurnDraw]),
                ])
            },
        }),
        Some("Tree-standard-5") => play(tree::TreeIndividual {
            card_node: {
                use tree::CardNode::*;
                OperatorAdd(vec![OperatorMul(vec![FeatureAttack, OperatorAdd(vec![FeatureHasLethal, OperatorMin(vec![OperatorAdd(vec![FeatureHasGuard, OperatorMin(vec![FeatureHasLethal, OperatorMin(vec![FeatureHasCharge, OperatorAdd(vec![FeatureHasGuard, OperatorMin(vec![FeatureHasLethal, OperatorMin(vec![FeatureHasCharge, OperatorMin(vec![OperatorMin(vec![FeatureHasCharge, OperatorNeg(Box::new(FeatureHasBreakthrough))]), FeatureHasWard, FeatureHasGuard]), OperatorMul(vec![OperatorMul(vec![Literal(-0.23851728), FeatureHasDrain]), OperatorMax(vec![FeatureHasDrain, FeatureHasDrain, OperatorMin(vec![OperatorAdd(vec![FeatureHasDrain, OperatorMul(vec![OperatorMul(vec![Literal(-0.23851728), OperatorAdd(vec![FeatureHasBreakthrough, OperatorNeg(Box::new(FeatureHasWard)), FeatureHasBreakthrough])]), FeatureHasDrain]), OperatorMin(vec![OperatorMin(vec![OperatorNeg(Box::new(FeatureHasCharge)), OperatorNeg(Box::new(FeatureHasCharge))]), FeatureHasBreakthrough, FeatureHasWard])]), Literal(0.18201971)])])]), OperatorMin(vec![OperatorAdd(vec![FeatureHasDrain, FeatureHasDrain, OperatorMin(vec![OperatorMin(vec![OperatorNeg(Box::new(FeatureHasCharge)), OperatorNeg(Box::new(FeatureHasCharge))]), FeatureHasBreakthrough, FeatureHasWard])]), Literal(0.18201971)])])]), OperatorMax(vec![FeatureHasDrain, FeatureHasGuard, Literal(-0.23851728)])]), OperatorMul(vec![OperatorMul(vec![Literal(-0.23851728), FeatureHasDrain]), OperatorMax(vec![FeatureHasDrain, FeatureHasDrain, Literal(-0.23851728)])]), OperatorMin(vec![OperatorAdd(vec![FeatureHasDrain, OperatorNeg(Box::new(FeatureHasCharge)), OperatorMin(vec![OperatorMin(vec![OperatorNeg(Box::new(FeatureHasCharge)), OperatorNeg(Box::new(FeatureHasCharge))]), FeatureHasBreakthrough, FeatureHasWard])]), Literal(0.18201971)])])]), OperatorMax(vec![FeatureHasDrain, FeatureHasDrain, Literal(-0.23851728)])]), FeatureHasWard])])]), FeatureAttack])
            },
            state_node: {
                use tree::StateNode::*;
                FeatureOpMaxMana
            },
        }),
        Some("Linear-from-Linear-standard-1-1") => play(linear::LinearIndividual {
            weights: [
                -0.68858814,
                -0.6736405,
                0.51877856,
                0.029143095,
                -0.718837,
                -0.25197935,
                0.33484173,
                0.42963266,
                -0.06964922,
                -0.7775893,
                0.82913494,
                0.02366805,
                0.13568974,
                0.012722731,
                0.24883318,
                -0.11198187,
                0.93497086,
                0.95310736,
                0.7168217,
                0.8466759,
            ],
        }),
        Some("Linear-from-Linear-standard-1-2") => play(linear::LinearIndividual {
            weights: [
                -0.68858814,
                -0.6805117,
                0.30891037,
                0.1468494,
                -0.718837,
                -0.24669266,
                0.26745796,
                0.8163147,
                -0.087534904,
                -0.9889746,
                0.9876697,
                -0.13525486,
                0.24386835,
                -0.07205725,
                -0.09459996,
                -0.20932746,
                0.93497086,
                0.95310736,
                0.7168217,
                0.5435598,
            ],
        }),
        Some("Linear-from-Linear-standard-2-1") => play(linear::LinearIndividual {
            weights: [
                -0.65507054,
                -0.64310455,
                0.6000421,
                0.50536203,
                -0.8440044,
                -0.39615107,
                -0.29476237,
                0.4031124,
                -0.005370617,
                0.5725136,
                0.7808652,
                -0.2824986,
                0.08753133,
                -0.057546377,
                0.2871089,
                -0.45562696,
                0.67786837,
                0.7077298,
                0.5996754,
                0.040987253,
            ],
        }),
        Some("Linear-from-Linear-standard-2-2") => play(linear::LinearIndividual {
            weights: [
                -0.7749758,
                0.1766727,
                0.4332714,
                -0.93413067,
                -0.9381685,
                -0.18167782,
                -0.03480935,
                0.95640945,
                -0.15176582,
                0.9446106,
                0.17656565,
                -0.24631643,
                0.20911837,
                -0.057546377,
                -0.13892889,
                -0.20521617,
                0.9566674,
                0.96502376,
                0.71799994,
                0.75043464,
            ],
        }),
        Some("Linear-from-Linear-standard-3-1") => play(linear::LinearIndividual {
            weights: [
                -0.74176145,
                0.67525864,
                0.35297656,
                0.960202,
                -0.43018126,
                -0.66867876,
                0.67419505,
                -0.7870426,
                -0.004044056,
                -0.33080053,
                0.68304515,
                -0.02224636,
                0.1632452,
                -0.030466557,
                -0.14713264,
                -0.4590733,
                0.13990092,
                0.8682606,
                0.6586063,
                0.3099084,
            ],
        }),
        Some("Linear-from-Linear-standard-3-2") => play(linear::LinearIndividual {
            weights: [
                -0.9301307,
                -0.028253078,
                0.35297656,
                0.28680372,
                -0.7573118,
                0.04791832,
                0.7328229,
                -0.6921339,
                -0.21709204,
                -0.039408445,
                0.28531528,
                -0.02224636,
                0.16987157,
                -0.13909411,
                -0.03137088,
                -0.34944868,
                0.8792534,
                0.9861734,
                0.44805026,
                0.13966012,
            ],
        }),
        Some("Linear-from-Linear-standard-4-1") => play(linear::LinearIndividual {
            weights: [
                -0.98439264,
                -0.09955621,
                0.2645619,
                -0.09480262,
                -0.54256535,
                -0.25891852,
                -0.29967093,
                -0.26591206,
                -0.028533459,
                -0.6463201,
                0.8479543,
                -0.38811827,
                0.19604897,
                -0.103866816,
                -0.06833005,
                -0.35816908,
                0.7943373,
                0.70167494,
                0.83034587,
                0.6951666,
            ],
        }),
        Some("Linear-from-Linear-standard-4-2") => play(linear::LinearIndividual {
            weights: [
                -0.44405913,
                -0.95776606,
                0.2573557,
                -0.23662591,
                -0.7230866,
                -0.66835594,
                -0.40907574,
                -0.5892334,
                -0.028533459,
                -0.79006886,
                0.16664529,
                -0.021817446,
                0.19604897,
                -0.019815683,
                -0.37218595,
                -0.21116996,
                0.55324316,
                0.7330961,
                0.37869644,
                0.9721358,
            ],
        }),
        Some("Tree-from-Linear-standard-1-1") => play(tree::TreeIndividual {
            card_node: {
                use tree::CardNode::*;
                OperatorAdd(vec![
                    FeatureHasLethal,
                    OperatorMul(vec![FeatureAttack, Literal(0.107727766)]),
                    OperatorAdd(vec![
                        OperatorMul(vec![FeatureAttack, Literal(0.107727766)]),
                        OperatorMul(vec![FeatureAttack, Literal(0.107727766)]),
                        OperatorMul(vec![FeatureHasDrain, Literal(-0.09459996)]),
                        OperatorMul(vec![Literal(0.7168217), FeatureHasLethal]),
                        OperatorMul(vec![Literal(0.93497086), Literal(0.93497086)]),
                        OperatorMul(vec![Literal(-0.09459996), Literal(0.95310736)]),
                        OperatorMul(vec![FeatureHasLethal, Literal(0.7168217)]),
                        OperatorMul(vec![
                            OperatorMul(vec![FeatureAttack, Literal(0.107727766)]),
                            Literal(0.93497086),
                        ]),
                    ]),
                    FeatureHasGuard,
                    OperatorMul(vec![
                        OperatorAdd(vec![
                            OperatorMul(vec![
                                FeatureAttack,
                                OperatorMul(vec![Literal(0.93497086), Literal(0.93497086)]),
                            ]),
                            OperatorMul(vec![FeatureAttack, Literal(0.107727766)]),
                            OperatorAdd(vec![
                                Literal(0.107727766),
                                OperatorMul(vec![FeatureAttack, Literal(0.107727766)]),
                                FeatureHasLethal,
                                FeatureHasGuard,
                                OperatorMul(vec![Literal(0.93497086), Literal(0.93497086)]),
                                FeatureHasLethal,
                                OperatorMul(vec![FeatureHasLethal, Literal(0.7168217)]),
                                OperatorMul(vec![
                                    OperatorMul(vec![FeatureHasDrain, Literal(0.107727766)]),
                                    OperatorMul(vec![FeatureAttack, Literal(0.107727766)]),
                                ]),
                            ]),
                            FeatureHasGuard,
                            OperatorMul(vec![
                                OperatorMul(vec![FeatureHasLethal, Literal(0.7168217)]),
                                OperatorMul(vec![Literal(0.93497086), Literal(0.93497086)]),
                            ]),
                            OperatorMul(vec![Literal(0.107727766), Literal(0.95310736)]),
                            OperatorMul(vec![FeatureHasLethal, Literal(0.7168217)]),
                            FeatureHasWard,
                        ]),
                        Literal(0.93497086),
                    ]),
                    OperatorMul(vec![Literal(0.107727766), FeatureHasGuard]),
                    OperatorMul(vec![FeatureHasLethal, Literal(0.7168217)]),
                    OperatorMul(vec![FeatureHasDrain, Literal(0.93497086)]),
                ])
            },
            state_node: {
                use tree::StateNode::*;
                Literal(0.8163147)
            },
        }),
        Some("Tree-from-Linear-standard-1-2") => play(tree::TreeIndividual {
            card_node: {
                use tree::CardNode::*;
                OperatorAdd(vec![
                    OperatorMul(vec![
                        OperatorMul(vec![
                            Literal(0.7168217),
                            OperatorMul(vec![
                                OperatorMul(vec![FeatureHasGuard, Literal(0.95310736)]),
                                FeatureAttack,
                            ]),
                        ]),
                        Literal(0.107727766),
                    ]),
                    FeatureHasWard,
                    OperatorMul(vec![
                        OperatorMul(vec![
                            OperatorMul(vec![
                                OperatorMul(vec![Literal(0.107727766), Literal(0.95310736)]),
                                Literal(0.107727766),
                            ]),
                            Literal(0.95310736),
                        ]),
                        FeatureAttack,
                    ]),
                    OperatorMul(vec![
                        OperatorMul(vec![FeatureAttack, Literal(0.93497086)]),
                        FeatureHasGuard,
                    ]),
                    OperatorMul(vec![
                        OperatorMul(vec![FeatureHasLethal, Literal(0.7168217)]),
                        Literal(0.107727766),
                    ]),
                    Literal(0.7168217),
                    FeatureHasWard,
                    OperatorMul(vec![
                        FeatureHasDrain,
                        OperatorAdd(vec![
                            OperatorMul(vec![
                                OperatorMul(vec![
                                    Literal(0.7168217),
                                    OperatorMul(vec![FeatureHasWard, Literal(-0.07205725)]),
                                ]),
                                Literal(0.107727766),
                            ]),
                            Literal(-0.09459996),
                            Literal(0.7168217),
                            Literal(0.93497086),
                            OperatorMul(vec![
                                OperatorMul(vec![
                                    FeatureHasDrain,
                                    OperatorMul(vec![
                                        OperatorMul(vec![
                                            OperatorMul(vec![
                                                Literal(0.7168217),
                                                OperatorMul(vec![
                                                    OperatorMul(vec![
                                                        OperatorMul(vec![
                                                            OperatorMul(vec![
                                                                FeatureHasGuard,
                                                                Literal(0.95310736),
                                                            ]),
                                                            FeatureHasGuard,
                                                        ]),
                                                        Literal(0.7168217),
                                                    ]),
                                                    Literal(0.93497086),
                                                ]),
                                            ]),
                                            Literal(0.107727766),
                                        ]),
                                        Literal(0.7168217),
                                    ]),
                                ]),
                                FeatureHasLethal,
                            ]),
                            Literal(0.7168217),
                            OperatorMul(vec![FeatureHasGuard, Literal(-0.09459996)]),
                            OperatorMul(vec![
                                FeatureHasDrain,
                                OperatorMul(vec![FeatureHasWard, Literal(-0.07205725)]),
                            ]),
                        ]),
                    ]),
                ])
            },
            state_node: {
                use tree::StateNode::*;
                OperatorAdd(vec![
                    OperatorMul(vec![
                        FeatureMeCurrentMana,
                        OperatorMul(vec![FeatureMeMaxMana, Literal(-0.6853397)]),
                    ]),
                    OperatorMul(vec![FeatureOpCurrentMana, Literal(-0.718837)]),
                    Literal(-0.68858814),
                    OperatorMul(vec![FeatureOpHealth, Literal(-0.6853397)]),
                    Literal(-0.718837),
                    OperatorMul(vec![Literal(-0.718837), FeatureOpDecksize]),
                    OperatorMul(vec![FeatureOpCurrentMana, Literal(0.3361919)]),
                    OperatorMul(vec![
                        OperatorMul(vec![
                            Literal(0.079236984),
                            OperatorMul(vec![Literal(-0.6853397), FeatureOpCurrentMana]),
                        ]),
                        Literal(-0.6853397),
                    ]),
                    OperatorMul(vec![FeatureMeCurrentMana, Literal(-0.6853397)]),
                    OperatorMul(vec![Literal(0.079236984), Literal(-0.7775893)]),
                    FeatureOpCurrentMana,
                    OperatorMul(vec![FeatureOpRune, Literal(0.079236984)]),
                ])
            },
        }),
        Some("Tree-from-Linear-standard-2-1") => play(tree::TreeIndividual {
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
                                    OperatorMul(vec![FeatureHasCharge, Literal(-0.20521617)]),
                                ]),
                                OperatorMul(vec![Literal(0.96502376), Literal(-0.057546377)]),
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
                                                OperatorMul(vec![FeatureDefense, FeatureHasCharge]),
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
                                OperatorMul(vec![FeatureHasBreakthrough, Literal(-0.20521617)]),
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
        }),
        Some("Tree-from-Linear-standard-2-2") => play(tree::TreeIndividual {
            card_node: {
                use tree::CardNode::*;
                OperatorAdd(vec![OperatorMul(vec![FeatureAttack, Literal(0.08753133)]), FeatureHasWard, OperatorMul(vec![FeatureAttack, Literal(0.08753133)]), OperatorMul(vec![FeatureHasCharge, Literal(-0.20521617)]), FeatureHasLethal, OperatorMul(vec![FeatureHasGuard, Literal(0.96502376)]), OperatorMul(vec![OperatorAdd(vec![OperatorMul(vec![FeatureAttack, Literal(0.08753133)]), FeatureHasWard, OperatorMul(vec![FeatureAttack, Literal(0.08753133)]), OperatorMul(vec![FeatureHasCharge, Literal(-0.20521617)]), FeatureHasLethal, OperatorMul(vec![FeatureHasGuard, Literal(0.96502376)]), OperatorMul(vec![OperatorMul(vec![OperatorMul(vec![FeatureHasDrain, OperatorMul(vec![OperatorAdd(vec![OperatorMul(vec![FeatureAttack, Literal(0.08753133)]), FeatureHasWard, OperatorMul(vec![FeatureAttack, FeatureAttack]), OperatorMul(vec![FeatureHasCharge, Literal(-0.20521617)]), OperatorMul(vec![FeatureHasDrain, Literal(0.9566674)]), Literal(0.08753133), OperatorMul(vec![FeatureHasLethal, OperatorMul(vec![OperatorMul(vec![Literal(0.0856266), Literal(0.9566674)]), Literal(0.96502376)])]), OperatorMul(vec![OperatorMul(vec![OperatorMul(vec![Literal(0.9566674), OperatorMul(vec![FeatureHasLethal, Literal(0.0856266)])]), OperatorMin(vec![OperatorMul(vec![FeatureHasCharge, Literal(-0.20521617)]), OperatorMul(vec![OperatorMul(vec![OperatorAdd(vec![OperatorMul(vec![FeatureAttack, Literal(0.9566674)]), OperatorMul(vec![FeatureAttack, Literal(0.08753133)]), OperatorMul(vec![FeatureHasGuard, FeatureAttack]), OperatorMin(vec![FeatureAttack, FeatureHasLethal]), OperatorMul(vec![FeatureHasDrain, Literal(0.9566674)]), Literal(0.08753133), OperatorMul(vec![OperatorAdd(vec![OperatorMul(vec![FeatureAttack, Literal(0.08753133)]), FeatureHasWard, OperatorMul(vec![FeatureAttack, Literal(0.08753133)]), OperatorMul(vec![FeatureHasDrain, Literal(0.9566674)]), FeatureHasLethal, OperatorMul(vec![FeatureHasGuard, Literal(0.96502376)]), OperatorMul(vec![OperatorMul(vec![OperatorMul(vec![FeatureHasDrain, OperatorMul(vec![OperatorAdd(vec![OperatorMul(vec![FeatureAttack, Literal(0.9566674)]), OperatorMul(vec![FeatureAttack, Literal(0.08753133)]), OperatorMul(vec![FeatureHasGuard, FeatureAttack]), OperatorMin(vec![FeatureAttack, FeatureHasLethal]), OperatorMul(vec![FeatureHasDrain, Literal(0.9566674)]), Literal(0.08753133), OperatorMul(vec![FeatureHasLethal, OperatorMul(vec![FeatureHasGuard, Literal(0.96502376)])]), FeatureHasWard]), Literal(0.0856266)])]), OperatorMin(vec![FeatureHasDrain, FeatureHasLethal])]), Literal(0.9566674)]), OperatorMul(vec![OperatorMul(vec![Literal(0.08753133), OperatorMin(vec![OperatorMul(vec![FeatureHasDrain, OperatorMul(vec![OperatorAdd(vec![OperatorMul(vec![FeatureAttack, Literal(0.08753133)]), OperatorMul(vec![FeatureDefense, OperatorMul(vec![FeatureHasDrain, Literal(0.96502376)])]), OperatorMul(vec![FeatureAttack, Literal(0.08753133)]), OperatorMul(vec![FeatureHasCharge, Literal(-0.20521617)]), OperatorMul(vec![Literal(-0.20521617), Literal(0.9566674)]), Literal(0.08753133), FeatureHasWard, OperatorMul(vec![OperatorMul(vec![OperatorMul(vec![OperatorAdd(vec![FeatureHasDrain, FeatureHasGuard]), OperatorMin(vec![FeatureAttack, FeatureAttack])]), Literal(0.0856266)]), FeatureHasWard])]), Literal(0.0856266)])]), FeatureHasLethal])]), Literal(0.0856266)])]), OperatorMul(vec![FeatureHasGuard, Literal(0.96502376)])]), FeatureHasWard]), Literal(0.0856266)]), Literal(0.9566674)])])]), Literal(0.0856266)])]), Literal(0.0856266)])]), OperatorMin(vec![FeatureHasDrain, OperatorMul(vec![OperatorAdd(vec![OperatorMul(vec![FeatureAttack, Literal(0.9566674)]), OperatorMul(vec![FeatureAttack, Literal(0.08753133)]), OperatorMul(vec![FeatureHasGuard, FeatureAttack]), OperatorMin(vec![FeatureAttack, FeatureHasLethal]), OperatorMul(vec![FeatureHasDrain, Literal(0.9566674)]), Literal(0.08753133), OperatorMul(vec![FeatureHasLethal, OperatorMul(vec![OperatorMul(vec![OperatorMul(vec![FeatureHasDrain, OperatorMul(vec![OperatorAdd(vec![OperatorMul(vec![FeatureAttack, Literal(0.9566674)]), OperatorMul(vec![FeatureAttack, Literal(0.08753133)]), OperatorMul(vec![FeatureHasGuard, FeatureAttack]), OperatorMin(vec![FeatureAttack, FeatureHasLethal]), OperatorMul(vec![FeatureHasDrain, Literal(0.9566674)]), Literal(0.08753133), OperatorMul(vec![FeatureHasLethal, FeatureHasGuard]), FeatureHasWard]), Literal(0.0856266)])]), OperatorMin(vec![FeatureHasDrain, FeatureHasLethal])]), Literal(0.96502376)])]), FeatureHasWard]), Literal(0.0856266)])])]), Literal(0.9566674)]), OperatorMul(vec![OperatorMul(vec![OperatorAdd(vec![FeatureHasGuard, Literal(-0.20521617)]), OperatorMin(vec![FeatureAttack, FeatureHasLethal])]), Literal(0.0856266)])]), Literal(0.9566674)]), OperatorMul(vec![OperatorMul(vec![OperatorAdd(vec![FeatureHasGuard, Literal(-0.20521617)]), OperatorMin(vec![FeatureAttack, FeatureHasLethal])]), Literal(0.0856266)])])
            },
            state_node: {
                use tree::StateNode::*;
                OperatorAdd(vec![
                    FeatureMeMaxMana,
                    OperatorMul(vec![FeatureMeDecksize, FeatureMeMaxMana]),
                    Literal(0.29115748),
                    OperatorMul(vec![
                        OperatorMul(vec![
                            FeatureOpNextTurnDraw,
                            OperatorMul(vec![Literal(-0.9381685), FeatureOpNextTurnDraw]),
                        ]),
                        OperatorMul(vec![Literal(-0.9381685), Literal(0.46793103)]),
                    ]),
                    OperatorMul(vec![
                        FeatureMeNextTurnDraw,
                        OperatorMul(vec![FeatureOpCurrentMana, Literal(-0.29476237)]),
                    ]),
                    FeatureMeMaxMana,
                    Literal(-0.65507054),
                    FeatureOpNextTurnDraw,
                    FeatureOpCurrentMana,
                    Literal(-0.65507054),
                    OperatorMul(vec![FeatureMeCurrentMana, Literal(-0.65507054)]),
                    FeatureMeDecksize,
                ])
            },
        }),
        Some("Tree-from-Linear-standard-3-1") => play(tree::TreeIndividual {
            card_node: {
                use tree::CardNode::*;
                OperatorAdd(vec![
                    OperatorMul(vec![FeatureAttack, Literal(0.16987157)]),
                    OperatorMul(vec![
                        OperatorMul(vec![FeatureHasWard, Literal(0.8682606)]),
                        Literal(0.16987157),
                    ]),
                    FeatureHasLethal,
                    Literal(0.8682606),
                    FeatureHasWard,
                    OperatorMul(vec![FeatureHasGuard, Literal(0.8682606)]),
                    OperatorMul(vec![FeatureHasBreakthrough, FeatureHasDrain]),
                    Literal(0.8682606),
                ])
            },
            state_node: {
                use tree::StateNode::*;
                OperatorAdd(vec![
                    OperatorMul(vec![FeatureMeCurrentMana, Literal(-0.9301307)]),
                    FeatureOpMaxMana,
                    OperatorMul(vec![FeatureMeHealth, Literal(0.35297656)]),
                    OperatorMul(vec![FeatureMeMaxMana, Literal(-0.63147354)]),
                    OperatorMul(vec![FeatureMeNextTurnDraw, Literal(-0.3260188)]),
                    OperatorMul(vec![
                        FeatureMeRune,
                        OperatorMul(vec![FeatureMeRune, Literal(0.4400499)]),
                    ]),
                    OperatorMul(vec![FeatureMeCurrentMana, Literal(-0.9301307)]),
                    Literal(-0.9301307),
                    OperatorMul(vec![
                        Literal(-0.3989172),
                        OperatorMul(vec![FeatureMeDecksize, Literal(-0.3260188)]),
                    ]),
                    FeatureMeCurrentMana,
                    OperatorMul(vec![FeatureOpNextTurnDraw, FeatureMeMaxMana]),
                    Literal(0.83642316),
                ])
            },
        }),
        Some("Tree-from-Linear-standard-3-2") => play(tree::TreeIndividual {
            card_node: {
                use tree::CardNode::*;
                OperatorAdd(vec![
                    FeatureHasGuard,
                    FeatureHasDrain,
                    OperatorMul(vec![FeatureHasLethal, Literal(0.8682606)]),
                    OperatorMul(vec![Literal(0.2644744), FeatureAttack]),
                    OperatorMul(vec![Literal(0.3099084), Literal(0.8792534)]),
                    OperatorMul(vec![
                        OperatorMul(vec![FeatureHasWard, FeatureHasLethal]),
                        Literal(0.8682606),
                    ]),
                    FeatureHasLethal,
                    FeatureHasWard,
                ])
            },
            state_node: {
                use tree::StateNode::*;
                OperatorAdd(vec![
                    OperatorMul(vec![FeatureMeCurrentMana, Literal(-0.9301307)]),
                    Literal(0.35297656),
                    OperatorMul(vec![
                        FeatureOpNextTurnDraw,
                        OperatorMul(vec![
                            OperatorMul(vec![
                                Literal(-0.9301307),
                                OperatorMul(vec![Literal(-0.9301307), FeatureOpMaxMana]),
                            ]),
                            FeatureMeHealth,
                        ]),
                    ]),
                    FeatureMeHealth,
                    FeatureOpDecksize,
                    FeatureOpDecksize,
                    OperatorMul(vec![FeatureOpCurrentMana, Literal(-0.8443084)]),
                    Literal(-0.31141996),
                    FeatureOpNextTurnDraw,
                    Literal(-0.3260188),
                    OperatorMul(vec![
                        FeatureOpNextTurnDraw,
                        OperatorMul(vec![Literal(0.83642316), FeatureMeHealth]),
                    ]),
                    Literal(-0.3989172),
                ])
            },
        }),
        Some("Tree-from-Linear-standard-4-1") => play(tree::TreeIndividual {
            card_node: {
                use tree::CardNode::*;
                OperatorAdd(vec![
                    OperatorMul(vec![FeatureAttack, Literal(0.19604897)]),
                    OperatorAdd(vec![
                        OperatorMul(vec![FeatureAttack, Literal(0.19604897)]),
                        OperatorMul(vec![
                            OperatorMul(vec![FeatureHasDrain, Literal(0.7029624)]),
                            FeatureHasWard,
                        ]),
                        FeatureHasLethal,
                        OperatorMul(vec![Literal(0.53820753), Literal(-0.21116996)]),
                        OperatorMul(vec![
                            FeatureHasWard,
                            OperatorMul(vec![FeatureHasWard, FeatureHasWard]),
                        ]),
                        OperatorMul(vec![FeatureHasCharge, Literal(-0.45361257)]),
                        OperatorAdd(vec![
                            FeatureHasLethal,
                            FeatureHasGuard,
                            OperatorMul(vec![
                                OperatorMul(vec![
                                    OperatorMul(vec![FeatureAttack, Literal(0.19604897)]),
                                    Literal(0.7029624),
                                ]),
                                OperatorMul(vec![
                                    FeatureHasWard,
                                    OperatorMul(vec![Literal(0.70167494), Literal(0.53820753)]),
                                ]),
                            ]),
                            OperatorMul(vec![
                                OperatorMul(vec![FeatureHasWard, FeatureHasDrain]),
                                Literal(-0.21116996),
                            ]),
                            OperatorMul(vec![FeatureHasDrain, FeatureHasBreakthrough]),
                            Literal(-0.45361257),
                            OperatorMul(vec![
                                OperatorMul(vec![FeatureHasGuard, Literal(0.70167494)]),
                                OperatorMul(vec![FeatureAttack, Literal(0.19604897)]),
                            ]),
                            OperatorMul(vec![Literal(0.7029624), Literal(0.7029624)]),
                        ]),
                        OperatorMul(vec![FeatureHasWard, Literal(0.53820753)]),
                    ]),
                    FeatureHasLethal,
                    OperatorMul(vec![FeatureHasCharge, Literal(-0.21116996)]),
                    FeatureHasLethal,
                    OperatorMul(vec![FeatureHasGuard, Literal(-0.45361257)]),
                    OperatorAdd(vec![
                        OperatorMul(vec![FeatureAttack, Literal(0.19604897)]),
                        FeatureHasGuard,
                        OperatorMul(vec![
                            OperatorMul(vec![
                                OperatorMul(vec![FeatureHasWard, Literal(0.19604897)]),
                                Literal(0.7029624),
                            ]),
                            Literal(-0.45361257),
                        ]),
                        OperatorMul(vec![FeatureHasCharge, Literal(-0.21116996)]),
                        OperatorMul(vec![FeatureHasDrain, Literal(0.7029624)]),
                        OperatorMul(vec![FeatureHasGuard, Literal(0.70167494)]),
                        OperatorMul(vec![FeatureHasGuard, Literal(0.53820753)]),
                        OperatorMul(vec![
                            FeatureHasWard,
                            OperatorMul(vec![FeatureHasWard, Literal(0.53820753)]),
                        ]),
                    ]),
                    OperatorMul(vec![FeatureHasWard, Literal(0.53820753)]),
                ])
            },
            state_node: {
                use tree::StateNode::*;
                OperatorAdd(vec![
                    OperatorMul(vec![FeatureMeCurrentMana, Literal(-0.7309079)]),
                    OperatorMul(vec![
                        FeatureMeDecksize,
                        OperatorMul(vec![FeatureOpDecksize, Literal(0.40940738)]),
                    ]),
                    OperatorMul(vec![
                        OperatorAdd(vec![
                            OperatorMul(vec![FeatureMeCurrentMana, Literal(-0.7309079)]),
                            Literal(0.048369884),
                            OperatorMul(vec![
                                OperatorMul(vec![Literal(0.40940738), Literal(0.86868167)]),
                                Literal(0.2573557),
                            ]),
                            OperatorMul(vec![
                                OperatorMul(vec![FeatureMeDecksize, Literal(0.40940738)]),
                                Literal(0.40940738),
                            ]),
                            Literal(0.23570824),
                            OperatorMul(vec![
                                OperatorMul(vec![
                                    Literal(0.23570824),
                                    OperatorMul(vec![FeatureOpMaxMana, Literal(0.8400798)]),
                                ]),
                                Literal(0.048369884),
                            ]),
                            OperatorMul(vec![FeatureOpCurrentMana, Literal(0.41788054)]),
                            OperatorMul(vec![FeatureOpDecksize, Literal(0.40940738)]),
                            OperatorMul(vec![FeatureMeNextTurnDraw, Literal(0.23570824)]),
                            OperatorMul(vec![FeatureOpMaxMana, Literal(0.8400798)]),
                            OperatorMul(vec![FeatureOpNextTurnDraw, Literal(0.86868167)]),
                            OperatorMul(vec![FeatureMeMaxMana, FeatureOpDecksize]),
                        ]),
                        Literal(0.2573557),
                    ]),
                    Literal(0.048369884),
                    OperatorNeg(Box::new(FeatureMeNextTurnDraw)),
                    OperatorMul(vec![
                        OperatorAdd(vec![
                            OperatorMul(vec![FeatureMeCurrentMana, Literal(-0.7309079)]),
                            OperatorMul(vec![
                                FeatureMeCurrentMana,
                                OperatorMul(vec![
                                    OperatorMul(vec![
                                        FeatureOpNextTurnDraw,
                                        OperatorMul(vec![FeatureOpDecksize, Literal(0.40940738)]),
                                    ]),
                                    Literal(0.40940738),
                                ]),
                            ]),
                            OperatorMul(vec![
                                OperatorMul(vec![
                                    Literal(0.41788054),
                                    OperatorMul(vec![FeatureOpMaxMana, FeatureOpCurrentMana]),
                                ]),
                                Literal(0.23570824),
                            ]),
                            OperatorMul(vec![FeatureMeMaxMana, Literal(-0.09480262)]),
                            OperatorMul(vec![FeatureOpDecksize, Literal(0.23570824)]),
                            OperatorMul(vec![Literal(0.41788054), Literal(0.048369884)]),
                            OperatorMul(vec![FeatureOpCurrentMana, Literal(-0.09480262)]),
                            OperatorMul(vec![FeatureOpCurrentMana, Literal(0.40940738)]),
                            OperatorMul(vec![FeatureMeNextTurnDraw, Literal(0.23570824)]),
                            OperatorMul(vec![
                                OperatorMul(vec![FeatureOpNextTurnDraw, Literal(0.048369884)]),
                                Literal(0.8400798),
                            ]),
                            FeatureOpDecksize,
                            OperatorMul(vec![Literal(0.23570824), Literal(0.86868167)]),
                        ]),
                        Literal(0.048369884),
                    ]),
                    OperatorMul(vec![FeatureOpCurrentMana, Literal(0.41788054)]),
                    OperatorMul(vec![FeatureOpDecksize, Literal(0.40940738)]),
                    OperatorMul(vec![FeatureMeNextTurnDraw, Literal(0.23570824)]),
                    Literal(0.23570824),
                    OperatorMul(vec![FeatureOpNextTurnDraw, Literal(0.86868167)]),
                    OperatorMul(vec![Literal(0.23570824), Literal(0.86868167)]),
                ])
            },
        }),
        Some("Tree-from-Linear-standard-4-2") => play(tree::TreeIndividual {
            card_node: {
                use tree::CardNode::*;
                OperatorAdd(vec![
                    OperatorMul(vec![FeatureAttack, Literal(0.19604897)]),
                    OperatorMul(vec![
                        FeatureHasGuard,
                        OperatorAdd(vec![
                            FeatureHasLethal,
                            FeatureHasLethal,
                            OperatorMul(vec![FeatureAttack, Literal(0.19604897)]),
                            OperatorMul(vec![FeatureHasCharge, FeatureHasGuard]),
                            Literal(-0.103866816),
                            OperatorMul(vec![FeatureAttack, FeatureHasCharge]),
                            OperatorMul(vec![
                                OperatorAdd(vec![
                                    OperatorMul(vec![FeatureAttack, Literal(0.19604897)]),
                                    OperatorMul(vec![
                                        FeatureHasGuard,
                                        OperatorAdd(vec![
                                            FeatureHasLethal,
                                            FeatureHasLethal,
                                            OperatorMul(vec![FeatureAttack, Literal(0.19604897)]),
                                            OperatorMul(vec![FeatureHasGuard, FeatureHasGuard]),
                                            Literal(-0.103866816),
                                            OperatorMul(vec![FeatureHasGuard, FeatureHasCharge]),
                                            OperatorMul(vec![
                                                FeatureHasLethal,
                                                Literal(-0.103866816),
                                            ]),
                                            OperatorMul(vec![
                                                OperatorAdd(vec![
                                                    FeatureHasLethal,
                                                    FeatureHasWard,
                                                    OperatorMul(vec![
                                                        FeatureHasGuard,
                                                        OperatorMul(vec![
                                                            FeatureAttack,
                                                            Literal(0.19604897),
                                                        ]),
                                                    ]),
                                                    OperatorMul(vec![
                                                        FeatureHasBreakthrough,
                                                        FeatureHasGuard,
                                                    ]),
                                                    OperatorMul(vec![
                                                        FeatureAttack,
                                                        Literal(0.19604897),
                                                    ]),
                                                    OperatorMul(vec![
                                                        FeatureHasGuard,
                                                        FeatureHasCharge,
                                                    ]),
                                                    OperatorMul(vec![
                                                        OperatorAdd(vec![
                                                            OperatorMul(vec![
                                                                FeatureAttack,
                                                                Literal(0.19604897),
                                                            ]),
                                                            OperatorAdd(vec![
                                                                OperatorMul(vec![
                                                                    FeatureAttack,
                                                                    Literal(0.19604897),
                                                                ]),
                                                                OperatorMul(vec![
                                                                    FeatureHasGuard,
                                                                    OperatorMul(vec![
                                                                        FeatureAttack,
                                                                        Literal(0.19604897),
                                                                    ]),
                                                                ]),
                                                                OperatorMul(vec![
                                                                    FeatureHasLethal,
                                                                    Literal(-0.103866816),
                                                                ]),
                                                                FeatureHasDrain,
                                                                FeatureAttack,
                                                                OperatorMul(vec![
                                                                    FeatureHasGuard,
                                                                    Literal(0.70167494),
                                                                ]),
                                                                OperatorMul(vec![
                                                                    FeatureHasLethal,
                                                                    Literal(0.35807967),
                                                                ]),
                                                                FeatureHasWard,
                                                            ]),
                                                            OperatorMul(vec![
                                                                OperatorMul(vec![
                                                                    FeatureHasDrain,
                                                                    Literal(0.35807967),
                                                                ]),
                                                                Literal(-0.45361257),
                                                            ]),
                                                            FeatureHasDrain,
                                                            FeatureDefense,
                                                            OperatorMul(vec![
                                                                FeatureHasGuard,
                                                                Literal(0.70167494),
                                                            ]),
                                                            OperatorMul(vec![
                                                                Literal(0.53820753),
                                                                FeatureHasDrain,
                                                            ]),
                                                            FeatureHasWard,
                                                        ]),
                                                        Literal(-0.103866816),
                                                    ]),
                                                    OperatorMul(vec![
                                                        FeatureHasWard,
                                                        Literal(0.53820753),
                                                    ]),
                                                ]),
                                                Literal(0.53820753),
                                            ]),
                                        ]),
                                    ]),
                                    OperatorMul(vec![
                                        OperatorMul(vec![
                                            FeatureHasBreakthrough,
                                            Literal(-0.45361257),
                                        ]),
                                        FeatureAttack,
                                    ]),
                                    FeatureHasDrain,
                                    OperatorMul(vec![FeatureHasDrain, Literal(0.7029624)]),
                                    OperatorMul(vec![FeatureHasGuard, Literal(0.70167494)]),
                                    OperatorMul(vec![FeatureHasLethal, Literal(0.35807967)]),
                                    FeatureHasWard,
                                ]),
                                Literal(-0.103866816),
                            ]),
                            OperatorMul(vec![FeatureHasWard, Literal(0.53820753)]),
                        ]),
                    ]),
                    Literal(0.7029624),
                    FeatureHasDrain,
                    OperatorMul(vec![FeatureHasWard, Literal(0.53820753)]),
                    OperatorMul(vec![FeatureHasGuard, Literal(0.70167494)]),
                    OperatorMul(vec![FeatureHasLethal, FeatureHasLethal]),
                    FeatureHasWard,
                ])
            },
            state_node: {
                use tree::StateNode::*;
                OperatorAdd(vec![
                    OperatorMul(vec![FeatureMeCurrentMana, Literal(-0.7309079)]),
                    OperatorMul(vec![FeatureMeCurrentMana, Literal(-0.07216716)]),
                    OperatorMul(vec![FeatureMeHealth, Literal(0.2573557)]),
                    FeatureMeRune,
                    OperatorMul(vec![FeatureMeNextTurnDraw, Literal(0.23570824)]),
                    FeatureMeRune,
                    OperatorMul(vec![
                        Literal(0.40940738),
                        OperatorMul(vec![FeatureMeRune, Literal(-0.09480262)]),
                    ]),
                    OperatorMul(vec![FeatureOpDecksize, Literal(0.40940738)]),
                    OperatorMul(vec![
                        OperatorMul(vec![
                            FeatureMeMaxMana,
                            OperatorMul(vec![FeatureMeCurrentMana, Literal(-0.7309079)]),
                        ]),
                        Literal(-0.028533459),
                    ]),
                    OperatorMul(vec![
                        OperatorMul(vec![
                            FeatureOpCurrentMana,
                            OperatorMul(vec![FeatureOpNextTurnDraw, FeatureMeRune]),
                        ]),
                        OperatorAdd(vec![
                            OperatorMin(vec![FeatureOpDecksize, FeatureMeRune]),
                            FeatureOpDecksize,
                        ]),
                    ]),
                    OperatorMul(vec![FeatureOpNextTurnDraw, Literal(0.86868167)]),
                    OperatorMul(vec![Literal(0.86868167), Literal(-0.9591818)]),
                ])
            },
        }),
        None => play(AgentRandom),
        _ => unimplemented!(),
    }
}

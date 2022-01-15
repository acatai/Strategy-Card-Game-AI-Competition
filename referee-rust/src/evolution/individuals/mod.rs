pub mod binarytree;
pub mod linear;
pub mod tree;

pub use crate::evolution::individuals::binarytree::BinaryTreeIndividual;
pub use crate::evolution::individuals::linear::LinearIndividual;
pub use crate::evolution::individuals::tree::TreeIndividual;
use rand::Rng;

pub trait Individual: Clone + Default + Sync {
    fn crossover(parents: [&Self; 2], children: [&mut Self; 2], rng: &mut impl Rng);
    fn mutate(&mut self, rng: &mut impl Rng);
    fn randomize(&mut self, rng: &mut impl Rng);
}

export RAYON_NUM_THREADS=4

mkdir -p results-tree-from
rm -f results-tree-from/*

for index in {1..5}; do
  cargo run --release --bin evolve-from | tee "results-tree-from/evolution-$index.txt"
done

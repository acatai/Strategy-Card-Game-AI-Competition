export RAYON_NUM_THREADS=4

mkdir -p results-linear-from
rm -f results-linear-from/*

for index in {1..5}; do
  cargo run --release --bin evolve-from | tee "results-linear-from/evolution-$index.txt"
done

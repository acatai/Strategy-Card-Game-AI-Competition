export RAYON_NUM_THREADS=4

# individuals[0]="BinaryTree"
# individuals[0]="Linear"
individuals[0]="Tree"

# mkdir -p results-frombest
# rm -f results-frombest/*

for individual in "${individuals[@]}"; do
  for index in {2..5}; do
    INDIVIDUAL=$individual SCORING="frombest" cargo run --release --bin evolve | tee "results-frombest/evolution-$individual-frombest-$index.txt"
  done
done

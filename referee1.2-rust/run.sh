export RAYON_NUM_THREADS=4

individuals[0]="BinaryTree"
individuals[1]="Linear"
individuals[2]="Tree"

scorings[0]="baseline"
scorings[1]="standard"

mkdir -p results
rm -f results/*

for individual in "${individuals[@]}"; do
  for scoring in "${scorings[@]}"; do
    for index in {1..5}; do
      INDIVIDUAL=$individual SCORING=$scoring cargo run --release --bin evolve | tee "results/evolution-$individual-$scoring-$index.txt"
    done
  done
done

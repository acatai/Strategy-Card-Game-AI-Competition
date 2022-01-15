# Baseline1
# Baseline2
# Chad
(cd Chad/agent && cargo +nightly-2020-05-14 build --release)
# Coac
(cd Coac && cmake . && make)
# OneLaneIsEnough
(cd OneLaneIsEnough && g++ -std=c++17 -O3 main.cpp -o main)
# ReinforcedGreediness
mkdir -p agents

AGENTS[0]="BinaryTree-baseline-1"
AGENTS[1]="BinaryTree-baseline-3"
AGENTS[2]="BinaryTree-baseline-4"
AGENTS[3]="BinaryTree-baseline-5"
AGENTS[4]="BinaryTree-frombest-1"
AGENTS[5]="BinaryTree-frombest-2"
AGENTS[6]="BinaryTree-frombest-3"
AGENTS[7]="BinaryTree-frombest-4"
AGENTS[8]="BinaryTree-frombest-5"
AGENTS[9]="BinaryTree-standard-1"
AGENTS[10]="BinaryTree-standard-2"
AGENTS[11]="BinaryTree-standard-3"
AGENTS[12]="BinaryTree-standard-4"
AGENTS[13]="BinaryTree-standard-5"
AGENTS[14]="Linear-baseline-1"
AGENTS[15]="Linear-baseline-2"
AGENTS[16]="Linear-baseline-4"
AGENTS[17]="Linear-baseline-5"
AGENTS[18]="Linear-frombest-1"
AGENTS[19]="Linear-frombest-2"
AGENTS[20]="Linear-frombest-3"
AGENTS[21]="Linear-frombest-4"
AGENTS[22]="Linear-frombest-5"
AGENTS[23]="Linear-standard-1"
AGENTS[24]="Linear-standard-2"
AGENTS[25]="Linear-standard-3"
AGENTS[26]="Linear-standard-4"
AGENTS[27]="Linear-standard-5"
AGENTS[28]="Tree-baseline-1"
AGENTS[29]="Tree-baseline-2"
AGENTS[30]="Tree-baseline-3"
AGENTS[31]="Tree-baseline-4"
AGENTS[32]="Tree-baseline-5"
AGENTS[33]="Tree-frombest-1"
AGENTS[34]="Tree-frombest-2"
AGENTS[35]="Tree-frombest-3"
AGENTS[36]="Tree-frombest-4"
AGENTS[37]="Tree-frombest-5"
AGENTS[38]="Tree-standard-1"
AGENTS[39]="Tree-standard-2"
AGENTS[40]="Tree-standard-3"
AGENTS[41]="Tree-standard-4"
AGENTS[42]="Tree-standard-5"
AGENTS[43]="Linear-from-Linear-standard-1-1"
AGENTS[44]="Linear-from-Linear-standard-1-2"
AGENTS[45]="Linear-from-Linear-standard-2-1"
AGENTS[46]="Linear-from-Linear-standard-2-2"
AGENTS[47]="Linear-from-Linear-standard-3-1"
AGENTS[48]="Linear-from-Linear-standard-3-2"
AGENTS[49]="Linear-from-Linear-standard-4-1"
AGENTS[50]="Linear-from-Linear-standard-4-2"
AGENTS[51]="Tree-from-Linear-standard-1-1"
AGENTS[52]="Tree-from-Linear-standard-1-2"
AGENTS[53]="Tree-from-Linear-standard-2-1"
AGENTS[54]="Tree-from-Linear-standard-2-2"
AGENTS[55]="Tree-from-Linear-standard-3-1"
AGENTS[56]="Tree-from-Linear-standard-3-2"
AGENTS[57]="Tree-from-Linear-standard-4-1"
AGENTS[58]="Tree-from-Linear-standard-4-2"
for agent in "${AGENTS[@]}"; do
  (cd referee-rust && AGENT="$agent" cargo +stable build --release --bin agent && cp target/release/agent "../agents/$agent")
done

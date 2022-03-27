AGENTS[0]="python3 Baseline1/main.py"
AGENTS[1]="python3 Baseline2/main.py"
AGENTS[2]="./Chad/agent/target/release/agent"
AGENTS[3]="./Coac/main"
AGENTS[4]="./OneLaneIsEnough/main"
AGENTS[5]="python3 ReinforcedGreediness/agent.py"
AGENTS[6]="./agents/BinaryTree-baseline-1"
AGENTS[7]="./agents/BinaryTree-baseline-3"
AGENTS[8]="./agents/BinaryTree-baseline-4"
AGENTS[9]="./agents/BinaryTree-baseline-5"
AGENTS[10]="./agents/BinaryTree-frombest-1"
AGENTS[11]="./agents/BinaryTree-frombest-2"
AGENTS[12]="./agents/BinaryTree-frombest-3"
AGENTS[13]="./agents/BinaryTree-frombest-4"
AGENTS[14]="./agents/BinaryTree-frombest-5"
AGENTS[15]="./agents/BinaryTree-standard-1"
AGENTS[16]="./agents/BinaryTree-standard-2"
AGENTS[17]="./agents/BinaryTree-standard-3"
AGENTS[18]="./agents/BinaryTree-standard-4"
AGENTS[19]="./agents/BinaryTree-standard-5"
AGENTS[20]="./agents/Linear-baseline-1"
AGENTS[21]="./agents/Linear-baseline-2"
AGENTS[22]="./agents/Linear-baseline-4"
AGENTS[23]="./agents/Linear-baseline-5"
AGENTS[24]="./agents/Linear-frombest-1"
AGENTS[25]="./agents/Linear-frombest-2"
AGENTS[26]="./agents/Linear-frombest-3"
AGENTS[27]="./agents/Linear-frombest-4"
AGENTS[28]="./agents/Linear-frombest-5"
AGENTS[29]="./agents/Linear-standard-1"
AGENTS[30]="./agents/Linear-standard-2"
AGENTS[31]="./agents/Linear-standard-3"
AGENTS[32]="./agents/Linear-standard-4"
AGENTS[33]="./agents/Linear-standard-5"
AGENTS[34]="./agents/Tree-baseline-1"
AGENTS[35]="./agents/Tree-baseline-2"
AGENTS[36]="./agents/Tree-baseline-3"
AGENTS[37]="./agents/Tree-baseline-4"
AGENTS[38]="./agents/Tree-baseline-5"
AGENTS[39]="./agents/Tree-frombest-1"
AGENTS[40]="./agents/Tree-frombest-2"
AGENTS[41]="./agents/Tree-frombest-3"
AGENTS[42]="./agents/Tree-frombest-4"
AGENTS[43]="./agents/Tree-frombest-5"
AGENTS[44]="./agents/Tree-standard-1"
AGENTS[45]="./agents/Tree-standard-2"
AGENTS[46]="./agents/Tree-standard-3"
AGENTS[47]="./agents/Tree-standard-4"
AGENTS[48]="./agents/Tree-standard-5"
AGENTS[49]="./agents/Linear-from-Linear-standard-1-1"
AGENTS[50]="./agents/Linear-from-Linear-standard-1-2"
AGENTS[51]="./agents/Linear-from-Linear-standard-2-1"
AGENTS[52]="./agents/Linear-from-Linear-standard-2-2"
AGENTS[53]="./agents/Linear-from-Linear-standard-3-1"
AGENTS[54]="./agents/Linear-from-Linear-standard-3-2"
AGENTS[55]="./agents/Linear-from-Linear-standard-4-1"
AGENTS[56]="./agents/Linear-from-Linear-standard-4-2"
AGENTS[57]="./agents/Tree-from-Linear-standard-1-1"
AGENTS[58]="./agents/Tree-from-Linear-standard-1-2"
AGENTS[59]="./agents/Tree-from-Linear-standard-2-1"
AGENTS[60]="./agents/Tree-from-Linear-standard-2-2"
AGENTS[61]="./agents/Tree-from-Linear-standard-3-1"
AGENTS[62]="./agents/Tree-from-Linear-standard-3-2"
AGENTS[63]="./agents/Tree-from-Linear-standard-4-1"
AGENTS[64]="./agents/Tree-from-Linear-standard-4-2"

for i in {1..1000}; do
  SEED1=$RANDOM # Same for a whole epoch.
  for j in {1..10}; do
    for playerA in "${AGENTS[@]}"; do
      for playerB in "${AGENTS[@]}"; do
        SEED2=$RANDOM # Same for both players.
        echo -n "$(date +%FT%T) '$playerA' '$playerB' "
        java \
          --add-opens java.base/java.lang=ALL-UNNAMED \
          -jar LoCM.jar \
          -p1 "$playerA" \
          -p2 "$playerB" \
          -l /dev/stdout \
          -d "draftChoicesSeed=$SEED1 seed=$SEED2 shufflePlayer0Seed=$SEED2 shufflePlayer1Seed=$SEED2" \
          | awk 1 ORS=' ' \
          | sed 's/WARNING: sun.reflect.Reflection.getCallerClass is not supported. This will impact performance. //' -
        echo
      done
    done
  done
done

AGENTS[0]="python3 Baseline1/main.py"
AGENTS[1]="python3 Baseline2/main.py"
AGENTS[2]="./Chad/agent/target/release/agent"
AGENTS[3]="./Coac/main"
AGENTS[4]="./OneLaneIsEnough/main"
AGENTS[5]="python3 ReinforcedGreediness/agent.py"

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

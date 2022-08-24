AGENTS[0]="java -jar AdvancedAvocadoAgent/advanced-avocado-agent/agent/build/libs/agent-all.jar"
AGENTS[1]="python3 Ag2O/play.py"
AGENTS[2]="python3 Baseline1/main.py"
AGENTS[3]="python3 Baseline2/main.py"
AGENTS[4]="./Chad/agent/target/release/agent"
AGENTS[5]="./Coac/main"
AGENTS[6]="mono ./DrainPower/DrainPower.exe"
AGENTS[7]="mono ./DrainPower/DrainPower.exe aggressive"
AGENTS[8]="java -cp LANE_1_0 Player"
AGENTS[9]="./OneLaneIsEnough/main"
AGENTS[10]="python3 ReinforcedGreediness/agent.py"
AGENTS[11]="python3 ByteRL/locm1d2_submit.py"

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

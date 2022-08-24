export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
export NUMEXPR_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OMP_NUM_THREADS=1

AGENTS[0]="java -jar RandomWItems2lanes/agent.jar"
AGENTS[1]="java -jar Zylo/agent.jar"
AGENTS[2]="python3 ByteRL/locm1d5_submit.py"
AGENTS[3]="python3 Inspirai/agent.py"
AGENTS[4]="python3 MugenSlayerAttackOnDuraraBallV3/31072022rdycode.py"
AGENTS[5]="python3 NeteaseOPD/main.py"
AGENTS[6]="python3 USTC-gogogo/Zero.py"

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
          play \
          -p1 "$playerA" \
          -p2 "$playerB" \
          -l /dev/stdout \
          -d "cardGenSeed=$SEED1 constructedChoicesSeed=$SEED1 draftChoicesSeed=$SEED1 seed=$SEED2 shufflePlayer0Seed=$SEED2 shufflePlayer1Seed=$SEED2" \
          | awk 1 ORS=' ' \
          | sed 's/WARNING: sun.reflect.Reflection.getCallerClass is not supported. This will impact performance. //' -
        echo
      done
    done
  done
done

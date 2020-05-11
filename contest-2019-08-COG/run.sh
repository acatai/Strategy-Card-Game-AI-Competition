AGENTS[0]="python3 AntiSquid/main.py"
AGENTS[1]="./Coac/main"
AGENTS[2]="./ProphetCoac/main"
AGENTS[3]="js ./Conrisc/main.js"
AGENTS[4]="./Fabbiamo/main"
AGENTS[5]="./Marasbot/main"
AGENTS[6]="python3 UJIAgent1/main.py"
AGENTS[7]="python3 UJIAgent2/main.py"
AGENTS[8]="python3 UJIAgent3/main.py"
AGENTS[9]="python3 Baseline1/main.py"
AGENTS[10]="python3 Baseline2/main.py"

for i in {1..827}; do
  SEED1=$RANDOM # Same for a whole epoch.
  for j in {1..10}; do
    for playerA in "${AGENTS[@]}"; do
      for playerB in "${AGENTS[@]}"; do
        SEED2=$RANDOM # Same for both players.
        echo -n "$(date +%FT%T) '$playerA' '$playerB' "
        java -jar ../LoCM.jar \
          -p1 "$playerA" \
          -p2 "$playerB" \
          -l /dev/stdout \
          -d "draftChoicesSeed=$SEED1 seed=$SEED2 shufflePlayer0Seed=$SEED2 shufflePlayer1Seed=$SEED2" \
          | awk 1 ORS=' '
        echo
      done
    done
  done
done

### Build

```sh
# Debug build
nim c Player.nim
nim c Runner.nim
nim c Tester.nim

# Release build
nim c -d:release Player.nim
nim c -d:release Runner.nim
nim c -d:release Tester.nim
```

### CLI

```sh
./Player --draft="" --player="" --seed=N --state="" --time=N
./Runner --p1-draft="" --p1-player="" --p1-state="" --p1-time=N --p2-draft="" --p2-player="" --p2-state="" --p2-time=N --games=N --verbose=false
./Tester --referee="" --plain=false --player1="" --player2="" --games=N --threads=N --replays=false
```

### Run

```sh
nim c -d:release Runner.nim
./Runner \
  --p1-draft=Icebox \
  --p1-player=DFS \
  --p1-time=100 \
  --p2-draft=ClosetAI \
  --p2-player=FMC \
  --p2-time=150 \
  --games=16 \
  --verbose=false
```

### Run (CG referee)

```sh
nim c -d:release Player.nim
nim c -d:release Tester.nim
./Tester \
  --referee="java --add-opens java.base/java.lang=ALL-UNNAMED -jar LoCM.jar" \
  --player1="./Player --draft=Icebox --player=DFS --time=100" \
  --player2="./Player --draft=ClosetAI --player=FMC --time=150" \
  --games=16 \
  --threads=4
```

### Roadmap

**[Draft evaluations](Research/DraftEvaluations):**

* [x] ClosetAI (`--draft=ClosetAI`, [source](Research/DraftEvaluations/ClosetAI.nim), [ClosetAI profile on CodinGame](https://www.codingame.com/forum/u/ClosetAI))
* [x] Icebox (`--draft=Icebox`, [source](Research/DraftEvaluations/Icebox.nim), [Icebox profile on CodinGame](https://www.codingame.com/forum/u/icebox))
* [x] Manual (`--draft=Manual`, [source](Research/DraftEvaluations/Manual.nim))
* [x] Random (`--draft=Random3`, [source](Research/DraftEvaluations/Random3.nim))

**[Player algorithms](Research/PlayerAlgorithms):**

* [x] Bridge Burning Monte Carlo Tree Search (`--player=BBMCTS`, [source](Research/PlayerAlgorithms/BBMCTS.nim))
* [x] DFS (`--player=DFS`, [source](Research/PlayerAlgorithms/DFS.nim))
* [x] Flat Monte Carlo (`--player=FMC`, [source](Research/PlayerAlgorithms/FMC.nim))
* [x] Greedy (`--player=Greedy`, [source](Research/PlayerAlgorithms/Greedy.nim))
* [x] Monte Carlo Tree Search (`--player=MCTS`, [source](Research/PlayerAlgorithms/MCTS.nim))
* [x] Monte Carlo Tree Search - lookahead (`--player=MCTS0`, [source](Research/PlayerAlgorithms/MCTS0.nim))
* [x] Monte Carlo Tree Search + pruning (`--player=MCTSP`, [source](Research/PlayerAlgorithms/MCTSP.nim))
* [x] Noop (`--player=Noop`, [source](Research/PlayerAlgorithms/Noop.nim))
* [x] Random (`--player=Random`, [source](Research/PlayerAlgorithms/Random.nim))

**[State evaluations](Research/StateEvaluations):**

* [x] Simple (`--state=Simple`, [source](Research/StateEvaluations/Simple.nim))

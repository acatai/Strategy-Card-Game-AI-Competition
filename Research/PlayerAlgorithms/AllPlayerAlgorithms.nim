import std / tables
import BBMCTS, DFS, FMC, Greedy, MCTS, MCTS0, MCTSP, Noop, Random

const playerAlgorithms * = toTable({
  "default": playerAlgorithmDFS,
  "BBMCTS":  playerAlgorithmBBMCTS,
  "DFS":     playerAlgorithmDFS,
  "FMC":     playerAlgorithmFMC,
  "Greedy":  playerAlgorithmGreedy,
  "MCTS":    playerAlgorithmMCTS,
  "MCTS0":   playerAlgorithmMCTS0,
  "MCTSP":   playerAlgorithmMCTSP,
  "Noop":    playerAlgorithmNoop,
  "Random":  playerAlgorithmRandom,
})

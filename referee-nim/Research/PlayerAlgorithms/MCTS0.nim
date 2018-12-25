import std / [random, times]
import Shared / MCTSNode
import .. / .. / Engine / [Action, Config, Search, State]

proc playerAlgorithmMCTS0 * (config: Config, state: State): SearchResult =
  proc evaluate (node: MCTSNode): void =
    node.propagate(config.evalState(node.state))

  block:
    var root = MCTSNode(state: state)
    let time = cpuTime()

    while cpuTime() - time < config.time:
      for _ in 1 .. 8:
        root.run(evaluate)

    if not defined(release):
      stderr.writeLine(root)

    root.toSearchResult

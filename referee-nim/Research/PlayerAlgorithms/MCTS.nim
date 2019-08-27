import std / [random, times]
import Shared / MCTSNode
import .. / .. / Engine / [Config, Search, State]

proc playerAlgorithmMCTS * (config: Config, state: State): SearchResult =
  proc evaluate (node: MCTSNode): void =
    var score = config.evalState(node.state)

    for _ in 1 .. 8:
      var state = node.state.copy.swap
      state.rechargeCreatures
      state.op.hand.setLen(0)

      var legal = state.computeActions
      while legal.len > 0:
        state.applyAction(legal.sample)
        legal = state.computeActions
        score = score.min(config.evalState(state.swap))

    node.propagate(score)

  block:
    var root = MCTSNode(state: state)
    let time = cpuTime()

    while cpuTime() - time < config.time:
      for _ in 1 .. 8:
        root.run(evaluate)

    if not defined(release):
      stderr.writeLine(root)

    root.toSearchResult

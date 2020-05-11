import std / [random, times]
import Shared / MCTSNode
import .. / .. / Engine / [Action, Config, Search, State]

proc playerAlgorithmMCTSP * (config: Config, state: State): SearchResult =
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

  proc run (node: MCTSNode): void =
    let wasExpanding = not node.opened
    if wasExpanding:
      node.nodes = @[]
      node.opened = true

      for action in node.state.computeActions:
        if action.actionType != pass and node.move != nil:
          let valid = case node.move.actionType:
            of attack: action.actionType == attack
            of use:    action.actionType == attack or action.actionType == use
            of summon: true
            else:      false

          if not valid:
            continue

        var state = node.state.copy
        state.applyAction(action)
        node.nodes.add(MCTSNode(move: action, parent: node, state: state))

    if node.nodes.len == 0:
      node.evaluate
    elif wasExpanding:
      node.pick.evaluate
    else:
      node.pick.run

  block:
    var root = MCTSNode(state: state)
    let time = cpuTime()

    while cpuTime() - time < config.time:
      for _ in 1 .. 8:
        root.run

    if not defined(release):
      stderr.writeLine(root)

    root.toSearchResult

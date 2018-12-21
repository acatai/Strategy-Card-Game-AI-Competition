import std / [random, times]
import .. / .. / Engine / [Action, Config, Search, State]

proc simulate (config: Config, root: State): SearchResult =
  var state = root.copy
  var legals = state.computeActions
  var actions: seq[Action]

  while legals.len > 0:
    let action = legals.rand
    actions.add(action)
    state.applyAction(action)
    legals = state.computeActions

  SearchResult(actions: actions, score: config.evalState(state))

proc playerAlgorithmFMC * (config: Config, state: State): SearchResult =
  block:
    result = SearchResult(score: NegInf)

    let time = cpuTime()

    while cpuTime() - time < config.time:
      for _ in 1 .. 10:
        let simulated = simulate(config, state)
        if simulated.score > result.score:
          result = simulated

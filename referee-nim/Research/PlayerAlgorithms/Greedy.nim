import .. / .. / Engine / [Action, Config, Search, State]

func apply (state: State, action: Action): State {.inline.} =
  result = state.copy
  result.applyAction(action)

proc playerAlgorithmGreedy * (config: Config, root: State): SearchResult =
  block:
    result = SearchResult()

    var state = root.copy
    var legal = state.computeActions

    while legal.len > 0:
      var bestEval = NegInf
      var bestMove: Action

      for action in legal:
        let eval = config.evalState(state.apply(action))
        if eval > bestEval:
          bestEval = eval
          bestMove = action

      result.actions.add(bestMove)
      state.applyAction(bestMove)
      legal = state.computeActions

    result.score = config.evalState(state)

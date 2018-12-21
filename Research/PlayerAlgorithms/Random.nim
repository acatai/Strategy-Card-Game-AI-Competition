import std / random
import .. / .. / Engine / [Config, Search, State]

proc playerAlgorithmRandom * (config: Config, root: State): SearchResult =
  result = SearchResult()

  var state = root.copy
  var legal = state.computeActions

  while legal.len > 0:
    let action = legal.rand
    result.actions.add(action)
    state.applyAction(action)
    legal = state.computeActions

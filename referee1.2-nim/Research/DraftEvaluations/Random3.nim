import std / random
import .. / .. / Engine / [Config, Draft, State]

proc evaluateDraftRandom3*(config: Config, state: State): DraftResult =
  DraftResult(index: rand(2))

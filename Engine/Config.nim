import Draft, Search, State

type
  Config * = ref object
    evalDraftFn *: proc (config: Config, state: State): DraftResult
    evalStateFn *: proc (config: Config, state: State): float
    playFn *: proc (config: Config, state: State): SearchResult
    time *: float

proc evalDraft * (config: Config, state: State): DraftResult {.inline.} =
  config.evalDraftFn(config, state)

proc evalState * (config: Config, state: State): float {.inline.} =
  config.evalStateFn(config, state)

proc play * (config: Config, state: State): SearchResult {.inline.} =
  config.playFn(config, state)

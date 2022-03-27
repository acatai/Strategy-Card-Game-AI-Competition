import std / strformat
import Card, State

type
  Draft* = array[30, array[3, Card]]
  DraftResult* = ref object
    index*: int
    score*: float

func `$`*(draftResult: DraftResult): string =
  &"PICK {draftResult.index} # score: {draftResult.score}"

func evaluateDraftWith*(
  state: State,
  evaluate: proc (card: Card): float {.noSideEffect.}
): DraftResult {.inline.} =
  result = DraftResult(score: NegInf)

  for index, card in state.me.hand:
    let score = card.evaluate
    if score > result.score:
      result.index = index
      result.score = score

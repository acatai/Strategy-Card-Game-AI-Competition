import std / strformat
import Constants

type
  ActionType* = enum
    attack,
    pass,
    summon,
    use
  Action* = ref object
    text*: string
    case actionType*: ActionType
      of attack, use:
        id1*: int
        id2*: int
      of pass:
        discard
      of summon:
        id*: int
        lane*: 0 .. Lanes - 1

func newActionAttack*(id1, id2: int): Action {.inline.} =
  Action(actionType: attack, id1: id1, id2: id2)

func newActionPass*(): Action {.inline.} =
  Action(actionType: pass)

func newActionSummon*(id: int, lane: 0 .. Lanes - 1): Action {.inline.} =
  Action(actionType: summon, id: id, lane: lane)

func newActionUse*(id1, id2: int): Action {.inline.} =
  Action(actionType: use, id1: id1, id2: id2)

func `$`*(action: Action): string =
  case action.actionType:
    of attack: &"ATTACK {action.id1} {action.id2}"
    of pass: &"PASS"
    of summon: &"SUMMON {action.id} {action.lane}"
    of use: &"USE {action.id1} {action.id2}"

when isMainModule:
  func main(): void =
    let x = Action(actionType: attack, id1: 1, id2: 2)
    let y = Action(actionType: attack, id1: 1, id2: 3)

    doAssert $x == "ATTACK 1 2"
    doAssert $y == "ATTACK 1 3"

  main()

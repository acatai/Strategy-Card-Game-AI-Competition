import std / [streams, strformat]
import Input

type
  CardAttackState* = enum
    alreadyAttacked
    canAttack
    noAttack
  CardLocation* = enum
    inHand
    myBoard
    opBoard
  CardType* = enum
    creature,
    itemBlue,
    itemGreen,
    itemRed
  Card* = ref object
    attack*: int
    attackState*: CardAttackState
    cardDraw*: int
    cardNumber*: int
    cardType*: CardType
    cost*: int
    defense*: int
    hasBreakthrough*: bool
    hasCharge*: bool
    hasDrain*: bool
    hasGuard*: bool
    hasLethal*: bool
    hasWard*: bool
    instanceId*: int
    lane*: int
    location*: CardLocation
    myHealthChange*: int
    opHealthChange*: int

func `$`*(card: Card): string =
  let b = if card.hasBreakthrough: 'B' else: '-'
  let c = if card.hasCharge: 'C' else: '-'
  let d = if card.hasDrain: 'D' else: '-'
  let g = if card.hasGuard: 'G' else: '-'
  let l = if card.hasLethal: 'L' else: '-'
  let w = if card.hasWard: 'W' else: '-'
  result &= &"{card.instanceId:2} (#{card.cardNumber:3}:{card.cardType:>9}) "
  result &= &"{card.attack:2}/{card.defense:2} [{card.cost:2}] "
  result &= &"{b}{c}{d}{g}{l}{w}"

func copy*(card: Card): Card =
  Card(
    attack: card.attack,
    attackState: card.attackState,
    cardDraw: card.cardDraw,
    cardNumber: card.cardNumber,
    cardType: card.cardType,
    cost: card.cost,
    defense: card.defense,
    hasBreakthrough: card.hasBreakthrough,
    hasCharge: card.hasCharge,
    hasDrain: card.hasDrain,
    hasGuard: card.hasGuard,
    hasLethal: card.hasLethal,
    hasWard: card.hasWard,
    instanceId: card.instanceId,
    lane: card.lane,
    location: card.location,
    myHealthChange: card.myHealthChange,
    opHealthChange: card.opHealthChange,
  )

proc readCard*(input: Input): Card =
  let card = Card(attackState: noAttack)

  card.cardNumber = input.getInt
  card.instanceId = input.getInt

  card.location = case input.getInt:
    of -1: opBoard
    of 0: inHand
    of 1: myBoard
    else: myBoard # discard "Shouldn't happen."

  card.cardType = case input.getInt:
    of 0: creature
    of 1: itemGreen
    of 2: itemRed
    of 3: itemBlue
    else: itemBlue # discard "Shouldn't happen."

  card.cost = input.getInt
  card.attack = input.getInt
  card.defense = input.getInt

  let keywords = input.getStr
  card.hasBreakthrough = keywords[0] == 'B'
  card.hasCharge = keywords[1] == 'C'
  card.hasDrain = keywords[2] == 'D'
  card.hasGuard = keywords[3] == 'G'
  card.hasLethal = keywords[4] == 'L'
  card.hasWard = keywords[5] == 'W'

  card.myHealthChange = input.getInt
  card.opHealthChange = input.getInt
  card.cardDraw = input.getInt
  card.lane = input.getInt
  card

proc readCard*(input: string): Card =
  input.newStringStream.newInput.readCard

when isMainModule:
  proc main(): void =
    let a = "1 2 3 4 5 6 7 BCDG-- 8 9 10 0".readCard
    let b = "7 6 5 4 3 2 1 ----LW 0 0 11 1".readCard

    doAssert $a == " 2 (#  1: itemBlue)  6/ 7 [ 5] BCDG--"
    doAssert $b == " 6 (#  7: itemBlue)  2/ 1 [ 3] ----LW"

  main()

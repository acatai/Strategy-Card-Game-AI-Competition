import std / strformat
import Card, Constants, Input

type
  Gamer * = ref object
    boards       *: array[Lanes, seq[Card]]
    bonusMana    *: bool
    currentMana  *: int
    decksize     *: int
    hand         *: seq[Card]
    handsize     *: int
    health       *: int
    maxMana      *: int
    nextTurnDraw *: int
    rune         *: int

func modifyHealth * (gamer: var Gamer, diff: int): void =
  gamer.health += diff

  while gamer.health <= gamer.rune:
    gamer.nextTurnDraw += 1
    gamer.rune = max(0, gamer.rune - 5)
    if gamer.rune <= 0:
      break

func `$` * (gamer: Gamer): string =
  let bonusMana = if gamer.bonusMana: '+' else: ' '
  result &= &"HP{gamer.health:2}({gamer.rune:2}) "
  result &= &"MP{gamer.currentMana:2}/{gamer.maxMana:2}{bonusMana} "
  result &= &"D{gamer.decksize:2} "
  result &= &"H{gamer.handsize:2}+{gamer.nextTurnDraw}"

func copy * (gamer: Gamer): Gamer =
  result = Gamer(
    bonusMana:    gamer.bonusMana,
    currentMana:  gamer.currentMana,
    decksize:     gamer.decksize,
    hand:         gamer.hand,
    handsize:     gamer.handsize,
    health:       gamer.health,
    maxMana:      gamer.maxMana,
    nextTurnDraw: gamer.nextTurnDraw,
    rune:         gamer.rune,
  )

  for lane, board in gamer.boards:
    result.boards[lane] = board

func newGamer * (): Gamer {.inline.} =
  Gamer(health: 30, nextTurnDraw: 1, rune: 25)

proc readGamer * (input: Input): Gamer =
  result = Gamer()
  result.health       = input.getInt
  result.maxMana      = input.getInt
  result.decksize     = input.getInt
  result.rune         = input.getInt
  result.nextTurnDraw = input.getInt
  result.currentMana  = result.maxMana

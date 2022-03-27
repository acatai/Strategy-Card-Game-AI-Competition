import std / [random, strformat]
import .. / Engine / [Action, Card, Cards, Config, Draft, Gamer, State]
import IOHelpers

proc doDraw (gamer: var Gamer, deck: var seq[Card], turn: int): void =
  let suicide = turn > 50
  for _ in 1 .. gamer.nextTurnDraw:
    if gamer.decksize == 0 or suicide:
      gamer.modifyHealth(gamer.rune - gamer.health)
      if gamer.decksize == 0:
        continue

    if gamer.handsize == 8:
      break

    gamer.hand.add(deck.pop)
    gamer.handsize += 1
    gamer.decksize -= 1
  gamer.nextTurnDraw = 1

proc newDraft*(cards: openArray[Card]): Draft =
  var indexes = newSeq[int](cards.len)
  for index in indexes.low .. indexes.high:
    indexes[index] = index
  indexes.shuffle

  for pick in 0 ..< 30:
    for card in 0 ..< 3:
      result[pick][card] = cards[indexes[pick * 3 + card]]

proc newDraft*(): Draft {.inline.} =
  newDraft(getCards())

proc play*(a, b: Config, draft: Draft, verbose: bool = false): bool =
  var state = newState()
  var deck1: seq[Card]
  var deck2: seq[Card]

  for turn in 1 .. 30:
    for card in draft[turn - 1]:
      state.me.hand.add(card.copy)

    let pick1 = a.evalDraft(state)
    let pick2 = b.evalDraft(state)

    deck1.add(state.me.hand[pick1.index].copy)
    deck2.add(state.me.hand[pick2.index].copy)

    state.me.decksize += 1
    state.op.decksize += 1

    if verbose:
      echo &"{stamp()} Draft {turn}"
      echo &"{stamp()} 1? {state.me.hand[0]}"
      echo &"{stamp()} 2? {state.me.hand[1]}"
      echo &"{stamp()} 3? {state.me.hand[2]}"
      echo &"{stamp()} 1! {pick1}"
      echo &"{stamp()} 2! {pick2}"

    state.me.hand.setLen(0)

  for i in countdown(29, 1):
    let j = rand(i)
    swap(deck1[i], deck1[j])
    swap(deck2[i], deck2[j])

  for id, card in deck1: card.instanceId = (30 - id) * 2 - 1
  for id, card in deck2: card.instanceId = (30 - id) * 2

  if verbose:
    echo &"{stamp()} Cards"
    for index in countdown(60, 1):
      let player = (index - 1) mod 2
      let card = (if player == 1: deck1 else: deck2)[(index - 1) div 2]
      echo &"{stamp()} {2 - player}? {card}"

  for card in 1 .. 3:
    doDraw(state.me, deck1, 0)
    doDraw(state.op, deck2, 0)
  doDraw(state.op, deck2, 0)

  block loop:
    for turn in 1 .. 256:
      state.rechargeCreatures

      if verbose:
        echo &"{stamp()} Turn {turn:<12} # [{state.me}] [{state.op}]"

      state.rechargeMana(turn)
      doDraw(state.me, deck1, turn)
      for action in a.play(state).actions:
        state.applyAction(action)
        if verbose:
          echo &"{stamp()} 1! {action:14} # [{state.me}] [{state.op}]"
        if state.isGameOver:
          break loop

      state = state.swap

      state.rechargeMana(turn)
      doDraw(state.me, deck2, turn)
      for action in b.play(state).actions:
        state.applyAction(action)
        if verbose:
          echo &"{stamp()} 2! {action:14} # [{state.op}] [{state.me}]"
        if state.isGameOver:
          state = state.swap
          break loop

      state = state.swap

  if verbose:
    echo &"{stamp()} End               # [{state.me}] [{state.op}]"

  return state.me.health > 0

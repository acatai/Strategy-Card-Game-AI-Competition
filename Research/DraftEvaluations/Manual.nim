import .. / .. / Engine / [Card, Config, Draft, State]

func evaluateDraftManual * (config: Config, state: State): DraftResult =
  state.evaluateDraftWith(func (card: Card): float =
    return
      (card.attack + card.defense) / (card.cost + 5) +
      (if card.hasBreakthrough: 0.1 else: 0) +
      (if card.hasCharge:       0.2 else: 0) +
      (if card.hasDrain:        0.2 else: 0) +
      (if card.hasGuard:        0.4 else: 0) +
      (if card.hasLethal:       0.3 else: 0) +
      (if card.hasWard:         0.2 else: 0)
  )

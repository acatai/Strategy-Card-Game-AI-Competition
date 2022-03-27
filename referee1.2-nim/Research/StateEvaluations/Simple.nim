import .. / .. / Engine / [Config, State]

func evaluateStateSimple*(config: Config, state: State): float =
  var score = 0

  # Death.
  if state.op.health <= 0: score += 1000
  if state.me.health <= 0: score -= 1000

  # Health diff.
  score += (state.me.health - state.op.health) * 2

  for index in state.me.boards.low .. state.me.boards.high:
    # Card count.
    score += (state.me.boards[index].len - state.op.boards[index].len) * 10

    # Card strength.
    for card in state.me.boards[index]: score += card.attack + card.defense
    for card in state.op.boards[index]: score -= card.attack + card.defense

  score.float

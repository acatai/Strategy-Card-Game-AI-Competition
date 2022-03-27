import std / math
import .. / .. / Engine / [Card, Config, Draft, State]

func evaluateDraftIcebox*(config: Config, state: State): DraftResult =
  state.evaluateDraftWith(func (card: Card): float =
    let healthDiff = card.myHealthChange - card.opHealthChange

    result += card.attack.float
    result += card.defense.float
    result -= 6.392651 * 0.001 * pow(card.cost.float, 2)
    result -= 1.463006 * card.cost.float
    result -= 1.435985
    result += 5.219
    result += 5.985350469 * 0.01 * pow(healthDiff.float, 2)
    result += 3.880957 * 0.1 * (card.myHealthChange - card.opHealthChange).float
    result -= 1.63766 * 0.1
    result -= 5.516179907 * pow(card.cardDraw.float, 2)
    result += 0.239521 * card.cardDraw.float
    result -= 7.751401869 * 0.01

    if card.hasBreakthrough: result += 0.0
    if card.hasCharge: result += 0.26015517
    if card.hasDrain: result += 0.15241379
    if card.hasGuard: result += 0.04418965
    if card.hasLethal: result += 0.15313793
    if card.hasWard: result += 0.16238793
  )

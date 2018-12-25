import std / strformat
import Action, Card, Constants, Gamer, Input

type
  State * = ref object
    halt *: bool
    me   *: Gamer
    op   *: Gamer

func applyAction * (state: var State, action: Action): void =
  var me = state.me
  var op = state.op

  case action.actionType:
    of attack:
      var attacker: Card
      var attackerBoard: int
      var attackerIndex: int
      for lane, board in me.boards:
        for index, card in board:
          if card.instanceId == action.id1:
            attacker = card
            attackerBoard = lane
            attackerIndex = index
            break

      var attackerAfter = attacker.copy
      attackerAfter.attackState = alreadyAttacked

      if action.id2 == -1:
        if attacker.hasDrain:
          me.modifyHealth(attacker.attack)
        op.modifyHealth(-attacker.attack)
        me.boards[attackerBoard][attackerIndex] = attackerAfter
      else:
        var defender: Card
        var defenderBoard: int
        var defenderIndex: int
        for lane, board in op.boards:
          for index, card in board:
            if card.instanceId == action.id2:
              defender = card
              defenderBoard = lane
              defenderIndex = index
              break

        var defenderAfter = defender.copy

        if defender.hasWard: defenderAfter.hasWard = attacker.attack == 0
        if attacker.hasWard: attackerAfter.hasWard = defender.attack == 0

        var damageGiven = if defender.hasWard: 0 else: attacker.attack
        var damageTaken = if attacker.hasWard: 0 else: defender.attack
        var healthGain  = 0
        var healthTaken = 0

        # attacking
        if damageGiven >= defender.defense: defenderAfter = nil
        if attacker.hasBreakthrough and defenderAfter == nil:
          healthTaken = defender.defense - damageGiven
        if attacker.hasLethal and damageGiven > 0: defenderAfter = nil
        if attacker.hasDrain and damageGiven > 0: healthGain = attacker.attack
        if defenderAfter != nil: defenderAfter.defense -= damageGiven

        # defending
        if damageTaken >= attacker.defense: attackerAfter = nil
        if defender.hasLethal and damageTaken > 0: attackerAfter = nil
        if attackerAfter != nil: attackerAfter.defense -= damageTaken

        if attackerAfter == nil:
          me.boards[attackerBoard].delete(attackerIndex)
        else:
          me.boards[attackerBoard][attackerIndex] = attackerAfter

        if defenderAfter == nil:
          op.boards[defenderBoard].delete(defenderIndex)
        else:
          op.boards[defenderBoard][defenderIndex] = defenderAfter

        me.modifyHealth(healthGain)
        op.modifyHealth(healthTaken)
    of pass:
      state.halt = true
    of summon:
      var card: Card
      for cardIndex, cardOnHand in me.hand:
        if cardOnHand.instanceId == action.id:
          card = cardOnHand.copy
          me.hand.delete(cardIndex)
          me.handsize -= 1
          break

      card.attackState = if card.hasCharge: canAttack else: noAttack
      me.boards[action.lane].add(card)
      me.currentMana -= card.cost
      me.nextTurnDraw += card.cardDraw
      me.modifyHealth(card.myHealthChange)
      op.modifyHealth(card.opHealthChange)
    of use:
      var item: Card
      for cardIndex, cardOnHand in me.hand:
        if cardOnHand.instanceId == action.id1:
          item = cardOnHand
          me.hand.delete(cardIndex)
          me.handsize -= 1
          break

      me.currentMana -= item.cost
      me.nextTurnDraw += item.cardDraw
      me.modifyHealth(item.myHealthChange)
      op.modifyHealth(item.opHealthChange)

      if action.id2 == -1:
        op.modifyHealth(-item.defense)
      else:
        let targetOwner = if item.cardType == itemGreen: me else: op

        var target: Card
        var targetBoard: int
        var targetIndex: int
        for lane, board in targetOwner.boards:
          for index, card in board:
            if card.instanceId == action.id2:
              target = card
              targetBoard = lane
              targetIndex = index
              break

        var targetAfter = target.copy

        case item.cardType:
          of creature:
            discard "Shouldn't happen."
          of itemBlue, itemRed:
            targetAfter.hasCharge =
              target.hasCharge and not item.hasCharge
            targetAfter.hasBreakthrough =
              target.hasBreakthrough and not item.hasBreakthrough
            targetAfter.hasDrain =
              target.hasDrain and not item.hasDrain
            targetAfter.hasGuard =
              target.hasGuard and not item.hasGuard
            targetAfter.hasLethal =
              target.hasLethal and not item.hasLethal
            targetAfter.hasWard =
              target.hasWard and not item.hasWard

            targetAfter.attack = max(0, target.attack - item.attack)

            if item.defense > 0:
              if targetAfter.hasWard:
                targetAfter.hasWard = false
              else:
                targetAfter.defense -= item.defense
          of itemGreen:
            targetAfter.hasCharge =
              target.hasCharge or item.hasCharge
            targetAfter.hasBreakthrough =
              target.hasBreakthrough or item.hasBreakthrough
            targetAfter.hasDrain =
              target.hasDrain or item.hasDrain
            targetAfter.hasGuard =
              target.hasGuard or item.hasGuard
            targetAfter.hasLethal =
              target.hasLethal or item.hasLethal
            targetAfter.hasWard =
              target.hasWard or item.hasWard

            targetAfter.attack += item.attack
            targetAfter.defense += item.defense

            if item.hasCharge and targetAfter.attackState != alreadyAttacked:
              targetAfter.attackState = canAttack

        if targetAfter.defense <= 0:
          targetOwner.boards[targetBoard].delete(targetIndex)
        else:
          targetOwner.boards[targetBoard][targetIndex] = targetAfter

proc computeActions * (state: State): seq[Action] =
  if state.halt:
    return

  # PASS
  result.add(newActionPass())

  # SUMMON [id] [lane]
  for lane, board in state.me.boards:
    if board.len < MaxInLane:
      for card in state.me.hand:
        if card.cardType == creature and card.cost <= state.me.currentMana:
          result.add(newActionSummon(card.instanceId, lane))

  # ATTACK [id1] [id2]
  for lane, board in state.op.boards:
    var targets: seq[int]
    for card in board:
      if card.hasGuard:
        targets.add(card.instanceId)

    if targets.len == 0:
      targets.add(-1)
      for card in board:
        targets.add(card.instanceId)

    for card in state.me.boards[lane]:
      if card.attackState == canAttack:
        for target in targets:
          result.add(newActionAttack(card.instanceId, target))

  # USE [id1] [id2]
  for card in state.me.hand:
    if card.cardType != creature and card.cost <= state.me.currentMana:
      if card.cardType == itemGreen:
        for board in state.me.boards:
          for creature in board:
            result.add(newActionUse(card.instanceId, creature.instanceId))
      else:
        if card.cardType == itemBlue:
          result.add(newActionUse(card.instanceId, -1))
        for board in state.op.boards:
          for creature in board:
            result.add(newActionUse(card.instanceId, creature.instanceId))

func copy * (state: State): State {.inline.} =
  State(halt: state.halt, me: state.me.copy, op: state.op.copy)

func isGameOver * (state: State): bool {.inline.} =
  state.me.health <= 0 or state.op.health <= 0

func newState * (): State {.inline.} =
  result = State(me: newGamer(), op: newGamer())
  result.op.bonusMana = true

func rechargeMana * (state: var State, turn: int): void =
  var player = state.me
  player.bonusMana = player.bonusMana and (turn == 1 or player.currentMana > 0)
  player.maxMana = min(turn, 12) + (if player.bonusMana: 1 else: 0)
  player.currentMana = player.maxMana

func rechargeCreatures * (state: var State): void =
  for player in [state.me, state.op]:
    for lane in mitems(player.boards):
      for card in mitems(lane):
        card = card.copy
        card.attackState = canAttack

func swap * (state: State): State {.inline.} =
  State(me: state.op, op: state.me)

proc readState * (input: Input): State =
  var state = State()
  state.halt = false
  state.me = input.readGamer
  state.op = input.readGamer
  state.op.handsize = input.getInt

  # Skip opponent actions.
  for index in 1 .. input.getInt:
    discard input.getLine

  for index in 1 .. input.getInt:
    var card = input.readCard
    case card.location:
      of inHand:
        state.me.hand.add(card)
      of myBoard:
        card.attackState = canAttack
        state.me.boards[card.lane].add(card)
      of opBoard:
        card.attackState = canAttack
        state.op.boards[card.lane].add(card)

  state.me.handsize = state.me.hand.len
  state

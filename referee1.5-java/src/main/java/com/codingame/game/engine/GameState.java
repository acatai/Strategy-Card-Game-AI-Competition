package com.codingame.game.engine;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;

/**
 * Created by aCat on 2018-03-20.
 */
public class GameState {
    public int turn;
    public int winner;
    public int currentPlayer;
    public Gamer[] players;
    public HashMap<Integer, Card> cardIdMap;

    public GameState(ConstructPhase constr) {
        assert (constr.decks[0].size() == Constants.CARDS_IN_DECK);
        assert (constr.decks[1].size() == Constants.CARDS_IN_DECK);

        turn = -1;
        winner = -1;
        currentPlayer = 1;
        players = new Gamer[]{new Gamer(0, constr.decks[0]), new Gamer(1, constr.decks[1])};

        cardIdMap = new HashMap<>();
        for (int i = 0; i < 2; i++)
            for (Card c : constr.decks[i])
                cardIdMap.put(c.id, c);
    }

    public List<Action> computeLegalActions() {
        List<Action> legals = new ArrayList<>();
        legals.addAll(computeLegalSummons());
        legals.addAll(computeLegalAttacks());
        legals.addAll(computeLegalItems());
        legals.add(Action.newPass());
        return legals;
    }

    public List<Action> computeLegalSummons() {
        Gamer player = players[currentPlayer];
        ArrayList<Action> actions = new ArrayList<>();

        if (Constants.LANES == 1) {
            if (player.board.size() == Constants.MAX_CREATURES_IN_LINE)
                return actions;

            for (Card c : player.hand) {
                if (c.type != Card.Type.CREATURE || c.cost > player.currentMana)
                    continue;
                actions.add(Action.newSummon(c.id));
            }

            return actions;
        }

        int[] creaturesInline = new int[Constants.LANES];
        for (CreatureOnBoard c : player.board)
            creaturesInline[c.lane]++;

        for (int l = 0; l < Constants.LANES; l++) {
            if (creaturesInline[l] == Constants.MAX_CREATURES_IN_LINE / Constants.LANES)
                continue;

            for (Card c : player.hand) {
                if (c.type != Card.Type.CREATURE || c.cost > player.currentMana)
                    continue;
                actions.add(Action.newSummon(c.id, l));
            }
        }

        return actions;
    }

    private List<Integer> computeLegalTargets(int lane) {
        Gamer enemyPlayer = players[1 - currentPlayer];

        ArrayList<Integer> targets = new ArrayList<>();

        for (CreatureOnBoard c : enemyPlayer.board) // First priority - guards
            if (c.keywords.hasGuard && c.lane == lane)
                targets.add(c.id);

        if (targets.isEmpty()) { // if no guards we can freely attack any creature plus face
            targets.add(-1);
            for (CreatureOnBoard c : enemyPlayer.board)
                if (c.lane == lane)
                    targets.add(c.id);
        }

        return targets;
    }

    public List<Action> computeLegalAttacks() {
        Gamer player = players[currentPlayer];
        ArrayList<Action> actions = new ArrayList<>();
        List<Integer> targets;

        if (Constants.LANES == 1) {
            targets = computeLegalTargets(0);

            for (CreatureOnBoard c : player.board) {
                if (!c.canAttack)
                    continue;
                for (Integer tid : targets)
                    actions.add(Action.newAttack(c.id, tid));
            }
            return actions;
        }

        for (CreatureOnBoard c : player.board) {
            if (!c.canAttack)
                continue;
            targets = computeLegalTargets(c.lane);
            for (Integer tid : targets)
                actions.add(Action.newAttack(c.id, tid));
        }
        return actions;
    }

    public List<Action> computeLegalItems() {
        Gamer player = players[currentPlayer];
        ArrayList<Action> actions = new ArrayList<>();

        for (Card c : player.hand) {
            if (c.type == Card.Type.CREATURE || c.cost > player.currentMana)
                continue;

            if (c.type == Card.Type.ITEM_GREEN) { // on friendly creatures
                for (CreatureOnBoard cb : player.board)
                    actions.add(Action.newUse(c.id, cb.id));
            } else { // red or blue item: on enemy creatures
                for (CreatureOnBoard cb : players[1 - currentPlayer].board)
                    actions.add(Action.newUse(c.id, cb.id));
                if (c.type == Card.Type.ITEM_BLUE) // blue also on the player
                    actions.add(Action.newUse(c.id, -1));
            }
        }

        return actions;
    }


    public void AdvanceState() {
        CheckWinCondition();

        for (CreatureOnBoard c : players[currentPlayer].board) {
            c.canAttack = false;
            c.hasAttacked = false;
        }

        players[currentPlayer].drawValueToShow = players[currentPlayer].nextTurnDraw; // this is the correct way

        currentPlayer = 1 - currentPlayer;
        Gamer player = players[currentPlayer];
        player.performedActions.clear();
        turn++;

        if (player.maxMana < Constants.MAX_MANA + (player.bonusManaTurns > 0 ? 1 : 0))
            player.maxMana += 1;

        if (player.bonusManaTurns > 0 && player.currentMana == 0) {
            player.bonusManaTurns--;
            if (player.bonusManaTurns == 0)
                player.maxMana--;
        }

        player.currentMana = player.maxMana;

        for (CreatureOnBoard c : player.board) {
            c.canAttack = true; // mark ALL creatures as ready to charge
            //if (c.keywords.hasRegenerate && c.defense < c.lastTurnDefense)
            //c.defense = c.lastTurnDefense;
            c.lastTurnDefense = c.defense; // for all creatures (just in case)
        }
        player.DrawCards(player.nextTurnDraw, turn / 2);
        player.drawValueToShow = player.nextTurnDraw;
        player.nextTurnDraw = 1;
        player.healthLostThisTurn = 0;
        CheckWinCondition();
    }

    private int findIndex(int player, int id) {
        int index = -1;
        for (int i = 0; i < players[player].board.size(); i++)
            if (players[player].board.get(i).id == id)
                index = i;
        return index;
    }

    public void AdvanceState(Action action) { // ASSUMING THE ACTION IS LEGAL !
        ActionResult result;
        switch (action.type) {
            case SUMMON: // SUMMON [id] [lane]
                result = AdvanceSummon(action);
                break;
            case ATTACK: // ATTACK [id1] [id2]
                result = AdvanceAttack(action);
                break;
            case USE: // USE [id1] [id2]
                result = AdvanceUse(action);
                break;
            default:
                throw new IllegalStateException("Unexpected value: " + action.type);
        }
        action.result = result;
        players[currentPlayer].ModifyHealth(result.attackingPlayerHealthChange);
        players[1 - currentPlayer].ModifyHealth(result.defendingPlayerHealthChange);
        players[currentPlayer].nextTurnDraw += result.cardDraw;

        players[currentPlayer].performedActions.add(action);
        CheckWinCondition();
    }


    public void CheckWinCondition() {
        if (players[1 - currentPlayer].health <= 0) // first proper win
            winner = currentPlayer;
        else if (players[currentPlayer].health <= 0) // second self-kill
            winner = 1 - currentPlayer;
    }

    private ActionResult AdvanceSummon(Action action) {
        Card c = cardIdMap.get(action.arg1);
        int maxCreaturesPerLane = Constants.MAX_CREATURES_IN_LINE / Constants.LANES;

        players[currentPlayer].hand.remove(c);
        players[currentPlayer].currentMana -= c.cost;
        CreatureOnBoard creature = (Constants.LANES == 1) ? new CreatureOnBoard(c, 0) : new CreatureOnBoard(c, action.arg2);
        players[currentPlayer].board.add(creature);

        int countSummons = 1;
        List<CreatureOnBoard> creatures = new ArrayList<>();
        creatures.add(creature);

        if (Constants.LANES > 1 && c.area == Card.Area.LANE1 && players[currentPlayer].board.stream().filter(c2 -> c2.lane == action.arg2).count() < maxCreaturesPerLane) {
            Card cardCopy = new Card(c, true);
            CreatureOnBoard secondCopy = new CreatureOnBoard(cardCopy, action.arg2);
            cardIdMap.put(cardCopy.id, cardCopy);
            players[currentPlayer].board.add(secondCopy);

            creatures.add(secondCopy);
            countSummons += 1;
        } else if (Constants.LANES > 1 && c.area == Card.Area.LANE2 && players[currentPlayer].board.stream().filter(c2 -> (1 - c2.lane) == action.arg2).count() < maxCreaturesPerLane) {
            for (int i = 0; i < Constants.LANES; i++) {
                if (i == action.arg2)
                    continue;
                Card cardCopy = new Card(c, true);
                CreatureOnBoard creatureCopy = new CreatureOnBoard(cardCopy, i);
                cardIdMap.put(cardCopy.id, cardCopy);
                players[currentPlayer].board.add(creatureCopy);

                creatures.add(creatureCopy);
                countSummons += 1;
            }
        }
        return new SummonResult(creatures, countSummons * c.myHealthChange, countSummons * c.oppHealthChange, countSummons * c.cardDraw);
    }

    private ActionResult AdvanceAttack(Action action) {
        AttackResult result;
        int indexAtt = findIndex(currentPlayer, action.arg1);
        CreatureOnBoard att = players[currentPlayer].board.get(indexAtt);

        if (!att.canAttack)
            return new InvalidActionResult();

        if (action.arg2 == -1) { // attacking player
            result = ResolveAttack(att);
        } else { // attacking creature
            int indexDef = findIndex(1 - currentPlayer, action.arg2);
            CreatureOnBoard def = players[1 - currentPlayer].board.get(indexDef);

            result = ResolveAttack(att, def);

            if (result.defenderDied)
                players[1 - currentPlayer].removeFromBoard(indexDef);
            else
                players[1 - currentPlayer].board.set(indexDef, result.defender);
        }

        if (result.attackerDied)
            players[currentPlayer].removeFromBoard(indexAtt);
        else
            players[currentPlayer].board.set(indexAtt, result.attacker);
        return result;
    }

    private UseResult AdvanceUse(Action action) {
        UseResult result;

        Card item = cardIdMap.get(action.arg1);
        players[currentPlayer].hand.remove(item);
        players[currentPlayer].currentMana -= item.cost;

        if (action.arg2 == -1) { // red and blue cards used on player
            result = ResolveUse(item);
        } else {
            int targetPlayer = (item.type == Card.Type.ITEM_GREEN) ? currentPlayer : 1 - currentPlayer;
            int indexTarg = findIndex(targetPlayer, action.arg2);
            CreatureOnBoard targ = players[targetPlayer].board.get(indexTarg);
            List<UseResult.CreatureUseResult> targets = new ArrayList<>();

            switch (item.area) {
                case TARGET:
                    result = ResolveUse(item, targ);
                    if (result.targets.get(0).targetDied)
                        players[targetPlayer].removeFromBoard(indexTarg);
                    else
                        players[targetPlayer].board.set(indexTarg, result.targets.get(0).target);
                    break;
                case LANE1:
                case LANE2: {
                    int countUsages = 0;
                    for (int i = 0; i < players[targetPlayer].board.size(); i++) {
                        CreatureOnBoard potentialTarget = players[targetPlayer].board.get(i);
                        if (item.area != Card.Area.LANE2 && potentialTarget.lane != targ.lane)
                            continue;

                        UseResult partialResult = ResolveUse(item, potentialTarget);
                        if (partialResult.targets.get(0).targetDied) {
                            players[targetPlayer].removeFromBoard(i);
                            i--;
                        } else {
                            players[targetPlayer].board.set(i, partialResult.targets.get(0).target);
                        }
                        targets.addAll(partialResult.targets);
                        countUsages += 1;
                    }
                    result = new UseResult(new CreatureOnBoard(item), targets,
                            countUsages * item.myHealthChange, countUsages * item.oppHealthChange, countUsages * item.cardDraw);
                    break;
                }
                default:
                    throw new IllegalStateException("Unexpected value: " + item.area);
            }
        }
        return result;
    }

    // when creature attacks creatures // run it ONLY on legal actions
    private AttackResult ResolveAttack(CreatureOnBoard attacker, CreatureOnBoard defender) {
        CreatureOnBoard attackerAfter = new CreatureOnBoard(attacker);
        CreatureOnBoard defenderAfter = new CreatureOnBoard(defender);

        attackerAfter.canAttack = false;
        attackerAfter.hasAttacked = true;

        if (defender.keywords.hasWard)
            defenderAfter.keywords.hasWard = attacker.attack == 0;
        if (attacker.keywords.hasWard)
            attackerAfter.keywords.hasWard = defender.attack == 0;

        int damageGiven = defender.keywords.hasWard ? 0 : attacker.attack;
        int damageTaken = attacker.keywords.hasWard ? 0 : defender.attack;
        int healthGain = 0;
        int healthTaken = 0;

        // attacking
        if (damageGiven >= defender.defense)
            defenderAfter = null;
        if (attacker.keywords.hasBreakthrough && defenderAfter == null)
            healthTaken = defender.defense - damageGiven;
        if (attacker.keywords.hasLethal && damageGiven > 0)
            defenderAfter = null;
        if (attacker.keywords.hasDrain && damageGiven > 0)
            healthGain = attacker.attack;
        if (defenderAfter != null)
            defenderAfter.defense -= damageGiven;

        // defending
        if (damageTaken >= attacker.defense)
            attackerAfter = null;
        if (defender.keywords.hasLethal && damageTaken > 0)
            attackerAfter = null;
        if (attackerAfter != null)
            attackerAfter.defense -= damageTaken;
        return new AttackResult(attackerAfter == null ? attacker : attackerAfter, defenderAfter == null ? defender : defenderAfter,
                attackerAfter == null, defenderAfter == null,
                healthGain, healthTaken, 0, -damageTaken, -damageGiven);
    }

    // when creature attacks player // run it ONLY on legal actions
    private AttackResult ResolveAttack(CreatureOnBoard attacker) {
        CreatureOnBoard attackerAfter = new CreatureOnBoard(attacker);

        attackerAfter.canAttack = false;
        attackerAfter.hasAttacked = true;

        int healthGain = attacker.keywords.hasDrain ? attacker.attack : 0;
        int healthTaken = -attacker.attack;

        return new AttackResult(attackerAfter, healthGain, healthTaken, 0);
    }

    // when item is used on a creature // run it ONLY on legal actions
    private UseResult ResolveUse(Card item, CreatureOnBoard target) {
        CreatureOnBoard targetAfter = new CreatureOnBoard(target);

        if (item.type == Card.Type.ITEM_GREEN) { // add keywords
            targetAfter.keywords.hasCharge = target.keywords.hasCharge || item.keywords.hasCharge;
            if (item.keywords.hasCharge)
                targetAfter.canAttack = !targetAfter.hasAttacked; // No Swift Strike hack
            targetAfter.keywords.hasBreakthrough = target.keywords.hasBreakthrough || item.keywords.hasBreakthrough;
            targetAfter.keywords.hasDrain = target.keywords.hasDrain || item.keywords.hasDrain;
            targetAfter.keywords.hasGuard = target.keywords.hasGuard || item.keywords.hasGuard;
            targetAfter.keywords.hasLethal = target.keywords.hasLethal || item.keywords.hasLethal;
            //targetAfter.keywords.hasRegenerate   = target.keywords.hasRegenerate   || item.keywords.hasRegenerate;
            targetAfter.keywords.hasWard = target.keywords.hasWard || item.keywords.hasWard;
        } else { // Assumming ITEM_BLUE or ITEM_RED - remove keywords
            targetAfter.keywords.hasCharge = target.keywords.hasCharge && !item.keywords.hasCharge;
            targetAfter.keywords.hasBreakthrough = target.keywords.hasBreakthrough && !item.keywords.hasBreakthrough;
            targetAfter.keywords.hasDrain = target.keywords.hasDrain && !item.keywords.hasDrain;
            targetAfter.keywords.hasGuard = target.keywords.hasGuard && !item.keywords.hasGuard;
            targetAfter.keywords.hasLethal = target.keywords.hasLethal && !item.keywords.hasLethal;
            //targetAfter.keywords.hasRegenerate   = target.keywords.hasRegenerate   && !item.keywords.hasRegenerate;
            targetAfter.keywords.hasWard = target.keywords.hasWard && !item.keywords.hasWard;
        }

        targetAfter.attack = Math.max(0, target.attack + item.attack);

        if (targetAfter.keywords.hasWard && item.defense < 0)
            targetAfter.keywords.hasWard = false;
        else
            targetAfter.defense += item.defense;
        if (targetAfter.defense <= 0)
            targetAfter = null;

        int itemgiverHealthChange = item.myHealthChange;
        int targetHealthChange = item.oppHealthChange;

        UseResult.CreatureUseResult creatureResult = new UseResult.CreatureUseResult(
                targetAfter == null ? target : targetAfter, targetAfter == null,
                item.attack, item.defense);

        return new UseResult(new CreatureOnBoard(item), Collections.singletonList(creatureResult), itemgiverHealthChange, targetHealthChange, item.cardDraw);
    }

    // when item is used on a player // run it ONLY on legal actions
    private UseResult ResolveUse(Card item) {
        int itemgiverHealthChange = item.myHealthChange;
        int targetHealthChange = item.defense + item.oppHealthChange;

        return new UseResult(new CreatureOnBoard(item), itemgiverHealthChange, targetHealthChange, item.cardDraw);
    }

    // old method
    public String[] toStringLines() {
        ArrayList<String> lines = new ArrayList<>();

        Gamer player = players[currentPlayer];
        Gamer opponent = players[1 - currentPlayer];

        lines.add(String.valueOf(turn));
        lines.add(String.format("%d %d %d %d %d %d", player.health, player.maxMana, player.nextTurnDraw, player.hand.size(), player.board.size(), player.deck.size()));
        for (Card c : player.hand)
            lines.add(c.toString());
        for (CreatureOnBoard b : player.board)
            lines.add(b.toString());
        lines.add(String.format("%d %d %d %d %d %d %d", opponent.health, opponent.maxMana, opponent.nextTurnDraw, opponent.hand.size(), opponent.board.size(), opponent.deck.size(), opponent.performedActions.size()));
        for (CreatureOnBoard b : opponent.board)
            lines.add(b.toString());
        for (Action a : opponent.performedActions)
            lines.add(cardIdMap.get(a.arg1).baseId + " " + a.toStringNoText());

        return lines.toArray(new String[0]);
    }

    public String[] getPlayersInput() {
        ArrayList<String> lines = new ArrayList<>();

        Gamer player = players[currentPlayer];
        Gamer opponent = players[1 - currentPlayer];
        lines.add(player.getPlayerInput());
        lines.add(opponent.getPlayerInput());

        return lines.toArray(new String[0]);
    }

    public String[] getCardsInput() {
        ArrayList<String> lines = new ArrayList<>();

        Gamer player = players[currentPlayer];
        Gamer opponent = players[1 - currentPlayer];

        lines.add(String.valueOf(opponent.hand.size()) + " " + String.valueOf(opponent.performedActions.size()));
        for (Action a : opponent.performedActions)
            lines.add(String.valueOf(cardIdMap.get(a.arg1).baseId) + " " + a.toStringNoText());

        int cardCount = player.hand.size() + player.board.size() + opponent.board.size();
        lines.add(String.valueOf(cardCount));

        for (Card c : player.hand)
            lines.add(c.getAsInput());
        for (CreatureOnBoard b : player.board)
            lines.add(b.getAsInput(false));
        for (CreatureOnBoard b : opponent.board)
            lines.add(b.getAsInput(true));
        return lines.toArray(new String[0]);
    }

    public String toString() {
        StringBuilder sb = new StringBuilder();

        for (String line : getPlayersInput())
            sb.append(line).append("\n");
        for (String line : getPlayersInput())
            sb.append(line).append("\n");

        return sb.toString();
    }
}

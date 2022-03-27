import java.util.*;
import java.util.concurrent.ThreadLocalRandom;
import java.util.stream.Collectors;

import static java.lang.Math.abs;

class Player {

    private static int MY_HEALTH;
    private static int MY_MANA;
    private static int myDeck;
    private static int myRune;
    private static int myDraw;
    private static int ENEMY_HEALTH;
    private static int ENEMY_MANA;
    private static int enemyDeck;
    private static int enemyRune;
    private static int enemyDraw;

    private static int ENEMY_HAND_COUNT;
    private static int enemyActionsCount;

    private static final int[] DRAFT_SORTED = {116, 68, 151, 51, 65, 80, 7, 53, 29, 37, 67, 32, 139, 69, 49, 33, 66, 147, 18, 152, 28, 48, 82, 88, 23, 84, 52, 44, 87, 148, 99, 121, 64, 85, 103, 141, 158, 50, 95, 115, 133, 19, 109, 54, 157, 81, 150, 21, 34, 36, 135, 134, 70, 3, 61, 111, 75, 17, 144, 129, 145, 106, 9, 105, 15, 114, 128, 155, 96, 11, 8, 86, 104, 97, 41, 12, 26, 149, 90, 6, 13, 126, 93, 98, 83, 71, 79, 72, 73, 77, 59, 100, 137, 5, 89, 142, 112, 25, 62, 125, 122, 74, 120, 159, 22, 91, 39, 94, 127, 30, 16, 146, 1, 45, 38, 56, 47, 4, 58, 118, 119, 40, 27, 35, 101, 123, 132, 2, 136, 131, 20, 76, 14, 43, 102, 108, 46, 60, 130, 117, 140, 42, 124, 24, 63, 10, 154, 78, 31, 57, 138, 107, 113, 55, 143, 92, 156, 110, 160, 153};
    private static Map<Integer, Integer> DRAFT_VALUE;

    private static List<Card> MY_HAND;
    private static List<Card> MY_BOARD;
    private static List<Card> ENEMY_BOARD;

    private static List<String> ENEMY_ACTIONS;

    private static String getNewLane() {
        return " " + ThreadLocalRandom.current().nextInt(2);
    }

    private static void initDraft() {
        DRAFT_VALUE = new HashMap<>();
        for (int i = 0; i < DRAFT_SORTED.length; ++i)
            DRAFT_VALUE.put(DRAFT_SORTED[i], 200 - i);
    }

    public static void main(String args[]) {
        Scanner in = new Scanner(System.in);
        initDraft();
        // game loop
        while (true) {
            MY_HEALTH = in.nextInt();
            MY_MANA = in.nextInt();
            myDeck = in.nextInt();
            myRune = in.nextInt();
            myDraw = in.nextInt();
            ENEMY_HEALTH = in.nextInt();
            ENEMY_MANA = in.nextInt();
            enemyDeck = in.nextInt();
            enemyRune = in.nextInt();
            enemyDraw = in.nextInt();

            ENEMY_HAND_COUNT = in.nextInt();
            enemyActionsCount = in.nextInt();
            if (in.hasNextLine()) {
                in.nextLine();
            }
            ENEMY_ACTIONS = new ArrayList<>();
            for (int i = 0; i < enemyActionsCount; i++) {
                ENEMY_ACTIONS.add(in.nextLine());
            }
            int cardCount = in.nextInt();
            MY_HAND = new ArrayList<>();
            MY_BOARD = new ArrayList<>();
            ENEMY_BOARD = new ArrayList<>();
            for (int i = 0; i < cardCount; i++) {
                int cardNumber = in.nextInt();
                int instanceId = in.nextInt();
                int location = in.nextInt();
                int cardType = in.nextInt();
                int cost = in.nextInt();
                int attack = in.nextInt();
                int defense = in.nextInt();
                String abilities = in.next();
                int myHealthChange = in.nextInt();
                int opponentHealthChange = in.nextInt();
                int cardDraw = in.nextInt();
                int lane = in.nextInt();
                Card card = new Card(cardNumber, instanceId, cardType, cost, attack, defense, abilities,
                        myHealthChange, opponentHealthChange, cardDraw, lane);
                if (location == 0)
                    MY_HAND.add(card);
                else if (location == 1)
                    MY_BOARD.add(card);
                else if (location == -1)
                    ENEMY_BOARD.add(card);
            }

            Collections.sort(MY_BOARD);

            if (MY_MANA == 0) {
                pickPhase();
            } else {
                battlePhase();
            }
        }
    }

    private static Card existsGuard(List<Card> board) {
        for (Card card : board)
            if (card.defense > 0 && card.guard)
                return card;
        return null;
    }

    private static void battlePhase() {
        LinkedList<Situation> generated = new LinkedList<>();
        Situation best = new Situation("", MY_HAND, MY_BOARD, ENEMY_BOARD, MY_HEALTH, ENEMY_HEALTH);
        generated.add(best);
        // single card
        for (int index = 0; index < MY_HAND.size(); ++index)
            if (MY_HAND.get(index).cost <= MY_MANA) {
                generated.addAll(generateSituationsForOneCard(index, MY_HAND, MY_BOARD, ENEMY_BOARD));
            }
        // two cards
        for (int index1 = 0; index1 < (MY_HAND.size() - 1); ++index1)
            for (int index2 = index1 + 1; index2 < MY_HAND.size(); ++index2)
                if (MY_HAND.get(index1).cost + MY_HAND.get(index2).cost <= MY_MANA) {
                    generated.addAll(generateSituationsForTwoCards(index1, index2, MY_HAND, MY_BOARD, ENEMY_BOARD));
                }
        // three cards
        for (int index1 = 0; index1 < (MY_HAND.size() - 2); ++index1)
            for (int index2 = index1 + 1; (index2 < MY_HAND.size() - 1); ++index2)
                for (int index3 = index2 + 1; (index3 < MY_HAND.size()); ++index3)
                    if (MY_HAND.get(index1).cost + MY_HAND.get(index2).cost + MY_HAND.get(index3).cost <= MY_MANA) {
                        generated.addAll(generateSituationsForThreeCards(index1, index2, index3, MY_HAND, MY_BOARD, ENEMY_BOARD));
                    }
        int count = generated.size();
        while (++count < 10000 && !generated.isEmpty()) {
            if (count % 1000 == 0)
                System.err.print(count / 1000 + " ");
            Situation current = generated.pollFirst();
//            System.err.println("P: " + current.print());
            if (current.valueOf() > best.valueOf())
                best = current;
            generated.addAll(generateSituationsFromHand(current));
        }
        while (!generated.isEmpty()) {
            Situation current = generated.pollFirst();
            if (current.valueOf() > best.valueOf())
                best = current;
        }
        System.err.println("#@ PROCESSED: " + count);
        if (best == null || best.command.length() == 0)
            System.out.println("PASS");
        else {
            System.err.println(best.print());
            System.out.println(best.command);
        }
    }

    private static Collection<Situation> generateSituationsFromHand(Situation situation) {
        Card getUnit = null;
        int chosenIndex = -1;
        for (int i = 0; i < situation.myBoard.size(); ++i) {
            Card unit = situation.myBoard.get(i);
            if (!unit.used) {
                getUnit = unit;
                chosenIndex = i;
                break;
            }
        }
        if (getUnit == null) {
            return Collections.emptyList();
        }

        Card enemyGuard = existsGuard(situation.enemyBoard);
        boolean enemyHasGuard = enemyGuard != null;
        // tryb atakowania guarda pierwszym co mogę go pokonać
        if (enemyHasGuard) {
            for (int i = 0; i < situation.myBoard.size(); ++i) {
                Card unit = situation.myBoard.get(i);
                if (!unit.used && canKill(enemyGuard, unit)) {
                    getUnit = unit;
                    chosenIndex = i;
//                    System.err.println("#@ Can kill enemy guard: " + enemyGuard.instanceId + " with my: " + unit.instanceId);
                    break;
                }
            }
        }

        Card myUnit = copy(getUnit);
        myUnit.used = true;
        Collection<Situation> result = new LinkedList<>();
        if (!enemyHasGuard) {
            String command = situation.command + "; ATTACK " + myUnit.instanceId + " -1";
            List<Card> myNewBoard = copyListWithout(chosenIndex, situation.myBoard);
            myNewBoard.add(myUnit);
            int myHP = situation.myHealth;
            if (myUnit.drain)
                myHP += myUnit.attack;
            Situation newSituation = new Situation(command, situation.myHand, myNewBoard, situation.enemyBoard, myHP, situation.enemyHealth - myUnit.attack);
            result.add(newSituation);
        }
        if (situation.enemyBoard.size() > 0) {
            for (int enemyUnitIndex = 0; enemyUnitIndex < situation.enemyBoard.size(); ++enemyUnitIndex) {
                Card enemyUnit = situation.enemyBoard.get(enemyUnitIndex);
                if ((!enemyHasGuard || enemyUnit.guard) && (enemyUnit.lane == myUnit.lane)) {
                    Card enemyUnitAfterBattle = getAfterBattle(enemyUnit, myUnit);
                    Card myUnitAfterBattle = getAfterBattle(myUnit, enemyUnit);
                    List<Card> myNewBoard = copyListWithout(chosenIndex, situation.myBoard);
                    List<Card> enemyNewBoard = copyListWithout(enemyUnitIndex, situation.enemyBoard);
                    int myHP = situation.myHealth;
                    if (myUnit.drain)
                        myHP += Math.min(myUnit.attack, enemyUnit.defense);
                    if (myUnitAfterBattle != null) {
                        myUnitAfterBattle.used = true;
                        myNewBoard.add(myUnitAfterBattle);
                    }
                    int enemyHP = situation.enemyHealth;
                    if (enemyUnitAfterBattle != null)
                        enemyNewBoard.add(enemyUnitAfterBattle);
                    else if (myUnit.breakthrough)
                        enemyHP -= myUnit.attack - enemyUnit.defense;
                    String command = situation.command + "; ATTACK " + myUnit.instanceId + " " + enemyUnit.instanceId;
                    Situation newSituation = new Situation(command, situation.myHand, myNewBoard, enemyNewBoard, myHP, enemyHP);
                    result.add(newSituation);
                }
            }
        }
        // without attack:
        {
            List<Card> myNewBoard = copyListWithout(chosenIndex, situation.myBoard);
            myNewBoard.add(myUnit);
            Situation newSituation = new Situation(situation.command, situation.myHand, myNewBoard, situation.enemyBoard, situation.myHealth, situation.enemyHealth);
            result.add(newSituation);
        }
        return result;
    }

    private static boolean canKill(Card enemyGuard, Card myUnit) {
        return !enemyGuard.ward && (myUnit.lethal || myUnit.attack >= enemyGuard.defense);
    }

    private static Collection<Situation> generateSituationsForThreeCards(int index1, int index2, int index3, List<Card> myHand, List<Card> myBoard, List<Card> enemyBoard) {
        List<Situation> result = new ArrayList<>();
        Card card1 = myHand.get(index1);
        Card card2 = myHand.get(index2);
        Card card3 = myHand.get(index3);
        int units = (card1.cardType == 0 ? 1 : 0) + (card2.cardType == 0 ? 1 : 0) + (card3.cardType == 0 ? 1 : 0);
        if (units <= 1 || units + myBoard.size() > 6)
            return result;
        int myHP = MY_HEALTH;
        int enemyHP = ENEMY_HEALTH;
        List<Card> myNewHand = copyListWithout(index1, index2, index3, myHand);
        List<Card> myNewBoard = new ArrayList<>(myBoard);
        String command = "";
        if (card1.cardType == 0) {
            Card myUnit = copy(card1);
            myNewBoard.add(myUnit);
            if (!myUnit.charge)
                myUnit.used = true;
            else
                Collections.sort(myNewBoard);
            command = "SUMMON " + myUnit.instanceId + getNewLane();
            myHP += myUnit.myHealthChange;
            enemyHP += myUnit.opponentHealthChange;
        }
        if (card2.cardType == 0) {
            Card myUnit = copy(card2);
            myNewBoard.add(myUnit);
            if (!myUnit.charge)
                myUnit.used = true;
            else
                Collections.sort(myNewBoard);
            command += ";SUMMON " + myUnit.instanceId + getNewLane();
            myHP += myUnit.myHealthChange;
            enemyHP += myUnit.opponentHealthChange;
        }
        if (card3.cardType == 0) {
            Card myUnit = copy(card3);
            myNewBoard.add(myUnit);
            if (!myUnit.charge)
                myUnit.used = true;
            else
                Collections.sort(myNewBoard);
            command += ";SUMMON " + myUnit.instanceId + getNewLane();
            myHP += myUnit.myHealthChange;
            enemyHP += myUnit.opponentHealthChange;
        }
        if (units == 3) {
            Situation situation = new Situation(command, myNewHand, myNewBoard, enemyBoard, myHP, enemyHP);
            result.add(situation);
            return result;
        }
        processRedItem(myNewBoard, enemyBoard, result, card1, myNewHand, command, myHP, enemyHP);
        processRedItem(myNewBoard, enemyBoard, result, card2, myNewHand, command, myHP, enemyHP);
        processRedItem(myNewBoard, enemyBoard, result, card3, myNewHand, command, myHP, enemyHP);

        processGreenItem(enemyBoard, result, card1, myNewHand, myNewBoard, command, myHP, enemyHP);
        processGreenItem(enemyBoard, result, card2, myNewHand, myNewBoard, command, myHP, enemyHP);
        processGreenItem(enemyBoard, result, card3, myNewHand, myNewBoard, command, myHP, enemyHP);

        return result;
    }

    private static Collection<Situation> generateSituationsForTwoCards(int index1, int index2, List<Card> myHand, List<Card> myBoard, List<Card> enemyBoard) {
        Collection<Situation> result = new ArrayList<>();
        Card card1 = myHand.get(index1);
        Card card2 = myHand.get(index2);
        int units = (card1.cardType == 0 ? 1 : 0) + (card2.cardType == 0 ? 1 : 0);
        if (units == 0 || units + myBoard.size() > 6)
            return result;
        int myHP = MY_HEALTH;
        int enemyHP = ENEMY_HEALTH;
        List<Card> myNewHand = copyListWithout(index1, index2, myHand);
        List<Card> myNewBoard = new ArrayList<>(myBoard);
        String command = "";
        if (card1.cardType == 0) {
            Card myUnit = copy(card1);
            myNewBoard.add(myUnit);
            if (!myUnit.charge)
                myUnit.used = true;
            else
                Collections.sort(myNewBoard);
            command = "SUMMON " + myUnit.instanceId + getNewLane();
            myHP += myUnit.myHealthChange;
            enemyHP += myUnit.opponentHealthChange;
        }
        if (card2.cardType == 0) {
            Card myUnit = copy(card2);
            myNewBoard.add(myUnit);
            if (!myUnit.charge)
                myUnit.used = true;
            else
                Collections.sort(myNewBoard);
            command += ";SUMMON " + myUnit.instanceId + getNewLane();
            myHP += myUnit.myHealthChange;
            enemyHP += myUnit.opponentHealthChange;
        }
        if (units == 2) {
            Situation situation = new Situation(command, myNewHand, myNewBoard, enemyBoard, myHP, enemyHP);
            result.add(situation);
            return result;
        }
        processRedItem(myNewBoard, enemyBoard, result, card1, myNewHand, command, myHP, enemyHP);
        processRedItem(myNewBoard, enemyBoard, result, card2, myNewHand, command, myHP, enemyHP);

        processGreenItem(enemyBoard, result, card1, myNewHand, myNewBoard, command, myHP, enemyHP);
        processGreenItem(enemyBoard, result, card2, myNewHand, myNewBoard, command, myHP, enemyHP);

        return result;
    }

    private static Collection<Situation> generateSituationsForOneCard(int index1, List<Card> myHand, List<Card> myBoard, List<Card> enemyBoard) {
        Collection<Situation> result = new ArrayList<>();
        Card card1 = myHand.get(index1);
        int units = (card1.cardType == 0 ? 1 : 0);
        if (units + myBoard.size() > 6)
            return result;
        int myHP = MY_HEALTH;
        int enemyHP = ENEMY_HEALTH;

        List<Card> myNewHand = copyListWithout(index1, myHand);
        List<Card> myNewBoard = new ArrayList<>(myBoard);
        String command = "";
        if (card1.cardType == 0) {
            Card myUnit = copy(card1);
            myNewBoard.add(myUnit);
            if (!myUnit.charge)
                myUnit.used = true;
            else
                Collections.sort(myNewBoard);
            command = "SUMMON " + myUnit.instanceId + getNewLane();
            myHP += myUnit.myHealthChange;
            enemyHP += myUnit.opponentHealthChange;
        }
        if (units == 1) {
            Situation situation = new Situation(command, myNewHand, myNewBoard, enemyBoard, myHP, enemyHP);
            result.add(situation);
            return result;
        }
        processRedItem(myNewBoard, enemyBoard, result, card1, myNewHand, command, myHP, enemyHP);
        processGreenItem(enemyBoard, result, card1, myNewHand, myNewBoard, command, myHP, enemyHP);

        return result;
    }

    private static void processRedItem(List<Card> myBoard, List<Card> enemyBoard, Collection<Situation> result, Card card1, List<Card> myNewHand, String command, int myHP, int enemyHP) {
        if (card1.cardType == 2 && enemyBoard.size() > 0) {
            myHP += card1.myHealthChange;
            enemyHP += card1.opponentHealthChange;
            for (int enemyUnitIndex = 0; enemyUnitIndex < enemyBoard.size(); ++enemyUnitIndex) {
                Card enemyUnit = enemyBoard.get(enemyUnitIndex);
                List<Card> enemyNewBoard = copyListWithout(enemyUnitIndex, enemyBoard);
                String newCommand = command + ";USE " + card1.instanceId + " " + enemyUnit.instanceId;
                Card enemyUnitAfterCard = getAfterRedItem(enemyUnit, card1);
                if (enemyUnitAfterCard != null)
                    enemyNewBoard.add(enemyUnitAfterCard);
                Situation situation = new Situation(newCommand, myNewHand, myBoard, enemyNewBoard, myHP, enemyHP);
                result.add(situation);
            }
        }
    }

    private static void processGreenItem(List<Card> enemyBoard, Collection<Situation> result, Card card1, List<Card> myNewHand, List<Card> myNewBoard, String command, int myHP, int enemyHP) {
        if (card1.cardType == 1 && myNewBoard.size() > 0) {
            myHP += card1.myHealthChange;
            enemyHP += card1.opponentHealthChange;
            for (int myUnitIndex = 0; myUnitIndex < myNewBoard.size(); ++myUnitIndex) {
                Card myUnit = myNewBoard.get(myUnitIndex);
                List<Card> myNewBoard2 = copyListWithout(myUnitIndex, myNewBoard);
                String newCommand = command + ";USE " + card1.instanceId + " " + myUnit.instanceId;
                Card myUnitAfterCard = getAfterGreenItem(myUnit, card1);
                if (myUnitAfterCard != null)
                    myNewBoard2.add(myUnitAfterCard);
                Situation situation = new Situation(newCommand, myNewHand, myNewBoard2, enemyBoard, myHP, enemyHP);
                result.add(situation);
            }
        }
    }

    private static Card getAfterGreenItem(Card unit, Card item) {
        Card result = copy(unit);
        if (item.guard)
            result.guard = true;
        if (item.ward)
            result.ward = true;
        if (item.lethal)
            result.lethal = true;
        if (item.drain)
            result.drain = true;
        if (item.breakthrough)
            result.breakthrough = true;
        if (item.charge) {
            result.charge = true;
            unit.used = false;
        }
        result.defense += item.defense;
        result.attack += item.attack;
        return result;
    }

    private static Card getAfterRedItem(Card unit, Card item) {
        Card result = copy(unit);
        if (item.guard)
            result.guard = false;
        if (item.ward)
            result.ward = false;
        if (item.lethal)
            result.lethal = false;
        if (item.drain)
            result.drain = false;
        if (item.breakthrough)
            result.breakthrough = false;
        if (item.charge)
            result.charge = false;
        if (item.defense < 0) {
            if (result.ward)
                result.ward = false;
            else
                result.defense += item.defense;
            if (result.defense <= 0)
                return null;
        }
        result.attack += item.attack;
        if (result.attack < 0)
            result.attack = 0;
        return result;
    }

    private static Card getAfterBattle(Card defender, Card attacker) {
        if (defender.ward)
            return copyWithoutWard(defender);
        else if (attacker.attack >= defender.defense || attacker.lethal)
            return null;
        else {
            Card result = copy(defender);
            result.defense -= attacker.attack;
            return result;
        }
    }

    private static Card copyWithoutWard(Card c) {
        return new Card(c.cardNumber, c.instanceId, c.cardType, c.cost, c.attack, c.defense, c.abilities, c.myHealthChange, c.opponentHealthChange, c.cardDraw, c.guard, c.charge, c.breakthrough, c.drain, c.lethal, false, c.used, c.lane);
    }

    private static Card copy(Card c) {
        return new Card(c.cardNumber, c.instanceId, c.cardType, c.cost, c.attack, c.defense, c.abilities, c.myHealthChange, c.opponentHealthChange, c.cardDraw, c.guard, c.charge, c.breakthrough, c.drain, c.lethal, c.ward, c.used, c.lane);
    }

    private static List<Card> copyListWithout(int index, List<Card> list) {
        List<Card> result = new ArrayList<>();
        for (int i = 0; i < list.size(); ++i)
            if (i != index)
                result.add(list.get(i));
        return result;
    }

    private static List<Card> copyListWithout(int index1, int index2, List<Card> list) {
        List<Card> result = new ArrayList<>();
        for (int i = 0; i < list.size(); ++i)
            if (i != index1 && i != index2)
                result.add(list.get(i));
        return result;
    }

    private static List<Card> copyListWithout(int index1, int index2, int index3, List<Card> list) {
        List<Card> result = new ArrayList<>();
        for (int i = 0; i < list.size(); ++i)
            if (i != index1 && i != index2 && i != index3)
                result.add(list.get(i));
        return result;
    }

    private static int cardValueDraft(Card card) {
        if (card.cardType == 3)
            return 0;
        if (!DRAFT_VALUE.containsKey(card.cardNumber))
            System.err.println("WTF ?!?: " + card.cardNumber);
        return DRAFT_VALUE.get(card.cardNumber);
    }

    private static void pickPhase() {
        Card card = MY_HAND.get(0);
        double max = cardValueDraft(card);
        int pick = 0;
        for (int i = 1; i < MY_HAND.size(); ++i) {
            Card tCard = MY_HAND.get(i);
            if (tCard.cardType == 0 || tCard.cardType == 1 || tCard.cardType == 2) {
                double tMax = cardValueDraft(tCard);
                if (tMax > max) {
                    max = tMax;
                    card = tCard;
                    pick = i;
                }
            }
        }
        System.out.println("PICK " + pick);
    }

    static class Situation {
        final String command;
        final List<Card> myHand;
        final List<Card> myBoard;
        final List<Card> enemyBoard;
        final int myHealth;
        final int enemyHealth;
        private Double value;

        public Situation(String command, List<Card> myHand, List<Card> myBoard, List<Card> enemyBoard, int myHealth, int enemyHealth) {
            this.command = command;
            this.myHand = myHand;
            this.myBoard = myBoard;
            this.enemyBoard = enemyBoard;
            this.myHealth = myHealth;
            this.enemyHealth = enemyHealth;
            this.value = null;
        }

        double valueOf() {
            if (value != null)
                return value;
            if (enemyHealth <= 0)
                return 1000000000.0;
            value = enemyHealth * ENEMY_LIFE_PARAM;
            for (Card myCard : myHand)
                value += HAND_PARAM * myCard.valueOf();
            for (Card myCard : myBoard)
                value += MY_PARAM * myCard.valueOf();
            for (Card enemyCard : enemyBoard)
                value -= ENEMY_PARAM * enemyCard.valueOf();
            value += myHealth;
            value -= enemyHealth;
            return value;
        }

        String print() {
            StringBuilder b = new StringBuilder();
            int used = 0;
            for (Card card : myBoard)
                if (card.used)
                    ++used;
            b.append("S: " + valueOf());
            b.append(" U: ");
            b.append(myBoard.stream().map(u -> "" + u.instanceId + (u.used ? "M" : "")).collect(Collectors.joining(", ")));
            return b.toString();
        }
    }

    private final static double ENEMY_LIFE_PARAM = -1.0;
    private final static double ENEMY_PARAM = 1.2;
    private final static double MY_PARAM = 1.0;
    private final static double HAND_PARAM = 0.03;
    private final static double ATTACK_PARAM = 10.0;
    private final static double DEFENSE_PARAM = 6.0;
    private final static double BASE_UNIT_PARAM = 10.0;
    private final static double LETHAL_PARAM = 30.0;
    private final static double WARD_PARAM = 30.0;
    private final static double GUARD_PARAM = 20.0;
    private final static double BREAK_PARAM = 0.0;
    private final static double DRAIN_PARAM = 10.0;
    private final static double DRAIN_MULTI = 2.0;
    private final static double GUARD_MULTI = 2.0;
    private final static double WARD_MULTI = 2.0;

    static class Card implements Comparable<Card> {
        int cardNumber;
        int instanceId;
        int cardType;
        // 0: Creature
        // 1: Green item
        // 2: Red item
        // 3: Blue item
        int cost;
        int attack;
        int defense;
        String abilities;
        int myHealthChange;
        int opponentHealthChange;
        int cardDraw;
        boolean guard;
        boolean charge;
        boolean breakthrough;
        boolean drain;
        boolean lethal;
        boolean ward;
        boolean used;
        int lane;
        // Breakthrough: Creatures with Breakthrough can deal extra damage to the opponent when they attack enemy
        //      creatures. If their attack damage is greater than the defending creature's defense, the excess damage is dealt to the opponent.
        // Charge: Creatures with Charge can attack the turn they are summoned.
        // Drain: Creatures with Drain heal the player of the amount of the damage they deal (when attacking only).
        // Guard: Enemy creatures must attack creatures with Guard first.
        // Lethal: Creatures with Lethal kill the creatures they deal damage to.
        // Ward: Creatures with Ward ignore once the next damage they would receive from any source. The "shield"
        //      given by the Ward ability is then lost.
        private Double value;

        double valueOf() {
            if (value != null)
                return value;
            value = ATTACK_PARAM * abs(attack) + DEFENSE_PARAM * abs(defense);
            if (cardType == 0) {
                value += BASE_UNIT_PARAM;
                if (lethal)
                    value += LETHAL_PARAM;
                if (ward)
                    value += WARD_PARAM + attack * WARD_MULTI;
                if (guard)
                    value += GUARD_PARAM + defense * GUARD_MULTI;
                if (breakthrough)
                    value += BREAK_PARAM;
                if (drain)
                    value += DRAIN_PARAM + attack * DRAIN_MULTI;
            } else {
                if (lethal)
                    value += LETHAL_PARAM;
                if (ward)
                    value += WARD_PARAM;
                if (guard)
                    value += GUARD_PARAM;
                if (breakthrough)
                    value += BREAK_PARAM;
                if (drain)
                    value += DRAIN_PARAM;
                value /= 10.0;
            }
            return value;
        }

        public Card(int cardNumber, int instanceId, int cardType, int cost, int attack, int defense, String abilities, int myHealthChange, int opponentHealthChange, int cardDraw, boolean guard, boolean charge, boolean breakthrough, boolean drain, boolean lethal, boolean ward, boolean used, int lane) {
            this.cardNumber = cardNumber;
            this.instanceId = instanceId;
            this.cardType = cardType;
            this.cost = cost;
            this.attack = attack;
            this.defense = defense;
            this.abilities = abilities;
            this.myHealthChange = myHealthChange;
            this.opponentHealthChange = opponentHealthChange;
            this.cardDraw = cardDraw;
            this.guard = guard;
            this.charge = charge;
            this.breakthrough = breakthrough;
            this.drain = drain;
            this.lethal = lethal;
            this.ward = ward;
            this.used = used;
            this.lane = lane;
        }

        public Card(int cardNumber, int instanceId, int cardType, int cost, int attack, int defense, String abilities, int myHealthChange, int opponentHealthChange, int cardDraw, int lane) {
            this.cardNumber = cardNumber;
            this.instanceId = instanceId;
            this.cardType = cardType;
            this.cost = cost;
            this.attack = attack;
            this.defense = defense;
            this.abilities = abilities;
            this.myHealthChange = myHealthChange;
            this.opponentHealthChange = opponentHealthChange;
            this.cardDraw = cardDraw;
            this.guard = abilities.contains("G");
            this.charge = abilities.contains("C");
            this.breakthrough = abilities.contains("B");
            this.drain = abilities.contains("D");
            this.lethal = abilities.contains("L");
            this.ward = abilities.contains("W");
            this.value = null;
            this.used = false;
            if (cardNumber == 155 || cardNumber == 157 || cardNumber == 158 || cardNumber == 159)
                this.cardType = 2;
            this.lane = lane;
        }

        @Override
        public String toString() {
            return "CARD(" + cardNumber + " ID: " + instanceId + " HP: " + defense + " A: " + abilities + " TYPE: " + cardType +
                    ")";
        }

        @Override
        public int compareTo(Card o) {
            return (int) Math.round(valueOf() - o.valueOf());
        }
    }
}

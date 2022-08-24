import java.io.File;
import java.io.FileNotFoundException;
import java.util.*;
import java.util.stream.Collectors;

import static java.lang.Math.abs;

class Player {

    public static Scanner in;
    public static int MY_HEALTH;
    public static int MY_MANA;
    public static int MY_DECK;
    public static int MY_DRAW;
    public static int ENEMY_HEALTH;
    public static int ENEMY_MANA;
    public static int ENEMY_DECK;
    public static int ENEMY_DRAW;
    public static List<PCard> MY_HAND;
    public static List<PCard> MY_BOARD;
    public static List<PCard> ENEMY_BOARD;
    public static boolean BASE_LOGGING = true;
    public static boolean LOGGING = false;
    public static int MAX_UNIT_ID;

    public static void play() {
        in = new Scanner(System.in);
        MY_HAND = new ArrayList<>();
        MY_BOARD = new ArrayList<>();
        ENEMY_BOARD = new ArrayList<>();
        // game loop
        while (true) {
            MAX_UNIT_ID = 0;
            MY_HAND.clear();
            MY_BOARD.clear();
            ENEMY_BOARD.clear();
            MY_HEALTH = in.nextInt();
            MY_MANA = in.nextInt();
            MY_DECK = in.nextInt();
            MY_DRAW = in.nextInt();
            ENEMY_HEALTH = in.nextInt();
            ENEMY_MANA = in.nextInt();
            ENEMY_DECK = in.nextInt();
            ENEMY_DRAW = in.nextInt();
            if (BASE_LOGGING) {
                System.err.println("ME: " + MY_HEALTH + " : " + MY_MANA + " : " + MY_DECK + " : " + MY_DRAW);
                System.err.println("ENEMY: " + ENEMY_HEALTH + " : " + ENEMY_MANA + " : " + ENEMY_DECK + " : " + ENEMY_DRAW);
            }
            int opponentHand = in.nextInt();
            int opponentActions = in.nextInt();
            if (in.hasNextLine()) {
                in.nextLine();
            }
            for (int i = 0; i < opponentActions; i++) {
                String cardNumberAndAction = in.nextLine();
            }
            int cardCount = in.nextInt();
            if (BASE_LOGGING)
                System.err.println("COUNT: " + cardCount);
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
                int area = in.nextInt();
                int lane = in.nextInt();
                MAX_UNIT_ID = Math.max(instanceId, MAX_UNIT_ID);
                PCard card = new PCard(cardNumber, instanceId, cardType, cost, attack, defense, abilities,
                        myHealthChange, opponentHealthChange, cardDraw, area, lane);
                countValueOf(card);
                if (location == 0)
                    MY_HAND.add(card);
                else if (location == 1)
                    MY_BOARD.add(card);
                else
                    ENEMY_BOARD.add(card);
            }
            if (MY_MANA == 0)
                pickPhase();
            else
                battlePhase();
        }
    }

    public static void battlePhase() {
        if (BASE_LOGGING)
            for (PCard card : MY_HAND)
                System.err.println("HAND: " + card);
        LinkedList<Situation> generated = new LinkedList<>();
        Situation best = new Situation("", MY_HAND, MY_BOARD, ENEMY_BOARD, MY_HEALTH, ENEMY_HEALTH);
        countValueOf(best);
        generated.add(best);
        boolean[] canPlay = new boolean[MY_HAND.size()];
        for (int index = 0; index < MY_HAND.size(); ++index)
            canPlay[index] = canPlayCard(MY_HAND.get(index));
        // single card
        for (int index = 0; index < MY_HAND.size(); ++index)
            if (canPlay[index] && MY_HAND.get(index).cost <= MY_MANA) {
                generated.addAll(generateSituationsForOneCard(index, MY_HAND, MY_BOARD, ENEMY_BOARD));
            }
        // two cards
        for (int index1 = 0; index1 < (MY_HAND.size() - 1); ++index1)
            for (int index2 = index1 + 1; index2 < MY_HAND.size(); ++index2)
                if (canPlay[index1] && canPlay[index2] && MY_HAND.get(index1).cost + MY_HAND.get(index2).cost <= MY_MANA) {
                    generated.addAll(generateSituationsForTwoCards(index1, index2, MY_HAND, MY_BOARD, ENEMY_BOARD));
                }
        if (BASE_LOGGING)
            System.err.println("===== PROCESSING");
        int count = generated.size();
        while (++count < 10000 && !generated.isEmpty()) {
            if (BASE_LOGGING)
                if (count % 500 == 0)
                    System.err.print(count + " ");
            Situation current = generated.pollFirst();
            if (current.value > best.value)
                best = current;
            generated.addAll(generateSituationsFromHand(current));
        }
        while (!generated.isEmpty()) {
            Situation current = generated.pollFirst();
            if (current.value > best.value)
                best = current;
        }
        if (BASE_LOGGING)
            System.err.println("#@ PROCESSED: " + count);
        if (count < 10000) {
            if (BASE_LOGGING)
                System.err.println("===== INIT 3 cards");
            // three cards
            for (int index1 = 0; index1 < (MY_HAND.size() - 2); ++index1)
                for (int index2 = index1 + 1; index2 < (MY_HAND.size() - 1); ++index2)
                    for (int index3 = index2 + 1; index3 < MY_HAND.size(); ++index3)
                        if (canPlay[index1] && canPlay[index2] && canPlay[index3] && MY_HAND.get(index1).cost + MY_HAND.get(index2).cost + MY_HAND.get(index3).cost <= MY_MANA) {
                            generated.addAll(generateSituationsForThreeCards(index1, index2, index3, MY_HAND, MY_BOARD, ENEMY_BOARD));
                        }
            if (BASE_LOGGING)
                System.err.println("===== PROCESSING 3 cards");
            while (++count < 5000 && !generated.isEmpty()) {
                if (count % 500 == 0)
                    System.err.print(count + " ");
                Situation current = generated.pollFirst();
                if (current.value > best.value)
                    best = current;
                generated.addAll(generateSituationsFromHand(current));
            }
            while (!generated.isEmpty()) {
                Situation current = generated.pollFirst();
                if (current.value > best.value)
                    best = current;
            }
            if (BASE_LOGGING)
                System.err.println("#@ PROCESSED_2: " + count);
        }
        if (best == null || best.command.length() == 0)
            System.out.println("PASS");
        else {
            if (BASE_LOGGING)
                System.err.println(best.print() + ": " + best.command);
            System.out.println(best.command);
        }
    }
    static int[] T = {10, 20, 30, 40, 50, 60};
    public static void pickPhase() {
//        MY_HAND.sort(PCard::compareTo);
        List<PCard>[] cards = new List[7];

        for (int cost = 0; cost < 7; ++cost)
            cards[cost] = new ArrayList<>();

        for (PCard card : MY_HAND)
            if (card.cost > 5)
                cards[6].add(card);
            else
                cards[card.cost].add(card);

        for (int cost = 0; cost < 7; ++cost)
            cards[cost].sort(PCard::compareTo);

        int chosen = 0;
        int type0 = 0;
        int type1 = 0;
        int type2 = 0;
        StringBuilder action = new StringBuilder();
        double[] costMulti = new double[6];
        double[] typeMulti = new double[4];
        for (int cost = 0; cost < 6; ++cost)
            costMulti[cost] = COST_DIV_PARAM[cost];
        for (int type = 0; type < 4; ++type)
            typeMulti[type] = 1.0;
        while (chosen < 15) {
            int left = 15 - chosen;
            if (type0 + left <= 5) {
                typeMulti[0] = T[5 - left - type0];
            }
            if (type1 + left <= 3) {
                typeMulti[1] = T[3 - left - type1];
            }
            if (type2 + left <= 0) {
                typeMulti[2] = T[0 - left - type2];
                typeMulti[3] = T[0 - left - type2];
            }
            double bestValue = -1000000;
            PCard bestCard = null;
            int bestCost = -1;
            for (int cost = 0; cost < 6; ++cost)
                if (cards[cost].size() > 0) {
                    double tCost = typeMulti[cards[cost].get(0).cardType] * cards[cost].get(0).value / costMulti[cost];
                    if (tCost > bestValue) {
                        bestValue = tCost;
                        bestCard = cards[cost].get(0);
                        bestCost = cost;
                    }
                }
            if (bestCard != null) {
                action.append(";CHOOSE " + bestCard.cardNumber + " ;CHOOSE " + bestCard.cardNumber);
                cards[bestCost].remove(0);
                costMulti[bestCost] *= COST_MULTI_PARAM[bestCost];
                System.err.println("CHOOSE CARD WITH COST: " + bestCost + " WITH VALUE: " + bestCard.value + ": " + bestCard);
                if (bestCard.cardType == 0)
                    ++type0;
                else if (bestCard.cardType == 1)
                    ++type1;
                else
                    ++type2;
            } else {
                bestCard = cards[6].get(0);
                action.append(";CHOOSE " + bestCard.cardNumber + " ;CHOOSE " + bestCard.cardNumber);
                cards[6].remove(0);
                System.err.println("NO CHIP CARD ?!?");
            }
            ++chosen;
        }
        System.err.println("TYPES: " + type0 + " : " + type1 + " : " + type2);
//
//        for (int i = 0; i < 15; ++i) {
//            action.append(";CHOOSE " + MY_HAND.get(i).cardNumber + " ;CHOOSE " + MY_HAND.get(i).cardNumber);
//            PCard card = MY_HAND.get(i);
//            if (BASE_LOGGING)
//                System.err.println(card.value + ": " + card.cost + ": " + card);
//        }
        System.out.println(action);
    }

    public static void main(String args[]) {
        ENEMY_LIFE_PARAM =          -47024/ 1000000.0;
        MY_LIFE_PARAM =             88485/ 1000000.0;
        ENEMY_PARAM =               -1671352/ 1000000.0;
        MY_PARAM =                  842047/ 1000000.0;
        HAND_PARAM =                60542/ 1000000.0;
        ATTACK_PARAM =              1998731/ 1000000.0;
        DEFENSE_PARAM =             12043949/ 1000000.0;
        BASE_UNIT_PARAM =           272278/ 1000000.0;
        LETHAL_PARAM =              1200363/ 1000000.0;
        WARD_PARAM =                36296353/ 1000000.0;
        GUARD_PARAM =               260789/ 1000000.0;
        BREAK_PARAM =               9153/ 1000000.0;
        DRAIN_PARAM =               4079982/ 1000000.0;
        DRAIN_MULTI =               2004810/ 1000000.0;
        GUARD_MULTI =               2671893/ 1000000.0;
        WARD_MULTI =                141548/ 1000000.0;
        DIFFERENT_LANE_PARAM =      793120/ 1000000.0;
        AREA_PARAM_1_UNIT =         2780620/ 1000000.0;
        AREA_PARAM_1_RED =          146375/ 1000000.0;
        AREA_PARAM_1_GREEN =        2888678/ 1000000.0;
        AREA_PARAM_2_UNIT =         2578454/ 1000000.0;
        AREA_PARAM_2_RED =          27095575/ 1000000.0;
        AREA_PARAM_2_GREEN =        13976037/ 1000000.0;
        GREEN_CARD_PARAM =          248048/ 1000000.0;
        RED_CARD_PARAM =            731334/ 1000000.0;
        COST_DIV_PARAM[0] =         1538156/ 1000000.0;
        COST_DIV_PARAM[1] =         2049300/ 1000000.0;
        COST_DIV_PARAM[2] =         3284400/ 1000000.0;
        COST_DIV_PARAM[3] =         3969000/ 1000000.0;
        COST_DIV_PARAM[4] =         4413768/ 1000000.0;
        COST_DIV_PARAM[5] =         7161000/ 1000000.0;
        COST_MULTI_PARAM[0] =       1355099/ 1000000.0;
        COST_MULTI_PARAM[1] =       1085055/ 1000000.0;
        COST_MULTI_PARAM[2] =       1175849/ 1000000.0;
        COST_MULTI_PARAM[3] =       1272103/ 1000000.0;
        COST_MULTI_PARAM[4] =       1481564/ 1000000.0;
        COST_MULTI_PARAM[5] =       1135760/ 1000000.0;
        play();
    }

    public static Collection<Situation> generateSituationsFromHand(Situation situation) {
        PCard getUnit = null;
        int chosenIndex = -1;
        for (int i = 0; i < situation.myBoard.size(); ++i) {
            PCard unit = situation.myBoard.get(i);
            if (!unit.used) {
                getUnit = unit;
                chosenIndex = i;
                break;
            }
        }
        if (getUnit == null)
            return Collections.emptyList();

        PCard enemyGuard = existsGuard(situation.enemyBoard, getUnit.lane);
        boolean enemyHasGuard = enemyGuard != null;
        // tryb atakowania guarda pierwszym co moge go pokonac
        if (enemyHasGuard) {
            for (int i = 0; i < situation.myBoard.size(); ++i) {
                PCard unit = situation.myBoard.get(i);
                if (enemyGuard.lane == unit.lane && !unit.used && canKill(enemyGuard, unit)) {
                    getUnit = unit;
                    chosenIndex = i;
                    break;
                }
            }
        }

        PCard myUnit = copy(getUnit);
        myUnit.used = true;
        Collection<Situation> result = new LinkedList<>();
        if (!enemyHasGuard) {
            String command;
            if (myUnit.instanceId >= 0)
                command = situation.command + "; ATTACK " + myUnit.instanceId + " -1";
            else {
                command = situation.command + "; ATTACK " + (MAX_UNIT_ID + 1) + " -1";
                command += "; ATTACK " + (MAX_UNIT_ID + 2) + " -1";
                command += "; ATTACK " + (MAX_UNIT_ID + 3) + " -1";
                command += "; ATTACK " + (MAX_UNIT_ID + 4) + " -1";
                command += "; ATTACK " + (MAX_UNIT_ID + 5) + " -1";
            }
            List<PCard> myNewBoard = copyListWithout(chosenIndex, situation.myBoard);
            myNewBoard.add(myUnit);
            int myHP = situation.myHealth;
            if (myUnit.drain)
                myHP += myUnit.attack;
            Situation newSituation = new Situation(command, situation.myHand, myNewBoard, situation.enemyBoard, myHP, situation.enemyHealth - myUnit.attack);
            countValueOf(newSituation);
            result.add(newSituation);
        }
        if (situation.enemyBoard.size() > 0) {
            for (int enemyUnitIndex = 0; enemyUnitIndex < situation.enemyBoard.size(); ++enemyUnitIndex) {
                PCard enemyUnit = situation.enemyBoard.get(enemyUnitIndex);
                if (enemyUnit.lane == myUnit.lane && (!enemyHasGuard || enemyUnit.guard)) {
                    PCard enemyUnitAfterBattle = getAfterBattle(enemyUnit, myUnit);
                    PCard myUnitAfterBattle = getAfterBattle(myUnit, enemyUnit);
                    List<PCard> myNewBoard = copyListWithout(chosenIndex, situation.myBoard);
                    List<PCard> enemyNewBoard = copyListWithout(enemyUnitIndex, situation.enemyBoard);
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
                    String command;
                    if (myUnit.instanceId >= 0)
                        command = situation.command + "; ATTACK " + myUnit.instanceId + " " + enemyUnit.instanceId;
                    else {
                        command = situation.command + "; ATTACK " + (MAX_UNIT_ID + 1) + " " + enemyUnit.instanceId;
                        command += "; ATTACK " + (MAX_UNIT_ID + 2) + " " + enemyUnit.instanceId;
                        command += "; ATTACK " + (MAX_UNIT_ID + 3) + " " + enemyUnit.instanceId;
                        command += "; ATTACK " + (MAX_UNIT_ID + 4) + " " + enemyUnit.instanceId;
                        command += "; ATTACK " + (MAX_UNIT_ID + 5) + " " + enemyUnit.instanceId;
                    }
                    Situation newSituation = new Situation(command, situation.myHand, myNewBoard, enemyNewBoard, myHP, enemyHP);
                    countValueOf(newSituation);
                    result.add(newSituation);
                }
            }
        }
        // without attack:
        {
            List<PCard> myNewBoard = copyListWithout(chosenIndex, situation.myBoard);
            myNewBoard.add(myUnit);
            Situation newSituation = new Situation(situation.command, situation.myHand, myNewBoard, situation.enemyBoard, situation.myHealth, situation.enemyHealth);
            countValueOf(newSituation);
            result.add(newSituation);
        }
        return result;
    }

    public static Collection<Situation> generateSituationsForOneCard(int index1, List<PCard> myHand, List<PCard> myBoard, List<PCard> enemyBoard) {
        Collection<Situation> result = new ArrayList<>();
        PCard card1 = myHand.get(index1);
//        if (LOGGING)
//            System.err.println("===== ONE CARD: " + card1.instanceId + " TYPE: " + card1.cardType);
        int units = (card1.cardType == 0 ? 1 : 0);
        if (units + myBoard.size() > 6)
            return result;
        List<PCard> myNewHand = copyListWithout(index1, myHand);
        List<PCard> myNewBoard;
        String command = "";
        int countLane0 = 0;
        int countLane1 = 0;
        for (PCard unit : myBoard)
            if (unit.lane == 0)
                ++countLane0;
            else
                ++countLane1;
        if (card1.cardType == 0) {
            // lane0
            if (countLane0 < 2 || (countLane0 < 3 && card1.area != 1 && (card1.area == 0 || countLane1 < 3))) {
                int enemyHP = ENEMY_HEALTH;
                int myHP = MY_HEALTH;
                PCard myUnit = copy(card1);
                myUnit.lane = 0;
                myNewBoard = new ArrayList<>(myBoard);
                myNewBoard.add(myUnit);
                if (!myUnit.charge)
                    myUnit.used = true;
                if (card1.area > 0) {
                    PCard myUnit2 = copyWithoutId(card1);
                    myUnit2.lane = card1.area == 1 ? 0 : 1;
                    myNewBoard.add(myUnit2);
                    if (!myUnit2.charge)
                        myUnit2.used = true;
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }
                command = "SUMMON " + myUnit.instanceId + " 0";
                myHP += myUnit.myHealthChange;
                enemyHP += myUnit.opponentHealthChange;
                Situation situation = new Situation(command, myNewHand, myNewBoard, enemyBoard, myHP, enemyHP);
                countValueOf(situation);
                result.add(situation);
            }
            // lane1
            if (countLane1 < 2 || (countLane1 < 3 && card1.area != 1 && (card1.area == 0 || countLane0 < 3))) {
                int enemyHP = ENEMY_HEALTH;
                int myHP = MY_HEALTH;
                PCard myUnit = copy(card1);
                myUnit.lane = 1;
                myNewBoard = new ArrayList<>(myBoard);
                myNewBoard.add(myUnit);
                if (!myUnit.charge)
                    myUnit.used = true;
                if (card1.area > 0) {
                    PCard myUnit2 = copyWithoutId(card1);
                    myUnit2.lane = card1.area == 1 ? 1 : 0;
                    myNewBoard.add(myUnit2);
                    if (!myUnit2.charge)
                        myUnit2.used = true;
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }
                command = "SUMMON " + myUnit.instanceId + " 1";
                myHP += myUnit.myHealthChange;
                enemyHP += myUnit.opponentHealthChange;
                Situation situation = new Situation(command, myNewHand, myNewBoard, enemyBoard, myHP, enemyHP);
                countValueOf(situation);
                result.add(situation);
            }
            return result;
        }
        myNewBoard = new ArrayList<>(myBoard);
        processRedItem(myNewBoard, enemyBoard, result, card1, myNewHand, command, MY_HEALTH, ENEMY_HEALTH);
        processGreenItem(enemyBoard, result, card1, myNewHand, myNewBoard, command, MY_HEALTH, ENEMY_HEALTH);
        return result;
    }

    public static Collection<Situation> generateSituationsForTwoCards(int index1, int index2, List<PCard> myHand, List<PCard> myBoard, List<PCard> enemyBoard) {
        Collection<Situation> result = new ArrayList<>();
        PCard card1 = myHand.get(index1);
        PCard card2 = myHand.get(index2);
        if (LOGGING)
            System.err.println("===== TWO CARDS: " + card1.instanceId + ", " + card2.instanceId);
        int units = (card1.cardType == 0 ? 1 : 0) + (card2.cardType == 0 ? 1 : 0);
        if (units + myBoard.size() > 6)
            return result;
        int myHP = MY_HEALTH;
        int enemyHP = ENEMY_HEALTH;
        List<PCard> myNewHand = copyListWithout(index1, index2, myHand);
        List<PCard> myNewBoard = new ArrayList<>(myBoard);
        String command = "";
        int countLane0 = 0;
        int countLane1 = 0;
        for (PCard unit : myBoard)
            if (unit.lane == 0)
                ++countLane0;
            else
                ++countLane1;

        if (units > 0) {
            // 4 przypadki rzucania
            // pierwszy: 2x Lane0
            int add0 = 0;
            int add1 = 0;
            if (card1.cardType == 0) {
                if (card1.area == 0)
                    ++add0;
                else if (card1.area == 1)
                    add0 += 2;
                else if (card1.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if (card2.cardType == 0) {
                if (card2.area == 0)
                    ++add0;
                else if (card2.area == 1)
                    add0 += 2;
                else if (card2.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if ((add0 + countLane0) <= 3 && (add1 + countLane1) <= 3) {
                if (card1.cardType == 0) {
                    PCard myUnit = copy(card1);
                    myUnit.lane = 0;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (card1.area > 0) {
                        PCard myUnit2 = copyWithoutId(card1);
                        myUnit2.lane = card1.area == 1 ? 0 : 1;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command = "SUMMON " + myUnit.instanceId + " 0";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }
                if (card2.cardType == 0) {
                    PCard myUnit = copy(card2);
                    myUnit.lane = 0;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (card2.area > 0) {
                        PCard myUnit2 = copyWithoutId(card2);
                        myUnit2.lane = card2.area == 1 ? 0 : 1;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command += ";SUMMON " + myUnit.instanceId + " 0";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }

                Situation situation = new Situation(command, myNewHand, myNewBoard, enemyBoard, myHP, enemyHP);
                countValueOf(situation);
                result.add(situation);
                if (units < 2) {
                    processRedItem(myNewBoard, enemyBoard, result, card1, myNewHand, command, myHP, enemyHP);
                    processRedItem(myNewBoard, enemyBoard, result, card2, myNewHand, command, myHP, enemyHP);

                    processGreenItem(enemyBoard, result, card1, myNewHand, myNewBoard, command, myHP, enemyHP);
                    processGreenItem(enemyBoard, result, card2, myNewHand, myNewBoard, command, myHP, enemyHP);
                }
            }

            // drugi: 2x Lane1
            myHP = MY_HEALTH;
            enemyHP = ENEMY_HEALTH;
            command = "";
            myNewBoard = new ArrayList<>(myBoard);
            add0 = 0;
            add1 = 0;
            if (card1.cardType == 0) {
                if (card1.area == 0)
                    ++add1;
                else if (card1.area == 1)
                    add1 += 2;
                else if (card1.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if (card2.cardType == 0) {
                if (card2.area == 0)
                    ++add1;
                else if (card2.area == 1)
                    add1 += 2;
                else if (card2.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if ((add0 + countLane0) <= 3 && (add1 + countLane1) <= 3) {
                if (card1.cardType == 0) {
                    PCard myUnit = copy(card1);
                    myUnit.lane = 1;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (card1.area > 0) {
                        PCard myUnit2 = copyWithoutId(card1);
                        myUnit2.lane = card1.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command = "SUMMON " + myUnit.instanceId + " 1";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }
                if (card2.cardType == 0) {
                    PCard myUnit = copy(card2);
                    myUnit.lane = 1;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (card2.area > 0) {
                        PCard myUnit2 = copyWithoutId(card2);
                        myUnit2.lane = card2.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command += ";SUMMON " + myUnit.instanceId + " 1";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }
                Situation situation = new Situation(command, myNewHand, myNewBoard, enemyBoard, myHP, enemyHP);
                countValueOf(situation);
                result.add(situation);
                if (units < 2) {
                    processRedItem(myNewBoard, enemyBoard, result, card1, myNewHand, command, myHP, enemyHP);
                    processRedItem(myNewBoard, enemyBoard, result, card2, myNewHand, command, myHP, enemyHP);

                    processGreenItem(enemyBoard, result, card1, myNewHand, myNewBoard, command, myHP, enemyHP);
                    processGreenItem(enemyBoard, result, card2, myNewHand, myNewBoard, command, myHP, enemyHP);
                }
            }
            // trzeci: lane0 + lane1
            myHP = MY_HEALTH;
            enemyHP = ENEMY_HEALTH;
            command = "";
            myNewBoard = new ArrayList<>(myBoard);
            add0 = 0;
            add1 = 0;
            if (card1.cardType == 0) {
                if (card1.area == 0)
                    ++add0;
                else if (card1.area == 1)
                    add0 += 2;
                else if (card1.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if (card2.cardType == 0) {
                if (card2.area == 0)
                    ++add1;
                else if (card2.area == 1)
                    add1 += 2;
                else if (card2.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if ((add0 + countLane0) <= 3 && (add1 + countLane1) <= 3) {
                if (card1.cardType == 0) {
                    PCard myUnit = copy(card1);
                    myUnit.lane = 0;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (card1.area > 0) {
                        PCard myUnit2 = copyWithoutId(card1);
                        myUnit2.lane = card1.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command = "SUMMON " + myUnit.instanceId + " 0";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }
                if (card2.cardType == 0) {
                    PCard myUnit = copy(card2);
                    myUnit.lane = 1;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (card2.area > 0) {
                        PCard myUnit2 = copyWithoutId(card2);
                        myUnit2.lane = card2.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command += ";SUMMON " + myUnit.instanceId + " 1";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }
                Situation situation = new Situation(command, myNewHand, myNewBoard, enemyBoard, myHP, enemyHP);
                countValueOf(situation);
                result.add(situation);
                if (units < 2) {
                    processRedItem(myNewBoard, enemyBoard, result, card1, myNewHand, command, myHP, enemyHP);
                    processRedItem(myNewBoard, enemyBoard, result, card2, myNewHand, command, myHP, enemyHP);

                    processGreenItem(enemyBoard, result, card1, myNewHand, myNewBoard, command, myHP, enemyHP);
                    processGreenItem(enemyBoard, result, card2, myNewHand, myNewBoard, command, myHP, enemyHP);
                }
            }
            // czwarty: Lane1 + lane0
            myHP = MY_HEALTH;
            enemyHP = ENEMY_HEALTH;
            command = "";
            myNewBoard = new ArrayList<>(myBoard);
            add0 = 0;
            add1 = 0;
            if (card1.cardType == 0) {
                if (card1.area == 0)
                    ++add1;
                else if (card1.area == 1)
                    add1 += 2;
                else if (card1.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if (card2.cardType == 0) {
                if (card2.area == 0)
                    ++add0;
                else if (card2.area == 1)
                    add0 += 2;
                else if (card2.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if ((add0 + countLane0) <= 3 && (add1 + countLane1) <= 3) {
                if (card1.cardType == 0) {
                    PCard myUnit = copy(card1);
                    myUnit.lane = 1;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (card1.area > 0) {
                        PCard myUnit2 = copyWithoutId(card1);
                        myUnit2.lane = card1.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command = "SUMMON " + myUnit.instanceId + " 1";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }
                if (card2.cardType == 0) {
                    PCard myUnit = copy(card2);
                    myUnit.lane = 0;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (card2.area > 0) {
                        PCard myUnit2 = copyWithoutId(card2);
                        myUnit2.lane = card2.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command += ";SUMMON " + myUnit.instanceId + " 0";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }
                Situation situation = new Situation(command, myNewHand, myNewBoard, enemyBoard, myHP, enemyHP);
                countValueOf(situation);
                result.add(situation);
                if (units < 2) {
                    processRedItem(myNewBoard, enemyBoard, result, card1, myNewHand, command, myHP, enemyHP);
                    processRedItem(myNewBoard, enemyBoard, result, card2, myNewHand, command, myHP, enemyHP);

                    processGreenItem(enemyBoard, result, card1, myNewHand, myNewBoard, command, myHP, enemyHP);
                    processGreenItem(enemyBoard, result, card2, myNewHand, myNewBoard, command, myHP, enemyHP);
                }
            }
        }
        if (units == 0) {
            List<Situation> newResult = new ArrayList<>();
            if (card1.cardType == 1)
                processGreenItem(enemyBoard, newResult, card1, myNewHand, myNewBoard, command, MY_HEALTH, ENEMY_HEALTH);
            else
                processRedItem(myNewBoard, enemyBoard, newResult, card1, myNewHand, command, MY_HEALTH, ENEMY_HEALTH);

            for (Situation situation : newResult)
                if (card2.cardType == 1)
                    processGreenItem(situation.enemyBoard, result, card2, situation.myHand, situation.myBoard, situation.command, situation.myHealth, situation.enemyHealth);
                else
                    processRedItem(situation.myBoard, situation.enemyBoard, result, card2, situation.myHand, situation.command, situation.myHealth, situation.enemyHealth);
        }
        return result;
    }

    public static Collection<Situation> generateSituationsForThreeCards(int i1, int i2, int i3, List<PCard> myHand, List<PCard> myBoard, List<PCard> enemyBoard) {
        Collection<Situation> result = new ArrayList<>();
        PCard c1 = myHand.get(i1);
        PCard c2 = myHand.get(i2);
        PCard c3 = myHand.get(i3);
        if (LOGGING)
            System.err.println("===== THREE CARDS: " + c1.instanceId + ", " + c2.instanceId + ", " + c3.instanceId);
        int units = (c1.cardType == 0 ? 1 : 0) + (c2.cardType == 0 ? 1 : 0) + (c3.cardType == 0 ? 1 : 0);
        if (units < 2 || units + myBoard.size() > 6)
            return result;
        int myHP = MY_HEALTH;
        int enemyHP = ENEMY_HEALTH;
        List<PCard> myNewHand = copyListWithout(i1, i2, i3, myHand);
        List<PCard> myNewBoard = new ArrayList<>(myBoard);
        String command = "";
        int countLane0 = 0;
        int countLane1 = 0;
        for (PCard unit : myBoard)
            if (unit.lane == 0)
                ++countLane0;
            else
                ++countLane1;

        if (units > 0) {
            // 8 przypadkow rzucania
            // pierwszy: 3x Lane0
            int add0 = 0;
            int add1 = 0;
            if (c1.cardType == 0) {
                if (c1.area == 0)
                    ++add0;
                else if (c1.area == 1)
                    add0 += 2;
                else if (c1.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if (c2.cardType == 0) {
                if (c2.area == 0)
                    ++add0;
                else if (c2.area == 1)
                    add0 += 2;
                else if (c2.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if (c3.cardType == 0) {
                if (c3.area == 0)
                    ++add0;
                else if (c3.area == 1)
                    add0 += 2;
                else if (c3.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if (((add0 + countLane0) <= 3) && ((add1 + countLane1) <= 3)) {
                if (c1.cardType == 0) {
                    PCard myUnit = copy(c1);
                    myUnit.lane = 0;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (c1.area > 0) {
                        PCard myUnit2 = copyWithoutId(c1);
                        myUnit2.lane = c1.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command = "SUMMON " + myUnit.instanceId + " 0";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }
                if (c2.cardType == 0) {
                    PCard myUnit = copy(c2);
                    myUnit.lane = 0;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (c2.area > 0) {
                        PCard myUnit2 = copyWithoutId(c2);
                        myUnit2.lane = c2.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command += ";SUMMON " + myUnit.instanceId + " 0";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }
                if (c3.cardType == 0) {
                    PCard myUnit = copy(c3);
                    myUnit.lane = 0;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (c3.area > 0) {
                        PCard myUnit2 = copyWithoutId(c3);
                        myUnit2.lane = c3.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command += ";SUMMON " + myUnit.instanceId + " 0";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }

                Situation situation = new Situation(command, myNewHand, myNewBoard, enemyBoard, myHP, enemyHP);
                countValueOf(situation);
                result.add(situation);
                if (units < 3) {
                    processRedItem(myNewBoard, enemyBoard, result, c1, myNewHand, command, myHP, enemyHP);
                    processRedItem(myNewBoard, enemyBoard, result, c2, myNewHand, command, myHP, enemyHP);
                    processRedItem(myNewBoard, enemyBoard, result, c3, myNewHand, command, myHP, enemyHP);

                    processGreenItem(enemyBoard, result, c1, myNewHand, myNewBoard, command, myHP, enemyHP);
                    processGreenItem(enemyBoard, result, c2, myNewHand, myNewBoard, command, myHP, enemyHP);
                    processGreenItem(enemyBoard, result, c3, myNewHand, myNewBoard, command, myHP, enemyHP);
                }
            }

            // drugi: Lane0, Lane0, Lane1
            myHP = MY_HEALTH;
            enemyHP = ENEMY_HEALTH;
            command = "";
            myNewBoard = new ArrayList<>(myBoard);
            add0 = 0;
            add1 = 0;
            if (c1.cardType == 0) {
                if (c1.area == 0)
                    ++add0;
                else if (c1.area == 1)
                    add0 += 2;
                else if (c1.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if (c2.cardType == 0) {
                if (c2.area == 0)
                    ++add0;
                else if (c2.area == 1)
                    add0 += 2;
                else if (c2.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if (c3.cardType == 0) {
                if (c3.area == 0)
                    ++add1;
                else if (c3.area == 1)
                    add1 += 2;
                else if (c3.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if ((add0 + countLane0) <= 3 && (add1 + countLane1) <= 3) {
                if (c1.cardType == 0) {
                    PCard myUnit = copy(c1);
                    myUnit.lane = 0;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (c1.area > 0) {
                        PCard myUnit2 = copyWithoutId(c1);
                        myUnit2.lane = c1.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command = "SUMMON " + myUnit.instanceId + " 0";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }
                if (c2.cardType == 0) {
                    PCard myUnit = copy(c2);
                    myUnit.lane = 0;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (c2.area > 0) {
                        PCard myUnit2 = copyWithoutId(c2);
                        myUnit2.lane = c2.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command += ";SUMMON " + myUnit.instanceId + " 0";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }
                if (c3.cardType == 0) {
                    PCard myUnit = copy(c3);
                    myUnit.lane = 1;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (c3.area > 0) {
                        PCard myUnit2 = copyWithoutId(c3);
                        myUnit2.lane = c3.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command += ";SUMMON " + myUnit.instanceId + " 1";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }

                Situation situation = new Situation(command, myNewHand, myNewBoard, enemyBoard, myHP, enemyHP);
                countValueOf(situation);
                result.add(situation);
                if (units < 3) {
                    processRedItem(myNewBoard, enemyBoard, result, c1, myNewHand, command, myHP, enemyHP);
                    processRedItem(myNewBoard, enemyBoard, result, c2, myNewHand, command, myHP, enemyHP);
                    processRedItem(myNewBoard, enemyBoard, result, c3, myNewHand, command, myHP, enemyHP);

                    processGreenItem(enemyBoard, result, c1, myNewHand, myNewBoard, command, myHP, enemyHP);
                    processGreenItem(enemyBoard, result, c2, myNewHand, myNewBoard, command, myHP, enemyHP);
                    processGreenItem(enemyBoard, result, c3, myNewHand, myNewBoard, command, myHP, enemyHP);
                }
            }

            // trzeci: Lane0, Lane1, Lane1
            myHP = MY_HEALTH;
            enemyHP = ENEMY_HEALTH;
            command = "";
            myNewBoard = new ArrayList<>(myBoard);
            add0 = 0;
            add1 = 0;
            if (c1.cardType == 0) {
                if (c1.area == 0)
                    ++add0;
                else if (c1.area == 1)
                    add0 += 2;
                else if (c1.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if (c2.cardType == 0) {
                if (c2.area == 0)
                    ++add1;
                else if (c2.area == 1)
                    add1 += 2;
                else if (c2.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if (c3.cardType == 0) {
                if (c3.area == 0)
                    ++add1;
                else if (c3.area == 1)
                    add1 += 2;
                else if (c3.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if ((add0 + countLane0) <= 3 && (add1 + countLane1) <= 3) {
                if (c1.cardType == 0) {
                    PCard myUnit = copy(c1);
                    myUnit.lane = 0;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (c1.area > 0) {
                        PCard myUnit2 = copyWithoutId(c1);
                        myUnit2.lane = c1.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command = "SUMMON " + myUnit.instanceId + " 0";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }
                if (c2.cardType == 0) {
                    PCard myUnit = copy(c2);
                    myUnit.lane = 1;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (c2.area > 0) {
                        PCard myUnit2 = copyWithoutId(c2);
                        myUnit2.lane = c2.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command += ";SUMMON " + myUnit.instanceId + " 1";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }
                if (c3.cardType == 0) {
                    PCard myUnit = copy(c3);
                    myUnit.lane = 1;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (c3.area > 0) {
                        PCard myUnit2 = copyWithoutId(c3);
                        myUnit2.lane = c3.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command += ";SUMMON " + myUnit.instanceId + " 1";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }

                Situation situation = new Situation(command, myNewHand, myNewBoard, enemyBoard, myHP, enemyHP);
                countValueOf(situation);
                result.add(situation);
                if (units < 3) {
                    processRedItem(myNewBoard, enemyBoard, result, c1, myNewHand, command, myHP, enemyHP);
                    processRedItem(myNewBoard, enemyBoard, result, c2, myNewHand, command, myHP, enemyHP);
                    processRedItem(myNewBoard, enemyBoard, result, c3, myNewHand, command, myHP, enemyHP);

                    processGreenItem(enemyBoard, result, c1, myNewHand, myNewBoard, command, myHP, enemyHP);
                    processGreenItem(enemyBoard, result, c2, myNewHand, myNewBoard, command, myHP, enemyHP);
                    processGreenItem(enemyBoard, result, c3, myNewHand, myNewBoard, command, myHP, enemyHP);
                }
            }

            // czwarty: Lane0, Lane1, Lane0
            myHP = MY_HEALTH;
            enemyHP = ENEMY_HEALTH;
            command = "";
            myNewBoard = new ArrayList<>(myBoard);
            add0 = 0;
            add1 = 0;
            if (c1.cardType == 0) {
                if (c1.area == 0)
                    ++add0;
                else if (c1.area == 1)
                    add0 += 2;
                else if (c1.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if (c2.cardType == 0) {
                if (c2.area == 0)
                    ++add1;
                else if (c2.area == 1)
                    add1 += 2;
                else if (c2.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if (c3.cardType == 0) {
                if (c3.area == 0)
                    ++add0;
                else if (c3.area == 1)
                    add0 += 2;
                else if (c3.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if ((add0 + countLane0) <= 3 && (add1 + countLane1) <= 3) {
                if (c1.cardType == 0) {
                    PCard myUnit = copy(c1);
                    myUnit.lane = 0;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (c1.area > 0) {
                        PCard myUnit2 = copyWithoutId(c1);
                        myUnit2.lane = c1.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command = "SUMMON " + myUnit.instanceId + " 0";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }
                if (c2.cardType == 0) {
                    PCard myUnit = copy(c2);
                    myUnit.lane = 1;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (c2.area > 0) {
                        PCard myUnit2 = copyWithoutId(c2);
                        myUnit2.lane = c2.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command += ";SUMMON " + myUnit.instanceId + " 1";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }
                if (c3.cardType == 0) {
                    PCard myUnit = copy(c3);
                    myUnit.lane = 0;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (c3.area > 0) {
                        PCard myUnit2 = copyWithoutId(c3);
                        myUnit2.lane = c3.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command += ";SUMMON " + myUnit.instanceId + " 0";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }

                Situation situation = new Situation(command, myNewHand, myNewBoard, enemyBoard, myHP, enemyHP);
                countValueOf(situation);
                result.add(situation);
                if (units < 3) {
                    processRedItem(myNewBoard, enemyBoard, result, c1, myNewHand, command, myHP, enemyHP);
                    processRedItem(myNewBoard, enemyBoard, result, c2, myNewHand, command, myHP, enemyHP);
                    processRedItem(myNewBoard, enemyBoard, result, c3, myNewHand, command, myHP, enemyHP);

                    processGreenItem(enemyBoard, result, c1, myNewHand, myNewBoard, command, myHP, enemyHP);
                    processGreenItem(enemyBoard, result, c2, myNewHand, myNewBoard, command, myHP, enemyHP);
                    processGreenItem(enemyBoard, result, c3, myNewHand, myNewBoard, command, myHP, enemyHP);
                }
            }

            // piaty: Lane1, Lane1, Lane1
            myHP = MY_HEALTH;
            enemyHP = ENEMY_HEALTH;
            command = "";
            myNewBoard = new ArrayList<>(myBoard);
            add0 = 0;
            add1 = 0;
            if (c1.cardType == 0) {
                if (c1.area == 0)
                    ++add1;
                else if (c1.area == 1)
                    add1 += 2;
                else if (c1.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if (c2.cardType == 0) {
                if (c2.area == 0)
                    ++add1;
                else if (c2.area == 1)
                    add1 += 2;
                else if (c2.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if (c3.cardType == 0) {
                if (c3.area == 0)
                    ++add1;
                else if (c3.area == 1)
                    add1 += 2;
                else if (c3.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if ((add0 + countLane0) <= 3 && (add1 + countLane1) <= 3) {
                if (c1.cardType == 0) {
                    PCard myUnit = copy(c1);
                    myUnit.lane = 1;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (c2.area > 0) {
                        PCard myUnit2 = copyWithoutId(c1);
                        myUnit2.lane = c1.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command = "SUMMON " + myUnit.instanceId + " 1";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }
                if (c2.cardType == 0) {
                    PCard myUnit = copy(c2);
                    myUnit.lane = 1;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (c3.area > 0) {
                        PCard myUnit2 = copyWithoutId(c2);
                        myUnit2.lane = c2.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command += ";SUMMON " + myUnit.instanceId + " 1";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }
                if (c3.cardType == 0) {
                    PCard myUnit = copy(c3);
                    myUnit.lane = 1;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (c1.area > 0) {
                        PCard myUnit2 = copyWithoutId(c3);
                        myUnit2.lane = c3.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command += ";SUMMON " + myUnit.instanceId + " 1";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }

                Situation situation = new Situation(command, myNewHand, myNewBoard, enemyBoard, myHP, enemyHP);
                countValueOf(situation);
                result.add(situation);
                if (units < 3) {
                    processRedItem(myNewBoard, enemyBoard, result, c1, myNewHand, command, myHP, enemyHP);
                    processRedItem(myNewBoard, enemyBoard, result, c2, myNewHand, command, myHP, enemyHP);
                    processRedItem(myNewBoard, enemyBoard, result, c3, myNewHand, command, myHP, enemyHP);

                    processGreenItem(enemyBoard, result, c1, myNewHand, myNewBoard, command, myHP, enemyHP);
                    processGreenItem(enemyBoard, result, c2, myNewHand, myNewBoard, command, myHP, enemyHP);
                    processGreenItem(enemyBoard, result, c3, myNewHand, myNewBoard, command, myHP, enemyHP);
                }
            }

            // szosty: Lane1, Lane0, Lane1
            myHP = MY_HEALTH;
            enemyHP = ENEMY_HEALTH;
            command = "";
            myNewBoard = new ArrayList<>(myBoard);
            add0 = 0;
            add1 = 0;
            if (c1.cardType == 0) {
                if (c1.area == 0)
                    ++add1;
                else if (c1.area == 1)
                    add1 += 2;
                else if (c1.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if (c2.cardType == 0) {
                if (c2.area == 0)
                    ++add0;
                else if (c2.area == 1)
                    add0 += 2;
                else if (c2.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if (c3.cardType == 0) {
                if (c3.area == 0)
                    ++add1;
                else if (c3.area == 1)
                    add1 += 2;
                else if (c3.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if ((add0 + countLane0) <= 3 && (add1 + countLane1) <= 3) {
                if (c1.cardType == 0) {
                    PCard myUnit = copy(c1);
                    myUnit.lane = 1;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (c1.area > 0) {
                        PCard myUnit2 = copyWithoutId(c1);
                        myUnit2.lane = c1.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command = "SUMMON " + myUnit.instanceId + " 1";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }
                if (c2.cardType == 0) {
                    PCard myUnit = copy(c2);
                    myUnit.lane = 0;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (c2.area > 0) {
                        PCard myUnit2 = copyWithoutId(c2);
                        myUnit2.lane = c2.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command += ";SUMMON " + myUnit.instanceId + " 0";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }
                if (c3.cardType == 0) {
                    PCard myUnit = copy(c3);
                    myUnit.lane = 1;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (c3.area > 0) {
                        PCard myUnit2 = copyWithoutId(c3);
                        myUnit2.lane = c3.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command += ";SUMMON " + myUnit.instanceId + " 1";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }

                Situation situation = new Situation(command, myNewHand, myNewBoard, enemyBoard, myHP, enemyHP);
                countValueOf(situation);
                result.add(situation);
                if (units < 3) {
                    processRedItem(myNewBoard, enemyBoard, result, c1, myNewHand, command, myHP, enemyHP);
                    processRedItem(myNewBoard, enemyBoard, result, c2, myNewHand, command, myHP, enemyHP);
                    processRedItem(myNewBoard, enemyBoard, result, c3, myNewHand, command, myHP, enemyHP);

                    processGreenItem(enemyBoard, result, c1, myNewHand, myNewBoard, command, myHP, enemyHP);
                    processGreenItem(enemyBoard, result, c2, myNewHand, myNewBoard, command, myHP, enemyHP);
                    processGreenItem(enemyBoard, result, c3, myNewHand, myNewBoard, command, myHP, enemyHP);
                }
            }

            // siodmy: Lane1, Lane1, Lane0
            myHP = MY_HEALTH;
            enemyHP = ENEMY_HEALTH;
            command = "";
            myNewBoard = new ArrayList<>(myBoard);
            add0 = 0;
            add1 = 0;
            if (c1.cardType == 0) {
                if (c1.area == 0)
                    ++add1;
                else if (c1.area == 1)
                    add1 += 2;
                else if (c1.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if (c2.cardType == 0) {
                if (c2.area == 0)
                    ++add1;
                else if (c2.area == 1)
                    add1 += 2;
                else if (c2.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if (c3.cardType == 0) {
                if (c3.area == 0)
                    ++add0;
                else if (c3.area == 1)
                    add0 += 2;
                else if (c3.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if ((add0 + countLane0) <= 3 && (add1 + countLane1) <= 3) {
                if (c1.cardType == 0) {
                    PCard myUnit = copy(c1);
                    myUnit.lane = 1;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (c1.area > 0) {
                        PCard myUnit2 = copyWithoutId(c1);
                        myUnit2.lane = c1.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command = "SUMMON " + myUnit.instanceId + " 1";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }
                if (c2.cardType == 0) {
                    PCard myUnit = copy(c2);
                    myUnit.lane = 1;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (c2.area > 0) {
                        PCard myUnit2 = copyWithoutId(c2);
                        myUnit2.lane = c2.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command += ";SUMMON " + myUnit.instanceId + " 1";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }
                if (c3.cardType == 0) {
                    PCard myUnit = copy(c3);
                    myUnit.lane = 0;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (c3.area > 0) {
                        PCard myUnit2 = copyWithoutId(c3);
                        myUnit2.lane = c3.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command += ";SUMMON " + myUnit.instanceId + " 0";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }

                Situation situation = new Situation(command, myNewHand, myNewBoard, enemyBoard, myHP, enemyHP);
                countValueOf(situation);
                result.add(situation);
                if (units < 3) {
                    processRedItem(myNewBoard, enemyBoard, result, c1, myNewHand, command, myHP, enemyHP);
                    processRedItem(myNewBoard, enemyBoard, result, c2, myNewHand, command, myHP, enemyHP);
                    processRedItem(myNewBoard, enemyBoard, result, c3, myNewHand, command, myHP, enemyHP);

                    processGreenItem(enemyBoard, result, c1, myNewHand, myNewBoard, command, myHP, enemyHP);
                    processGreenItem(enemyBoard, result, c2, myNewHand, myNewBoard, command, myHP, enemyHP);
                    processGreenItem(enemyBoard, result, c3, myNewHand, myNewBoard, command, myHP, enemyHP);
                }
            }

            // osmy: Lane1, Lane0, Lane0
            myHP = MY_HEALTH;
            enemyHP = ENEMY_HEALTH;
            command = "";
            myNewBoard = new ArrayList<>(myBoard);
            add0 = 0;
            add1 = 0;
            if (c1.cardType == 0) {
                if (c1.area == 0)
                    ++add1;
                else if (c1.area == 1)
                    add1 += 2;
                else if (c1.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if (c2.cardType == 0) {
                if (c2.area == 0)
                    ++add0;
                else if (c2.area == 1)
                    add0 += 2;
                else if (c2.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if (c3.cardType == 0) {
                if (c3.area == 0)
                    ++add0;
                else if (c3.area == 1)
                    add0 += 2;
                else if (c3.area == 2) {
                    ++add0;
                    ++add1;
                }
            }
            if ((add0 + countLane0) <= 3 && (add1 + countLane1) <= 3) {
                if (c1.cardType == 0) {
                    PCard myUnit = copy(c1);
                    myUnit.lane = 1;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (c1.area > 0) {
                        PCard myUnit2 = copyWithoutId(c1);
                        myUnit2.lane = c1.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command = "SUMMON " + myUnit.instanceId + " 1";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }
                if (c2.cardType == 0) {
                    PCard myUnit = copy(c2);
                    myUnit.lane = 0;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (c2.area > 0) {
                        PCard myUnit2 = copyWithoutId(c2);
                        myUnit2.lane = c2.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command += ";SUMMON " + myUnit.instanceId + " 0";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }
                if (c3.cardType == 0) {
                    PCard myUnit = copy(c3);
                    myUnit.lane = 0;
                    myNewBoard.add(myUnit);
                    if (!myUnit.charge)
                        myUnit.used = true;
                    if (c3.area > 0) {
                        PCard myUnit2 = copyWithoutId(c3);
                        myUnit2.lane = c3.area == 1 ? myUnit.lane : 1 - myUnit.lane;
                        myNewBoard.add(myUnit2);
                        if (!myUnit2.charge)
                            myUnit2.used = true;
                        myHP += myUnit.myHealthChange;
                        enemyHP += myUnit.opponentHealthChange;
                    }
                    command += ";SUMMON " + myUnit.instanceId + " 0";
                    myHP += myUnit.myHealthChange;
                    enemyHP += myUnit.opponentHealthChange;
                }

                Situation situation = new Situation(command, myNewHand, myNewBoard, enemyBoard, myHP, enemyHP);
                countValueOf(situation);
                result.add(situation);
                if (units < 3) {
                    processRedItem(myNewBoard, enemyBoard, result, c1, myNewHand, command, myHP, enemyHP);
                    processRedItem(myNewBoard, enemyBoard, result, c2, myNewHand, command, myHP, enemyHP);
                    processRedItem(myNewBoard, enemyBoard, result, c3, myNewHand, command, myHP, enemyHP);

                    processGreenItem(enemyBoard, result, c1, myNewHand, myNewBoard, command, myHP, enemyHP);
                    processGreenItem(enemyBoard, result, c2, myNewHand, myNewBoard, command, myHP, enemyHP);
                    processGreenItem(enemyBoard, result, c3, myNewHand, myNewBoard, command, myHP, enemyHP);
                }
            }

        }

        return result;
    }

    public static void processRedItem(List<PCard> myBoard, List<PCard> enemyBoard, Collection<Situation> result, PCard card1, List<PCard> myNewHand, String command, int myHP, int enemyHP) {
        if (card1.cardType >= 2 && enemyBoard.size() > 0) {
            if (card1.area == 2) {
                int unitsAffected = 0;
                List<PCard> enemyNewBoard = new ArrayList<>();
                int firstEnemyInstanceId = -1;
                for (PCard enemyUnit : enemyBoard) {
                    PCard enemyUnitAfterCard = getAfterRedItem(enemyUnit, card1);
                    if (firstEnemyInstanceId < 0)
                        firstEnemyInstanceId = enemyUnit.instanceId;
                    if (enemyUnitAfterCard != null)
                        enemyNewBoard.add(enemyUnitAfterCard);
                    ++unitsAffected;
                }
                Situation situation = new Situation(command + ";USE " + card1.instanceId + " " + firstEnemyInstanceId, myNewHand, myBoard, enemyNewBoard, myHP + card1.myHealthChange, enemyHP + unitsAffected * card1.opponentHealthChange);
                countValueOf(situation);
                result.add(situation);
            } else if (card1.area == 1) {
                int countLane0 = 0;
                int countLane1 = 0;
                for (PCard enemyUnit : enemyBoard)
                    if (enemyUnit.lane == 0)
                        ++countLane0;
                    else
                        ++countLane1;
                if (countLane0 > 0) {
                    int unitsAffected = 0;
                    List<PCard> enemyNewBoard = new ArrayList<>();
                    int firstEnemyInstanceId = -1;
                    for (PCard enemyUnit : enemyBoard)
                        if (enemyUnit.lane == 0) {
                            PCard enemyUnitAfterCard = getAfterRedItem(enemyUnit, card1);
                            if (firstEnemyInstanceId < 0)
                                firstEnemyInstanceId = enemyUnit.instanceId;
                            if (enemyUnitAfterCard != null)
                                enemyNewBoard.add(enemyUnitAfterCard);
                            ++unitsAffected;
                        } else
                            enemyNewBoard.add(enemyUnit);
                    Situation situation = new Situation(command + ";USE " + card1.instanceId + " " + firstEnemyInstanceId, myNewHand, myBoard, enemyNewBoard, myHP + card1.myHealthChange, enemyHP + unitsAffected * card1.opponentHealthChange);
                    countValueOf(situation);
                    result.add(situation);
                }
                if (countLane1 > 0) {
                    int unitsAffected = 0;
                    List<PCard> enemyNewBoard = new ArrayList<>();
                    int firstEnemyInstanceId = -1;
                    for (PCard enemyUnit : enemyBoard)
                        if (enemyUnit.lane == 1) {
                            PCard enemyUnitAfterCard = getAfterRedItem(enemyUnit, card1);
                            if (firstEnemyInstanceId < 0)
                                firstEnemyInstanceId = enemyUnit.instanceId;
                            if (enemyUnitAfterCard != null)
                                enemyNewBoard.add(enemyUnitAfterCard);
                            ++unitsAffected;
                        } else
                            enemyNewBoard.add(enemyUnit);
                    Situation situation = new Situation(command + ";USE " + card1.instanceId + " " + firstEnemyInstanceId, myNewHand, myBoard, enemyNewBoard, myHP + card1.myHealthChange, enemyHP + unitsAffected * card1.opponentHealthChange);
                    countValueOf(situation);
                    result.add(situation);
                }
            } else {
                for (int enemyUnitIndex = 0; enemyUnitIndex < enemyBoard.size(); ++enemyUnitIndex) {
                    PCard enemyUnit = enemyBoard.get(enemyUnitIndex);
                    List<PCard> enemyNewBoard = copyListWithout(enemyUnitIndex, enemyBoard);
                    String newCommand = command + ";USE " + card1.instanceId + " " + enemyUnit.instanceId;
                    PCard enemyUnitAfterCard = getAfterRedItem(enemyUnit, card1);
                    if (enemyUnitAfterCard != null)
                        enemyNewBoard.add(enemyUnitAfterCard);
                    Situation situation = new Situation(newCommand, myNewHand, myBoard, enemyNewBoard, myHP + card1.myHealthChange, enemyHP + card1.opponentHealthChange);
                    countValueOf(situation);
                    result.add(situation);
                }
            }
        }
    }

    public static void processGreenItem(List<PCard> enemyBoard, Collection<Situation> result, PCard card1, List<PCard> myNewHand, List<PCard> myNewBoard, String command, int myHP, int enemyHP) {
        if (card1.cardType == 1 && myNewBoard.size() > 0) {
            if (card1.area == 2) {
                List<PCard> myNewBoard2 = new ArrayList<>();
                int firstMmyInstanceId = -1;
                for (PCard myUnit : myNewBoard) {
                    PCard myUnitAfterCard = getAfterGreenItem(myUnit, card1);
                    if (firstMmyInstanceId < 0)
                        firstMmyInstanceId = myUnit.instanceId;
                    if (myUnitAfterCard != null)
                        myNewBoard2.add(myUnitAfterCard);
                }
                Situation situation = new Situation(command + ";USE " + card1.instanceId + " " + firstMmyInstanceId, myNewHand, myNewBoard2, enemyBoard, myHP + card1.myHealthChange, enemyHP + card1.opponentHealthChange);
                countValueOf(situation);
                result.add(situation);
            } else if (card1.area == 1) {
                int countLane0 = 0;
                int countLane1 = 0;
                for (PCard myUnit : myNewBoard)
                    if (myUnit.lane == 0)
                        ++countLane0;
                    else
                        ++countLane1;
                if (countLane0 > 0) {
                    List<PCard> myNewBoard2 = new ArrayList<>();
                    int firstMmyInstanceId = -1;
                    for (PCard myUnit : myNewBoard)
                        if (myUnit.lane == 0) {
                            PCard myUnitAfterCard = getAfterGreenItem(myUnit, card1);
                            if (firstMmyInstanceId < 0)
                                firstMmyInstanceId = myUnit.instanceId;
                            if (myUnitAfterCard != null)
                                myNewBoard2.add(myUnitAfterCard);
                        } else
                            myNewBoard2.add(myUnit);
                    Situation situation = new Situation(command + ";USE " + card1.instanceId + " " + firstMmyInstanceId, myNewHand, myNewBoard2, enemyBoard, myHP + card1.myHealthChange, enemyHP + card1.opponentHealthChange);
                    countValueOf(situation);
                    result.add(situation);
                }
                if (countLane0 > 1) {
                    List<PCard> myNewBoard2 = new ArrayList<>();
                    int firstMmyInstanceId = -1;
                    for (PCard myUnit : myNewBoard)
                        if (myUnit.lane == 1) {
                            PCard myUnitAfterCard = getAfterGreenItem(myUnit, card1);
                            if (firstMmyInstanceId < 0)
                                firstMmyInstanceId = myUnit.instanceId;
                            if (myUnitAfterCard != null)
                                myNewBoard2.add(myUnitAfterCard);
                        } else
                            myNewBoard2.add(myUnit);
                    Situation situation = new Situation(command + ";USE " + card1.instanceId + " " + firstMmyInstanceId, myNewHand, myNewBoard2, enemyBoard, myHP + card1.myHealthChange, enemyHP + card1.opponentHealthChange);
                    countValueOf(situation);
                    result.add(situation);
                }
            } else {
                for (int myUnitIndex = 0; myUnitIndex < myNewBoard.size(); ++myUnitIndex) {
                    PCard myUnit = myNewBoard.get(myUnitIndex);
                    List<PCard> myNewBoard2 = copyListWithout(myUnitIndex, myNewBoard);
                    String newCommand = command + ";USE " + card1.instanceId + " " + myUnit.instanceId;
                    PCard myUnitAfterCard = getAfterGreenItem(myUnit, card1);
                    if (myUnitAfterCard != null)
                        myNewBoard2.add(myUnitAfterCard);
                    Situation situation = new Situation(newCommand, myNewHand, myNewBoard2, enemyBoard, myHP + card1.myHealthChange, enemyHP + card1.opponentHealthChange);
                    countValueOf(situation);
                    result.add(situation);
                }
            }
        }
    }

    public static PCard getAfterGreenItem(PCard unit, PCard item) {
        PCard result = copy(unit);
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

    public static PCard getAfterRedItem(PCard unit, PCard item) {
        PCard result = copy(unit);
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

    public static PCard getAfterBattle(PCard defender, PCard attacker) {
        if (defender.ward)
            return copyWithoutWard(defender);
        else if (attacker.attack >= defender.defense || attacker.lethal)
            return null;
        else {
            PCard result = copy(defender);
            result.defense -= attacker.attack;
            return result;
        }
    }

    public static PCard existsGuard(List<PCard> board, int lane) {
        for (PCard card : board)
            if (card.lane == lane && card.defense > 0 && card.guard)
                return card;
        return null;
    }

    public static boolean canKill(PCard enemyGuard, PCard myUnit) {
        return !enemyGuard.ward && (myUnit.lethal || myUnit.attack >= enemyGuard.defense);
    }

    public static PCard copyWithoutWard(PCard c) {
        PCard card = new PCard(c.cardNumber, c.instanceId, c.cardType, c.cost, c.attack, c.defense, c.abilities, c.myHealthChange, c.opponentHealthChange, c.cardDraw, c.guard, c.charge, c.breakthrough, c.drain, c.lethal, false, c.used, c.area, c.lane);
        countValueOf(card);
        return card;
    }

    public static PCard copy(PCard c) {
        PCard card = new PCard(c.cardNumber, c.instanceId, c.cardType, c.cost, c.attack, c.defense, c.abilities, c.myHealthChange, c.opponentHealthChange, c.cardDraw, c.guard, c.charge, c.breakthrough, c.drain, c.lethal, c.ward, c.used, c.area, c.lane);
        countValueOf(card);
        return card;
    }

    public static PCard copyWithoutId(PCard c) {
        PCard card = new PCard(c.cardNumber, -1, c.cardType, c.cost, c.attack, c.defense, c.abilities, c.myHealthChange, c.opponentHealthChange, c.cardDraw, c.guard, c.charge, c.breakthrough, c.drain, c.lethal, c.ward, c.used, c.area, c.lane);
        countValueOf(card);
        return card;
    }

    public static List<PCard> copyListWithout(int index, List<PCard> list) {
        List<PCard> result = new ArrayList<>();
        for (int i = 0; i < list.size(); ++i)
            if (i != index)
                result.add(list.get(i));
        return result;
    }

    public static List<PCard> copyListWithout(int index1, int index2, List<PCard> list) {
        List<PCard> result = new ArrayList<>();
        for (int i = 0; i < list.size(); ++i)
            if (i != index1 && i != index2)
                result.add(list.get(i));
        return result;
    }

    public static List<PCard> copyListWithout(int index1, int index2, int index3, List<PCard> list) {
        List<PCard> result = new ArrayList<>();
        for (int i = 0; i < list.size(); ++i)
            if (i != index1 && i != index2 && i != index3)
                result.add(list.get(i));
        return result;
    }

    public static boolean canPlayCard(PCard card) {
        if (card.cost > MY_MANA)
            return false;
        return true;
    }

    public static void countValueOf(Situation situation) {
        if (situation.enemyHealth <= 0) {
            situation.value = 1000000000.0;
            return;
        }
        if (LOGGING)
            System.err.print("DEBUG VO: " + situation.command + ": ");
        situation.value = situation.enemyHealth * ENEMY_LIFE_PARAM + situation.myHealth * MY_LIFE_PARAM;
        if (LOGGING)
            System.err.print("S1: " + situation.myHand.size() + ": " + situation.value);
        for (PCard myCard : situation.myHand)
            situation.value += HAND_PARAM * myCard.value;
        if (LOGGING)
            System.err.print(" S2: " + situation.myBoard.size() + ": " + situation.value);
        int countLane0 = 0;
        int countLane1 = 0;
        for (PCard myCard : situation.myBoard) {
            situation.value += MY_PARAM * myCard.value;
            if (myCard.lane == 0)
                ++countLane0;
            else
                ++countLane1;
        }
        situation.value += countLane0 * countLane1 * DIFFERENT_LANE_PARAM;
        if (LOGGING)
            System.err.print(" S3: " + situation.enemyBoard.size() + ": " + situation.value);
        for (PCard enemyCard : situation.enemyBoard)
            situation.value += ENEMY_PARAM * enemyCard.value;
        if (LOGGING)
            System.err.println(" S4: " + situation.value);
    }

    public static class Situation {
        public final String command;
        public final List<PCard> myHand;
        public final List<PCard> myBoard;
        public final List<PCard> enemyBoard;
        public final int myHealth;
        public final int enemyHealth;
        public double value;

        public Situation(String command, List<PCard> myHand, List<PCard> myBoard, List<PCard> enemyBoard, int myHealth, int enemyHealth) {
            this.command = command;
            this.myHand = myHand;
            this.myBoard = myBoard;
            this.enemyBoard = enemyBoard;
            this.myHealth = myHealth;
            this.enemyHealth = enemyHealth;
        }

        public String print() {
            StringBuilder b = new StringBuilder();
            int used = 0;
            for (PCard card : myBoard)
                if (card.used)
                    ++used;
            b.append("S: " + value);
            b.append(" ME: " + myHealth + " HIM: " + enemyHealth);
            b.append(" U: ");
            b.append(myBoard.stream().map(u -> "" + u.instanceId + (u.used ? "M" : "")).collect(Collectors.joining(", ")));
            return b.toString();
        }
    }

    public static void countValueOf(PCard card) {
        if (card.cost > 5) {
            card.value = 0.0;
            return;
        }
        card.value = ATTACK_PARAM * abs(card.attack) + DEFENSE_PARAM * abs(card.defense);
        if (card.cardType == 0) {
            card.value += BASE_UNIT_PARAM;
            if (card.lethal)
                card.value += LETHAL_PARAM;
            if (card.ward)
                card.value += WARD_PARAM + card.attack * WARD_MULTI;
            if (card.guard)
                card.value += GUARD_PARAM + card.defense * GUARD_MULTI;
            if (card.breakthrough)
                card.value += BREAK_PARAM;
            if (card.drain)
                card.value += DRAIN_PARAM + card.attack * DRAIN_MULTI;
        } else if (card.cardType < 3) {
            if (card.lethal)
                card.value += LETHAL_PARAM;
            if (card.ward)
                card.value += WARD_PARAM;
            if (card.guard)
                card.value += GUARD_PARAM;
            if (card.breakthrough)
                card.value += BREAK_PARAM;
            if (card.drain)
                card.value += DRAIN_PARAM;
            if (card.cardType == 1)
                card.value *= GREEN_CARD_PARAM;
            else
                card.value *= RED_CARD_PARAM;
        }

        if (MY_MANA == 0) {
            if (card.area == 1) {
                if (card.cardType == 0)
                    card.value *= AREA_PARAM_1_UNIT;
                if (card.cardType == 1)
                    card.value *= AREA_PARAM_1_GREEN;
                if (card.cardType >= 2)
                    card.value *= AREA_PARAM_1_RED;
            }
            if (card.area == 2) {
                if (card.cardType == 0)
                    card.value *= AREA_PARAM_2_UNIT;
                if (card.cardType == 1)
                    card.value *= AREA_PARAM_2_GREEN;
                if (card.cardType >= 2)
                    card.value *= AREA_PARAM_2_RED;
            }
        }
    }

    public static double ENEMY_LIFE_PARAM;
    public static double MY_LIFE_PARAM;
    public static double ENEMY_PARAM;
    public static double MY_PARAM;
    public static double HAND_PARAM;
    public static double ATTACK_PARAM;
    public static double DEFENSE_PARAM;
    public static double BASE_UNIT_PARAM;
    public static double LETHAL_PARAM;
    public static double WARD_PARAM;
    public static double GUARD_PARAM;
    public static double BREAK_PARAM;
    public static double DRAIN_PARAM;
    public static double DRAIN_MULTI;
    public static double GUARD_MULTI;
    public static double WARD_MULTI;
    public static double DIFFERENT_LANE_PARAM;
    public static double AREA_PARAM_1_UNIT;
    public static double AREA_PARAM_1_RED;
    public static double AREA_PARAM_1_GREEN;
    public static double AREA_PARAM_2_UNIT;
    public static double AREA_PARAM_2_RED;
    public static double AREA_PARAM_2_GREEN;
    public static double GREEN_CARD_PARAM;
    public static double RED_CARD_PARAM;
    public static double[] COST_MULTI_PARAM = new double[6];
    public static double[] COST_DIV_PARAM = new double[6];


    public static class PCard implements Comparable<PCard> {
        public int cardNumber;
        public int instanceId;
        public int cardType;
        // 0: Creature
        // 1: Green item
        // 2: Red item
        // 3: Blue item
        public int cost;
        public int attack;
        public int defense;
        public String abilities;
        public int myHealthChange;
        public int opponentHealthChange;
        public int cardDraw;
        public int area;
        public int lane;
        public boolean guard;
        public boolean charge;
        public boolean breakthrough;
        public boolean drain;
        public boolean lethal;
        public boolean ward;
        public boolean used;
        // Breakthrough: Creatures with Breakthrough can deal extra damage to the opponent when they attack enemy
        //      creatures. If their attack damage is greater than the defending creature's defense, the excess damage is dealt to the opponent.
        // Charge: Creatures with Charge can attack the turn they are summoned.
        // Drain: Creatures with Drain heal the player of the amount of the damage they deal (when attacking only).
        // Guard: Enemy creatures must attack creatures with Guard first.
        // Lethal: Creatures with Lethal kill the creatures they deal damage to.
        // Ward: Creatures with Ward ignore once the next damage they would receive from any source. The "shield"
        //      given by the Ward ability is then lost.
        public Double value;

        public PCard(int cardNumber, int instanceId, int cardType, int cost, int attack, int defense, String abilities, int myHealthChange, int opponentHealthChange, int cardDraw, boolean guard, boolean charge, boolean breakthrough, boolean drain, boolean lethal, boolean ward, boolean used, int area, int lane) {
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
            this.area = area;
            this.lane = lane;
        }

        public PCard(int cardNumber, int instanceId, int cardType, int cost, int attack, int defense, String abilities, int myHealthChange, int opponentHealthChange, int cardDraw, int area, int lane) {
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
            this.used = false;
            this.area = area;
            this.lane = lane;
        }

        @Override
        public String toString() {
            return "CARD(" + cardNumber + " ID: " + instanceId + " HP: " + defense + " A: " + abilities + " TYPE: " + cardType + " AREA: " + area +
                    ")";
        }

        @Override
        public int compareTo(PCard o) {
            return -Double.compare(value, o.value);
        }
    }
}

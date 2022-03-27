import java.util.*;

/**
 * AI description
 * Construction phase:
 * - pick random card
 * Game phase:
 * - while there are onboard friendly creatures and inhand green items with cost less then current mana
 *      use random green item to a random friendly creature
 * - each creature attacks one randomly chosen available target
 * - if there are guards - target is chosen among them, otherwise it is any opponent creature or -1
 * - while there are inhand creatures with cost less then current mana summons random such creature
 * - while there are inhand red/blue items with cost less then current mana choose randomly one of them
 *      you can choose red item only if there are enemy creatures onboard - then use it on a random such creature
 *      for blue items there is 50% probability you hit face, otherwise like red items
 */
public class PlayerRandomWItems2lanes {
    private static class SimplifiedState {
        public HashMap<Integer, Integer> IdToCostMap = new HashMap<>();
        public ArrayList<Integer> HandCreaturesIds = new ArrayList<>();
        public ArrayList<Integer> HandGreenItemsIds = new ArrayList<>();
        public ArrayList<Integer> HandRedItemsIds = new ArrayList<>();
        public ArrayList<Integer> HandBlueItemsIds = new ArrayList<>();
        public ArrayList<Integer> CanAttackIds = new ArrayList<>();
        public ArrayList<Integer> GuardTargetIds = new ArrayList<>();
        public ArrayList<Integer> NonGuardTargetIds = new ArrayList<>();
        public ArrayList<Integer> FriendlyIds = new ArrayList<>();
        public ArrayList<Integer> TargetCreaturesIds = new ArrayList<>();
        public HashMap<Integer, Integer> AnyCreatureToLane = new HashMap<>();

        public int Mana;

        SimplifiedState(Scanner scanner) { // Warning: System.err.println from the class goes to Main error channel, and are not cached by the codingame
            NonGuardTargetIds.add(-1);

            int playerHealth = scanner.nextInt();
            Mana = scanner.nextInt();
            int playerDeck = scanner.nextInt();
            int playerDraw = scanner.nextInt();
            int oppHealth = scanner.nextInt();
            int oppMana = scanner.nextInt();
            int oppDeck = scanner.nextInt();
            int oppDraw = scanner.nextInt();
            //System.err.format("my deck: %d, opp deck: %d\n", playerDeck, oppDeck);
            //System.err.format("my draw: %d, opp draw: %d\n", playerDraw, oppDraw);
            int opponentHand = scanner.nextInt();
            int opponentActions = scanner.nextInt();
            //System.err.format("oppA - " + opponentActions + "\n");
            if (scanner.hasNextLine())
                scanner.nextLine();
            for (int i = 0; i < opponentActions; i++) {
                String cardNumberAndAction = scanner.nextLine();
                //System.err.format("OPPACTION: %s\n", cardNumberAndAction);
            }
            int cardCount = scanner.nextInt();
            for (int i = 0; i < cardCount; i++) {
                int cardName = scanner.nextInt();
                int instanceId = scanner.nextInt();
                int location = scanner.nextInt();
                int type = scanner.nextInt();
                int cost = scanner.nextInt();
                int attack = scanner.nextInt();
                int defense = scanner.nextInt();
                String abilities = scanner.next();
                int myHealthChange = scanner.nextInt();
                int opponentHealthChange = scanner.nextInt();
                int cardDraw = scanner.nextInt();
                int area = scanner.nextInt();
                int lane = scanner.nextInt();
                //System.err.format("CARD %d (#%d) // lane=%d\n", instanceId, cardName, lane);

                if (location == 0) { // hand
                    IdToCostMap.put(instanceId, cost);
                    if (type == 0) // card is creature
                        HandCreaturesIds.add(instanceId);
                    else if (type == 1) // card is a green item
                        HandGreenItemsIds.add(instanceId);
                    else if (type == 2) // card is a red item
                        HandRedItemsIds.add(instanceId);
                    else if (type == 3) // card is a blue item
                        HandBlueItemsIds.add(instanceId);
                }
                if (location == 1) { // board
                    AnyCreatureToLane.put(instanceId, lane);
                    FriendlyIds.add(instanceId);
                    CanAttackIds.add(instanceId);
                }
                if (location == -1) { // opponent board
                    AnyCreatureToLane.put(instanceId, lane);
                    TargetCreaturesIds.add(instanceId);
                    if (abilities.charAt(3) == 'G')
                        GuardTargetIds.add(instanceId);
                    else
                        NonGuardTargetIds.add(instanceId);
                }
            }
        }
    }

    private static String constructionPhase(Random random, Scanner scanner) {
        SimplifiedState constructionState = new SimplifiedState(scanner);

        int candidates = constructionState.HandCreaturesIds.size() + constructionState.HandGreenItemsIds.size() +
                constructionState.HandRedItemsIds.size() + constructionState.HandBlueItemsIds.size();
        int[] countTimesChosen = new int[candidates];

        for (int i = 0; i < 30; i++) {
            int c;
            do {
                c = random.nextInt(candidates);
            } while (countTimesChosen[c] >= 3);
            countTimesChosen[c]++;
        }

        List<String> commands = new ArrayList<>();
        for (int c = 0; c < candidates; c++)
            for (int i = 0; i < countTimesChosen[c]; i++)
                commands.add("PICK " + c);
        return String.join(" ; ", commands);
    }

    public static void main(String[] args) {
        Random random = new Random();
        Scanner scanner = new Scanner(System.in);

        System.out.println(constructionPhase(random, scanner));

        while (true) {
            SimplifiedState state = new SimplifiedState(scanner);
            StringBuilder sb = new StringBuilder();
            sb.append("; ");
            boolean fullbonus = state.Mana == 13;

            // green items phase
            while (true) {
                state.HandGreenItemsIds.removeIf(c -> state.IdToCostMap.get(c) > state.Mana);
                System.err.println(String.format("GreenItems phase: %d items can be used on %d creatures.", state.HandGreenItemsIds.size(), state.FriendlyIds.size()));
                if (state.HandGreenItemsIds.isEmpty() || state.FriendlyIds.isEmpty())
                    break;

                Integer id = state.HandGreenItemsIds.get(random.nextInt(state.HandGreenItemsIds.size()));
                state.HandGreenItemsIds.remove(id);
                state.Mana -= state.IdToCostMap.get(id);
                int idt = state.FriendlyIds.get(random.nextInt(state.FriendlyIds.size()));
                sb.append(String.format("USE %d %d; ", id, idt));
            }

            // attack phase
            List<Integer> targets = state.GuardTargetIds.isEmpty() ? state.NonGuardTargetIds : state.GuardTargetIds;
            System.err.println(String.format("Attack phase: %d creatures can attack %d targets.", state.CanAttackIds.size(), targets.size()));
            while (!state.CanAttackIds.isEmpty()) {
                Integer ida = state.CanAttackIds.get(random.nextInt(state.CanAttackIds.size()));
                state.CanAttackIds.remove(ida);

                int idt = targets.get(random.nextInt(targets.size()));
                sb.append(String.format("ATTACK %d %d att; ", ida, idt));
            }

            // summon phase
            while (true) {
                state.HandCreaturesIds.removeIf(c -> state.IdToCostMap.get(c) > state.Mana);
                System.err.println(String.format("Summon phase: %d creatures can be summoned with mana limit %d.", state.HandCreaturesIds.size(), state.Mana));
                if (state.HandCreaturesIds.isEmpty())
                    break;

                Integer id = state.HandCreaturesIds.get(random.nextInt(state.HandCreaturesIds.size()));
                state.HandCreaturesIds.remove(id);
                state.Mana -= state.IdToCostMap.get(id);
                sb.append(String.format("SUMMON %d %d; ", id, random.nextInt(2)));
            }

            // red/blue items phase
            while (true) {
                state.HandRedItemsIds.removeIf(c -> state.IdToCostMap.get(c) > state.Mana);
                state.HandBlueItemsIds.removeIf(c -> state.IdToCostMap.get(c) > state.Mana);
                System.err.println(String.format("RedBlueItems phase: %d red items and %d blue items can be used on %d creatures (+player).", state.HandRedItemsIds.size(), state.HandBlueItemsIds.size(), state.TargetCreaturesIds.size()));

                if (state.TargetCreaturesIds.size() == 0)
                    state.HandRedItemsIds.clear();

                if (state.HandRedItemsIds.isEmpty() && state.HandBlueItemsIds.isEmpty())
                    break;

                int num = random.nextInt(state.HandRedItemsIds.size() + state.HandBlueItemsIds.size());
                if (num < state.HandRedItemsIds.size()) { // red item use
                    Integer id = state.HandRedItemsIds.get(num);
                    state.HandRedItemsIds.remove(id);
                    state.Mana -= state.IdToCostMap.get(id);
                    int idt = state.TargetCreaturesIds.get(random.nextInt(state.TargetCreaturesIds.size()));
                    sb.append(String.format("USE %d %d use; ", id, idt));
                } else { // blue item use
                    Integer id = state.HandBlueItemsIds.get(num - state.HandRedItemsIds.size());
                    state.HandBlueItemsIds.remove(id);
                    state.Mana -= state.IdToCostMap.get(id);
                    int idt = -1;
                    if (random.nextInt(2) < 1 && state.TargetCreaturesIds.size() > 0) // 50% to creature target
                        idt = state.TargetCreaturesIds.get(random.nextInt(state.TargetCreaturesIds.size()));
                    sb.append(String.format("USE %d %d; ", id, idt));
                }
            }

            //if (fullbonus)
            System.out.println(sb.toString());
            //else
            //  System.out.println(";");
        }
    }
}
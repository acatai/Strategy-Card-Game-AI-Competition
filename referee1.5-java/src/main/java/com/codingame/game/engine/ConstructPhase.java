package com.codingame.game.engine;

import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class ConstructPhase {
    public final List<Card> cardsForConstruction;
    //TODO we shouldn't mix arrays and collections, List<List<Card>> would be better
    public final List<Card>[] chosenCards;
    public final int[][] chosenQuantities;
    public final List<Card>[] decks; // after shuffle and assigning unique id's

    public final String[] text = new String[2];

    private final Random choicesRNG;
    private final Random[] shufflesRNG;
    private final RefereeParams params;

    // todo - add function and field documentation

    public ConstructPhase(RefereeParams params) {
        this.params = params;

        cardsForConstruction = new ArrayList<>();
        chosenCards = new ArrayList[]{new ArrayList<Card>(), new ArrayList<Card>()};
        decks = new ArrayList[]{new ArrayList<Card>(), new ArrayList<Card>()};
        chosenQuantities = new int[2][Constants.CARDSET.size() + 1];

        for (int player = 0; player < 2; player++)
            text[player] = "";

        choicesRNG = params.constructedChoicesRNG;
        shufflesRNG = new Random[]{params.shufflePlayer0RNG, params.shufflePlayer1RNG};
    }

    public void PrepareConstructed() {
        List<Card> allowedCards = new ArrayList<>(Constants.CARDSET.values());

        if (params.predefinedConstructedIds != null) { // parameter-forced construction choices
            for (int pick = 0; pick < Constants.CARDS_IN_CONSTRUCTED; pick++)
                cardsForConstruction.add(Constants.CARDSET.get(params.predefinedConstructedIds[pick]));
            return;
        }

        ArrayList<Integer> cardsForConstructionIds = new ArrayList<>();
        for (int pick = 0; pick < Math.min(Constants.CARDS_IN_CONSTRUCTED, allowedCards.size()); pick++) {
            int i;
            do {
                i = choicesRNG.nextInt(allowedCards.size());
            } while (cardsForConstructionIds.contains(i));
            cardsForConstructionIds.add(i);
        }
        for (int pick : cardsForConstructionIds)
            cardsForConstruction.add(allowedCards.get(pick));

        cardsForConstruction.sort(new Card.CostComparator());
    }

    private Card handlePassCommand(int player) throws InvalidActionHard {
        Optional<Card> choice = cardsForConstruction.stream()
                .filter(c -> chosenQuantities[player][c.baseId] < Constants.CONSTRUCTED_MAX_COPY)
                .findFirst();
        if (choice.isPresent())
            return choice.get();
        throw new InvalidActionHard("Something went horrible wrong. No card available to choose.");
    }

    private Card handlePickCommand(String[] command, int player) throws InvalidActionHard {
        int value;
        try {
            value = Integer.parseInt(command[1]);
        } catch (NumberFormatException | ArrayIndexOutOfBoundsException e) {
            throw new InvalidActionHard("Invalid \"PICK\" argument. Expected integer (card position in presented list).");
        }

        if (value < 0 || value >= Constants.CARDS_IN_CONSTRUCTED)
            throw new InvalidActionHard("Invalid action argument. \"PICK\" argument should be an integer between 0 and " + (Constants.CARDS_IN_CONSTRUCTED - 1) + ".");
        Card choice = cardsForConstruction.get(value);
        if (chosenQuantities[player][choice.baseId] >= Constants.CONSTRUCTED_MAX_COPY)
            throw new InvalidActionHard("Invalid action argument. Card can be chosen at most " + Constants.CONSTRUCTED_MAX_COPY + " times.");
        return choice;
    }

    private Card handleChooseCommand(String[] command, int player) throws InvalidActionHard {
        int value;
        try {
            value = Integer.parseInt(command[1]);
        } catch (NumberFormatException | ArrayIndexOutOfBoundsException e) {
            throw new InvalidActionHard("Invalid \"CHOOSE\" argument. Expected integer (card base id).");
        }
        Optional<Card> choice = cardsForConstruction.stream()
                .filter(c -> value == c.baseId)
                .findAny();

        if (!choice.isPresent())
            throw new InvalidActionHard("Invalid action format. \"CHOOSE\" argument should be valid card's base id.");

        if (chosenQuantities[player][choice.get().baseId] >= Constants.CONSTRUCTED_MAX_COPY)
            throw new InvalidActionHard("Invalid action argument. Card can be chosen at most " + Constants.CONSTRUCTED_MAX_COPY + " times.");
        return choice.get();
    }


    public void playerChoice(String action, int player) throws InvalidActionHard {
        Card choice;
        String[] command = action.split(" ", 3);
        String text = command.length < 3 ? "" : command[2].trim();

        switch (command[0]) {
            case "PASS":
                choice = handlePassCommand(player);
                break;
            case "PICK":
                choice = handlePickCommand(command, player);
                break;
            case "CHOOSE":
                choice = handleChooseCommand(command, player);
                break;
            default:
                throw new InvalidActionHard("Invalid action. Expected  \"PICK [0...n]\", \"CHOOSE id\" or \"PASS\".");
        }
        chosenCards[player].add(choice);
        chosenQuantities[player][choice.baseId] += 1;
        if (!text.isEmpty())
            this.text[player] += text + " ";
    }

    public String handlePlayerChoices(String actions, int player) throws InvalidActionHard {
        for (String action : actions.split(";")) {
            action = action.trim();
            if (action.isEmpty())
                continue; // empty action is a valid action
            if (action.equals("PASS"))
                while (chosenCards[player].size() < Constants.CARDS_IN_DECK)
                    playerChoice("PASS", player);
            else
                playerChoice(action, player);
        }
        return summarizeChoices(player);
    }

    public void shuffleDecks() {
        for (int player = 0; player < 2; player++) {
            for (Card c : chosenCards[player])
                decks[player].add(new Card(c, true));
            Collections.shuffle(decks[player], shufflesRNG[player]);
        }
    }

    public String summarizeChoices(int player) {
        StringJoiner logMessage = new StringJoiner(", ");
        for (int i = 0; i < Constants.CARDSET.size(); i++)
            if (chosenQuantities[player][i] > 0)
                logMessage.add(i + "x" + chosenQuantities[player][i]);
        return logMessage.toString();
    }


    public String[] getMockPlayersInput(int player) {
        ArrayList<String> lines = new ArrayList<>();
        lines.add(join(Constants.INITIAL_HEALTH, 0, 0, 0));
        lines.add(join(Constants.INITIAL_HEALTH, 0, 0, 0));
        lines.add("0 0");
        lines.add(String.valueOf(Math.min(Constants.CARDS_IN_CONSTRUCTED, this.cardsForConstruction.size())));

        return lines.stream().toArray(String[]::new);
    }

    static public String join(Object... args) {
        return Stream.of(args).map(String::valueOf).collect(Collectors.joining(" "));
    }
}

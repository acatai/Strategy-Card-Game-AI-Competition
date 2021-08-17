package com.codingame.game.engine;

import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.stream.Stream;

public class ConstructPhase {
    public enum Difficulty {NORMAL, LESS_EASY, EASY, VERY_EASY}

    public ConstructPhase.Difficulty difficulty;
    public List<Card> allowedCards;
    //TODO List should be used everywhere, apart from creation
    public ArrayList<Card> cardsForConstruction;
    //TODO we shouldn't mix arrays and collections, List<List<Card>> would be better
    public ArrayList<Card>[] chosenCards;
    public int[][] chosenQuantities;
    public ArrayList<Card>[] decks; // after shuffle and assigning unique id's

    public String[] text = new String[2];

    private final Random choicesRNG;
    private final Random[] shufflesRNG;
    private final RefereeParams params;

    public int[] showdraftQuantities;
    public ArrayList<Card> showdraftCards;

    // todo - add function and field documentation

    public ConstructPhase(ConstructPhase.Difficulty difficulty, RefereeParams params)
    {
        this.difficulty = difficulty;
        this.params = params;

        chosenCards = new ArrayList[] {new ArrayList<Card>(), new ArrayList<Card>()};
        decks = new ArrayList[] {new ArrayList<Card>(), new ArrayList<Card>()};
        chosenQuantities = new int[2][Constants.CARDSET.size()+1];

        choicesRNG = params.draftChoicesRNG;
        shufflesRNG = new Random[] {params.shufflePlayer0RNG, params.shufflePlayer1RNG};
    }

    private boolean isVeryEasyCard(Card card)
    {
        return card.type == Card.Type.CREATURE
                && !card.keywords.hasAnyKeyword()
                && card.myHealthChange == 0 && card.oppHealthChange == 0 && card.cardDraw == 0;
    }

    private void prepareAllowedCards()
    {
        Collection<Card> cardBase = Constants.CARDSET.values();

        if (difficulty == ConstructPhase.Difficulty.NORMAL) {
            allowedCards = new ArrayList<>(cardBase);
        } else if (difficulty == ConstructPhase.Difficulty.LESS_EASY) {
            allowedCards = cardBase.stream()
                    .filter(card -> !card.keywords.hasDrain && !card.keywords.hasLethal && !card.keywords.hasWard)
                    .collect(Collectors.toList());
        } else if (difficulty == ConstructPhase.Difficulty.EASY) {
            allowedCards = cardBase.stream()
                    .filter(card -> card.type == Card.Type.CREATURE)
                    .filter(card -> !card.keywords.hasDrain && !card.keywords.hasLethal && !card.keywords.hasWard)
                    .collect(Collectors.toList());
        } else {
            allowedCards = cardBase.stream()
                    .filter(this::isVeryEasyCard)
                    .collect(Collectors.toList());
        }
    }
    public void PrepareConstructed()
    {
        prepareAllowedCards();
        cardsForConstruction = new ArrayList<>();
        if (params.predefinedConstructedIds != null) // parameter-forced draft choices
        {
            for(int pick = 0; pick <  Constants.CARDS_IN_CONSTRUCTED; pick++)
                cardsForConstruction.add(Constants.CARDSET.get(params.predefinedConstructedIds[pick]));
            return;
        }

        ArrayList<Integer> drafting = new ArrayList<>();
        for (int pick = 0; pick < Math.min(Constants.CARDS_IN_CONSTRUCTED, allowedCards.size()); pick++)
        {
            int i;
            do
            {
                i = choicesRNG.nextInt(allowedCards.size());
            } while (drafting.contains(i));
            drafting.add(i);
        }
        for (int pick : drafting)
            cardsForConstruction.add(allowedCards.get(pick));

        prepareShowdraft();
    }

    private void prepareShowdraft()
    {
        showdraftQuantities = new int[161];
        for (Card c : cardsForConstruction)
            showdraftQuantities[c.baseId]++;

        showdraftCards = new ArrayList<>(cardsForConstruction);

        showdraftCards.sort((lhs, rhs) -> {
            if (lhs.cost == rhs.cost && showdraftQuantities[rhs.baseId] == showdraftQuantities[lhs.baseId])
                return lhs.baseId - rhs.baseId;
            else if (lhs.cost == rhs.cost)
                return showdraftQuantities[rhs.baseId] - showdraftQuantities[lhs.baseId];
            else
                return lhs.cost - rhs.cost;
        });
    }

    private Card handlePassCommand(String[] command, int player) throws InvalidActionHard{
        Optional<Card> choice = cardsForConstruction.stream().
                filter(c -> chosenQuantities[player][c.baseId] < Constants.CONSTRUCTED_MAX_COPY).
                findFirst();
        if (choice.isPresent())
            return choice.get();
        throw new InvalidActionHard("Something went horrible wrong. No card available to choose.");
    }

    private Card handlePickCommand(String[] command, int player) throws InvalidActionHard {
        int value = Integer.parseInt(command[1]);
        if (value < 0 || value >= Constants.CARDS_IN_CONSTRUCTED)
            throw  new InvalidActionHard("Invalid action argument. \"PICK\" argument should be between 0 and " + (Constants.CARDS_IN_CONSTRUCTED -1) + ".");
        Card choice = cardsForConstruction.get(value);
        if (chosenQuantities[player][choice.baseId] >= Constants.CONSTRUCTED_MAX_COPY)
            throw new InvalidActionHard("Invalid action argument. Card can be chosen maximally three times.");
        return choice;
    }

    private Card handleChooseCommand(String[] command, int player) throws InvalidActionHard{
        int value = Integer.parseInt(command[1]);
        Optional<Card> choice = cardsForConstruction.stream().
                filter(c -> value == c.baseId).
                findAny();

        if (!choice.isPresent())
            throw new InvalidActionHard("Invalid action format. \"CHOOSE\" argument should be valid card's base id.");

        if (chosenQuantities[player][choice.get().baseId] >= Constants.CONSTRUCTED_MAX_COPY)
            throw new InvalidActionHard("Invalid action argument. Card can be chosen maximally three times.");
        return choice.get();
    }


    public ConstructPhase.ChoiceResultPair PlayerChoice_CHANGED(String action, int player) throws InvalidActionHard
    {
        Card choice = null;
        String text = "";

        String[] command = action.split(" ", 3);
        text = command.length < 3 ? "" : command[2].trim();

        switch (command[0]){
            case "PASS":
                choice = handlePassCommand(command, player);
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

        return new ChoiceResultPair(choice, text);
    }

    public void ShuffleDecks()
    {
        for (int player=0; player < 2; player++)
        {
            for (Card c : chosenCards[player])
                decks[player].add(new Card(c));

            Collections.shuffle(decks[player], shufflesRNG[player]);
            for (int i=0; i < decks[player].size(); i++)
                decks[player].get(i).id = 2 * i + player + 1;
        }
    }


    public static class ChoiceResultPair
    {
        public Card card;
        public String text;

        public ChoiceResultPair(Card card, String text)
        {
            this.card = card;
            this.text = text;
        }
    }

    public String[] getMockPlayersInput(int player, int turn) {
        ArrayList<String> lines = new ArrayList<>();
        lines.add(join(Constants.INITIAL_HEALTH, 0, turn , 25, 0));
        lines.add(join(Constants.INITIAL_HEALTH, 0, player==0 ? turn : (turn+1), 25, 0));
        lines.add("0 0");
        lines.add(String.valueOf(Math.min(Constants.CARDS_IN_CONSTRUCTED, this.allowedCards.size())));

        return lines.stream().toArray(String[]::new);
    }

    static public String join(Object... args) {
        return Stream.of(args).map(String::valueOf).collect(Collectors.joining(" "));
    }
}

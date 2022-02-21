package com.codingame.game.engine;

import com.codingame.game.Player;
import com.codingame.gameengine.core.MultiplayerGameManager;

import java.util.Properties;
import java.util.Random;

public class RefereeParams {
    public final Random cardGenRNG;
    public final Random constructedChoicesRNG;
    public final Random shufflePlayer0RNG;
    public final Random shufflePlayer1RNG;
    public final String predefinedCardListFile;
    public final Integer[] predefinedConstructedIds;
    private Properties params;

    public RefereeParams(long cardGenSeed, long constructedChoicesSeed, long shufflePlayer0Seed, long shufflePlayer1Seed) {
        cardGenRNG = new Random(cardGenSeed);
        constructedChoicesRNG = new Random(constructedChoicesSeed);
        shufflePlayer0RNG = new Random(shufflePlayer0Seed);
        shufflePlayer1RNG = new Random(shufflePlayer1Seed);
        predefinedCardListFile = null;
        predefinedConstructedIds = null;
    }

    public RefereeParams(MultiplayerGameManager<Player> gameManager) {
        // pure initialization if seed set by the manager
        long mainSeed = gameManager.getSeed();
        Random RNG = new Random(mainSeed);
        long cardGenSeed = RNG.nextLong();
        long constructedChoicesSeed = RNG.nextLong();
        long shufflePlayer0Seed = RNG.nextLong();
        long shufflePlayer1Seed = RNG.nextLong();

        params = gameManager.getGameParameters();

        if (isNumber(params.getProperty("seed"))) { // overriding when seed given as parameter
            mainSeed = Long.parseLong(params.getProperty("seed"));
            RNG = new Random(mainSeed);
            cardGenSeed = RNG.nextLong();
            constructedChoicesSeed = RNG.nextLong();
            shufflePlayer0Seed = RNG.nextLong();
            shufflePlayer1Seed = RNG.nextLong();
        }

        // overriding remaining seeds
        if (isNumber(params.getProperty("cardGenSeed")))
            cardGenSeed = Long.parseLong(params.getProperty("cardGenSeed"));
        if (isNumber(params.getProperty("constructedChoicesSeed")))
            constructedChoicesSeed = Long.parseLong(params.getProperty("constructedChoicesSeed"));
        if (isNumber(params.getProperty("shufflePlayer0Seed")))
            shufflePlayer0Seed = Long.parseLong(params.getProperty("shufflePlayer0Seed"));
        if (isNumber(params.getProperty("shufflePlayer1Seed")))
            shufflePlayer1Seed = Long.parseLong(params.getProperty("shufflePlayer1Seed"));

        if (params.getProperty("predefinedConstructedIds") != null) {
            predefinedConstructedIds = new Integer[Constants.CARDS_IN_DECK];
            String[] picks = params.getProperty("predefinedConstructedIds").split(",");

            assert (picks.length >= Constants.CARDS_IN_DECK);

            for (int pick = 0; pick < Constants.CARDS_IN_DECK; pick++)
                predefinedConstructedIds[pick] = Integer.parseInt(picks[pick].trim());
        } else {
            predefinedConstructedIds = null;
        }

        if (params.getProperty("predefinedCardListFile") != null)
            predefinedCardListFile = params.getProperty("predefinedCardListFile");
        else
            predefinedCardListFile = null;

        // update params values
        // we can't update predefinedConstructedIds if there were not set by the user...
        params.setProperty("cardGenSeed", Long.toString(cardGenSeed));
        params.setProperty("constructedChoicesSeed", Long.toString(constructedChoicesSeed));
        params.setProperty("shufflePlayer0Seed", Long.toString(shufflePlayer0Seed));
        params.setProperty("shufflePlayer1Seed", Long.toString(shufflePlayer1Seed));

        // set RNG's
        cardGenRNG = new Random(cardGenSeed);
        constructedChoicesRNG = new Random(constructedChoicesSeed);
        shufflePlayer0RNG = new Random(shufflePlayer0Seed);
        shufflePlayer1RNG = new Random(shufflePlayer1Seed);

        //System.out.println(toString());
    }

    @Override
    public String toString() {
        return
                "cardGenSeed" + "=" + params.getProperty("cardGenSeed") + "\n" +
                "constructedChoicesSeed" + "=" + params.getProperty("constructedChoicesSeed") + "\n" +
                "shufflePlayer0Seed" + "=" + params.getProperty("shufflePlayer0Seed") + "\n" +
                "shufflePlayer1Seed" + "=" + params.getProperty("shufflePlayer1Seed") + "\n";
//                "predefinedConstructedIds" + "=" + params.getProperty("predefinedConstructedIds") + "\n";
    }
    // todo toString?

    private boolean isNumber(String str) {
        try {
            Long.parseLong(str);
            return true;
        } catch (NumberFormatException nfe) {
        }
        return false;
    }
}

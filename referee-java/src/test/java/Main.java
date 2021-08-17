//import com.codingame.gameengine.runner.Constants;
import com.codingame.game.engine.Constants;
import com.codingame.gameengine.runner.MultiplayerGameRunner;
import com.codingame.gameengine.runner.simulate.GameResult;

import java.util.Properties;

public class Main
{
    public static void main(String[] args)
    {
        if (args.length > 0)
        {
            Constants.TIMELIMIT_GAMETURN = Integer.parseInt(args[0]);
        }

        if (args.length > 1)
        {
            Constants.LANES = Integer.parseInt(args[1]);
        }

        Constants.VERBOSE_LEVEL = 2;
        System.setProperty("league.level", "4");


        Constants.LANES = 1;
        if (Constants.LANES > 1)
          runner(PlayerRandomWItems2lanes.class, PlayerRandomWItems2lanes.class).start();
        else
          runner(PlayerRandomWItems.class, PlayerRandomWItems.class).start();


        // fight(PlayerRandom.class, PlayerAggroStupid.class, 10);
        // fight(PlayerRandom.class, PlayerAggroStupid.class);
        // fight(PlayerRandom.class, PlayerDraftErrors.class);
        // fight(PlayerRandom.class, PlayerRandomSimplified.class);
        // fight(PlayerRandom.class, PlayerSimplest.class);
        // fight(PlayerRandom.class, PlayerRandom.class, 5);
        // fight(PlayerRandom.class, PlayerRandomWItems.class, 10);
        // fight(PlayerRandomWItems.class, PlayerAggroStupid.class, 10);
        //fight(PlayerAggroStupidWItems.class, PlayerAggroStupid.class, 10);
        //fight(PlayerAggroStupid.class, PlayerAggroStupidWItems.class, 10);

    }

    public static void fight(Class<?> playerA, Class<?> playerB)
    {
        fight(playerA, playerB, 1, true);
    }

    public static void fight(Class<?> playerA, Class<?> playerB, int rounds)
    {
        fight(playerA, playerB, rounds, false);
    }

    public static void fight(Class<?> playerA, Class<?> playerB, int rounds, boolean silent)
    {
        int scoreA = 0;
        int scoreB = 0;
        long time = 0;

        for (int round = 0; round < rounds; ++round)
        {
            long startTime = System.currentTimeMillis();
            MultiplayerGameRunner gameRunner = runner(playerA, playerB);
            GameResult gameResult = gameRunner.simulate();
            long elapsedTime = System.currentTimeMillis() - startTime;
            scoreA += gameResult.scores.get(0);
            scoreB += gameResult.scores.get(1);
            time += elapsedTime;

            if (!silent) System.out.println("Game time: " + elapsedTime);
        }

        System.out.println("Player A scored " + scoreA + " in " + rounds + " rounds.");
        System.out.println("Player B scored " + scoreB + " in " + rounds + " rounds.");
        System.out.println("Overall time: " + time + " ms. (avg. " + (time/rounds) + " ms. per game).");
    }

    public static MultiplayerGameRunner runner(Class<?> playerA, Class<?> playerB)
    {
      MultiplayerGameRunner gameRunner = new MultiplayerGameRunner();
      Properties gameParameters = new Properties();
      // todo set difficulty level
      //gameRunner.setSeed(1279960l);
      //gameParameters.setProperty("seed", "12700");
      //gameParameters.setProperty("draftChoicesSeed", "-5113144502819146988");
      //gameParameters.setProperty("shufflePlayer0Seed", "127");
      //gameParameters.setProperty("shufflePlayer1Seed", "333");
      // 1
      //gameParameters.setProperty("predefinedDraftIds", "1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,");
      //gameParameters.setProperty("predefinedDraftIds", "28 28 28,28 28 28,28 28 28,28 28 28,28 28 28,28 28 28,28 28 28,28 28 28,28 28 28,28 28 28,28 28 28,28 28 28,28 28 28,28 28 28,28 28 28,28 28 28,28 28 28,28 28 28,28 28 28,28 28 28,28 28 28,28 28 28,28 28 28,28 28 28,28 28 28,28 28 28,28 28 28,28 28 28,28 28 28,28 28 28");
      // 10
      //gameParameters.setProperty("predefinedDraftIds", "1 1 1,1 2 1,3 1 1,4 1 1,5 1 1,6 1 1,7 1 1,1 8 1,1 9 1,1 10 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,");
      // 15
      //gameParameters.setProperty("predefinedDraftIds", "1 1 1,1 2 1,3 1 1,4 1 1,5 1 1,6 1 1,7 1 1,1 8 1,1 9 1,1 10 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 11,1 12 1,1 1 13,1 14 1,1 1 1,15 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,1 1 1,");
      // 20
      //gameParameters.setProperty("predefinedDraftIds", "1 2 3 , 3 2 1 , 2 2 2 ,160 160 160, 150 151 152, 130 131 132, 7 7 7, 8 8 8, 9 9 9, 10 10 10, 11 11 11, 12 12 12, 13 13 13, 14 14 14, 15 15 15, 16 16 16, 17 17 17, 18 18 18, 19 19 19, 20 20 20, 11 11 11, 12 12 12, 13 13 13, 14 14 14, 15 15 15, 16 16 16, 17 17 17, 18 18 18, 19 19 19, 30 30 30");
      // 30
      //gameParameters.setProperty("predefinedDraftIds", "1 2 3 , 3 2 1 , 2 2 2 ,160 160 160, 150 151 152, 130 131 132, 7 7 7, 8 8 8, 9 9 9, 10 10 10, 11 11 11, 12 12 12, 53 13 13, 14 14 14, 55 15 15, 56 16 16, 57 17 17, 58 18 18, 19 19 19, 20 20 20, 11 11 11, 12 12 12, 13 13 13, 14 14 14, 15 15 15, 16 16 16, 17 17 17, 18 18 18, 19 19 19, 30 30 30");
      // 90
      //gameParameters.setProperty("predefinedDraftIds", "1 2 3,4 5 6,7 8 9,10 11 12,13 14 15,16 17 18,19 20 21,22 23 24,25 26 27,28 29 30,31 32 33,34 35 36,37 38 39,40 41 42,43 44 45,46 47 48,49 50 51,52 53 54,55 56 57,58 59 60,61 62 63,64 65 66,67 68 69,70 71 72,73 74 75,76 77 78,79 80 81,82 83 84,85 86 87,88 89 90");
      //gameParameters.setProperty("predefinedDraftIds", "91 92 93,94 95 96,97 98 99,100 101 102,103 104 105,106 107 108,109 110 111,112 113 114,115 116 117,118 119 120,121 122 123,124 125 126,127 128 129,130 131 132,133 134 135,136 137 138,139 140 141,142 143 144,145 146 147,148 149 150,151 152 153,154 155 156,157 158 159,160 160 160,160 160 160,160 160 160,160 160 160,160 160 160,160 160 160,160 160 160");

      gameRunner.setGameParameters(gameParameters);

      gameRunner.addAgent(playerA);
      gameRunner.addAgent(playerB);

      return gameRunner;
    }
}

package com.codingame.gameengine.runner;

import java.io.IOException;
import java.io.StringReader;
import java.lang.reflect.Field;
import java.nio.charset.Charset;
import java.nio.file.Paths;
import java.util.*;

import com.codingame.game.engine.Card;
import com.codingame.game.engine.cardgenerator.CardGenerator;
import com.codingame.gameengine.runner.simulate.GameResult;
import org.apache.commons.cli.*;

import com.codingame.game.engine.Constants;
import com.google.common.io.Files;
import com.google.gson.Gson;

public class CommandLineInterface {
    public static void main(String[] args) {
        Options playOptions = new Options();
        playOptions
                .addOption(Option.builder("d").hasArg().desc("Referee initial data").build())
                .addOption(Option.builder("p1").hasArg().required().desc("Required. Player 1 command line.").build())
                .addOption(Option.builder("p2").hasArg().required().desc("Required. Player 2 command line.").build())
                .addOption(Option.builder("l").hasArg().longOpt("logs").desc("File output for logs").build())
                .addOption(Option.builder("s").longOpt("server").desc("Server mode").build())
                .addOption(Option.builder("h").longOpt("help").desc("Print the help").build());
        Options generateOptions = new Options();
        generateOptions
                .addOption(Option.builder().longOpt("html").hasArg().desc("Path to the resulting html file").build())
                .addOption(Option.builder("n").hasArg().desc("Set the number of created cards. Default: 80").build())
                .addOption(Option.builder("h").longOpt("help").desc("Print the help").build());
        try {
            boolean printHelp = false;
            if (args.length > 0 && Objects.equals(args[0], "generate")) {
                CommandLine cmd = new DefaultParser().parse(generateOptions, args);
                printHelp = handleGenerate(cmd);
            } else if (args.length > 0 && Objects.equals(args[0], "play")) {
                CommandLine cmd = new DefaultParser().parse(playOptions, args);
                printHelp = handlePlay(cmd);
            } else {
                printHelp = true;
            }
            if (printHelp)
                printHelp(generateOptions, playOptions);
        } catch (ParseException e) {
            printHelp(generateOptions, playOptions);
        } catch (IOException | NoSuchFieldException | IllegalAccessException e) {
            e.printStackTrace();
        }
    }

    static void printHelp(Options generateOptions, Options playOptions) {
        HelpFormatter hf = new HelpFormatter();
        hf.printHelp(
                "generate [-html <File for output html>] [-n <Number of cards>] [{-h | --help}]",
                "Generate example cardset using build-in generator",
                generateOptions,
                ""
        );
        System.out.println("");
        hf.printHelp(
                "play -p1 <Player1 command line> -p2 <Player2 command line> [{-s | --server}] [{-l | --logs} <File output for logs>] [-d <Referee initial data] [{-h | --help}]",
                "Play a game between given two players",
                playOptions,
                ""
        );
        System.exit(0);
    }

    static boolean handleGenerate(CommandLine cmd) throws IOException {
        if (cmd.hasOption("help"))
            return true;

        int n;
        CardGenerator gen = new CardGenerator(new Random(), "cardWeights.json");
        if (cmd.hasOption("n"))
            n = Integer.parseInt(cmd.getOptionValue("n"));
        else
            n = 80;

        HashMap<Integer, Card> cardset = new HashMap<>();
        for (int i = 0; i < n; i++) {
            Card c = gen.generateCard(i);
            cardset.put(c.baseId, c);
        }
        if (cmd.hasOption("html")) {
            Constants.GenerateCardlistHTML(cardset, "cardset_template.html", cmd.getOptionValue("html"));
        } else {

            System.out.printf("%7s%7s%7s%7s%7s%10s%7s%7s%7s%7s\n", "Id", "Type", "Cost", "Att", "Def", "Keywords", "MyHP", "OppHP", "Draw", "Area");
            System.out.println("============================================================================");
            for (Card c : cardset.values())
                System.out.println(c.toPrettyStringWithoutId("%7s%7s%7s%7s%7s%10s%7s%7s%7s%7s"));
        }
        return false;
    }

    static boolean handlePlay(CommandLine cmd) throws IOException, NoSuchFieldException, IllegalAccessException {
        if (cmd.hasOption("help"))
            return true;

        MultiplayerGameRunner runner = new MultiplayerGameRunner();

        if (cmd.hasOption("d")) {
            Properties properties = new Properties();
            properties.load(new StringReader(cmd.getOptionValue("d").replaceAll(" ", "\n")));
            runner.setGameParameters(properties);
        }

        runner.addAgent(cmd.getOptionValue("p1"));
        runner.addAgent(cmd.getOptionValue("p2"));

        try {
            if (cmd.hasOption("s")) {
                runner.start();
            } else {
                Constants.HANDLE_UI = false;

                GameResult gameResult = runner.simulate();

                if (cmd.hasOption("l")) {
                    Files.asCharSink(Paths.get(cmd.getOptionValue("l")).toFile(), Charset.defaultCharset())
                            .write((String) new Gson().toJson(gameResult));
                }

                System.out.println(gameResult.scores.get(0));
                System.out.println(gameResult.scores.get(1));

                for (String line : gameResult.gameParameters) {
                    System.out.println(line);
                }
            }
        } finally {
            Field getPlayers = GameRunner.class.getDeclaredField("players");
            Field getProcess = CommandLinePlayerAgent.class.getDeclaredField("process");

            getPlayers.setAccessible(true);
            getProcess.setAccessible(true);

            List<Agent> players = (List<Agent>) getPlayers.get(runner);
            for (Agent player : players) {
                Process process = (Process) getProcess.get(player);
                process.destroy();
            }
        }
        return false;
    }
}

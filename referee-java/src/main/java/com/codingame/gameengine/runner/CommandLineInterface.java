package com.codingame.gameengine.runner;

import java.io.StringReader;
import java.lang.reflect.Field;
import java.nio.charset.Charset;
import java.nio.file.Paths;
import java.util.List;
import java.util.Properties;

import com.codingame.gameengine.runner.simulate.GameResult;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;

import com.codingame.game.engine.Constants;
import com.google.common.io.Files;
import com.google.gson.Gson;

public class CommandLineInterface {
  public static void main(String[] args) {
    try {
      Options options = new Options();
      options
        .addOption("d", true, "Referee initial data")
        .addOption("h", false, "Print the help")
        .addOption("l", true, "File output for logs")
        .addOption("p1", true, "Required. Player 1 command line.")
        .addOption("p2", true, "Required. Player 2 command line.")
        .addOption("s", false, "Server mode");

      CommandLine cmd = new DefaultParser().parse(options, args);
      if (cmd.hasOption("h") || !cmd.hasOption("p1") || !cmd.hasOption("p2")) {
        new HelpFormatter().printHelp(
          "-p1 <player1 command line> -p2 <player2 command line> [-s -l <File output for logs>]",
          options
        );
        System.exit(0);
      }

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
    } catch (Exception e) {
      System.err.println(e);
      e.printStackTrace(System.err);
      System.exit(1);
    }
  }
}

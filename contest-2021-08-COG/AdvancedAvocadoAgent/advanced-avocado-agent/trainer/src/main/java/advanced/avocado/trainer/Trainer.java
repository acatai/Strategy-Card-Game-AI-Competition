package advanced.avocado.trainer;

import java.io.File;
import java.io.FileReader;
import java.io.IOException;

import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;

import advanced.avocado.agent.Rating;

public class Trainer
{

  public static final int TRAINING_ITERATIONS = 1000;

  private String refereePath;

  private String agentPath;

  private Tree[] agentTrees;

  private Node[] currentNodes;

  /**
   * The main entrypoint for the training functionality.
   * 
   * @param args Execution arguments. `args[0]` should represent the path to the LoCM referee jar file. `args[1]` should
   *          represent the path to the agent jar file.
   */
  public static void main( String[] args )
  {
    Trainer trainer = new Trainer( args[0], args[1] );

    File logFolder = new File( "logs" );
    logFolder.mkdirs();

    trainer.agentTrees[0] = new Tree( Math.sqrt( 2.0 ) );
    trainer.agentTrees[1] = new Tree( Math.sqrt( 2.0 ) );
    trainer.agentTrees[2] = new Tree( Math.sqrt( 2.0 ) );

    trainer.currentNodes[0] = trainer.agentTrees[0].getNextNodeToExplore();
    trainer.currentNodes[1] = trainer.agentTrees[1].getNextNodeToExplore();
    trainer.currentNodes[2] = trainer.agentTrees[2].getNextNodeToExplore();

    Rating[] currentRatings = { trainer.currentNodes[0].getCurrentState(), trainer.currentNodes[1].getCurrentState(),
      trainer.currentNodes[2].getCurrentState() };

    try
    {
      for ( int i = 0; i < TRAINING_ITERATIONS; i++ )
      {
        System.out.println();
        System.out.println( "Iteration number: " + ( i + 1 ) );

        // Agent 1 vs Agent2
        trainer.currentNodes[0] = trainer.agentTrees[0].getNextNodeToExplore();
        currentRatings[0] = trainer.currentNodes[0].getCurrentState();

        trainer.currentNodes[1] = trainer.agentTrees[1].getNextNodeToExplore();
        currentRatings[1] = trainer.currentNodes[1].getCurrentState();

        trainer.runTraining( trainer.ratingToArguments( currentRatings[0] ),
                             trainer.ratingToArguments( currentRatings[1] ), trainer.currentNodes[0],
                             trainer.currentNodes[1] );

        // Agent2 vs Agent3
        trainer.currentNodes[1] = trainer.agentTrees[1].getNextNodeToExplore();
        currentRatings[1] = trainer.currentNodes[1].getCurrentState();

        trainer.currentNodes[2] = trainer.agentTrees[2].getNextNodeToExplore();
        currentRatings[2] = trainer.currentNodes[2].getCurrentState();

        trainer.runTraining( trainer.ratingToArguments( currentRatings[1] ),
                             trainer.ratingToArguments( currentRatings[2] ), trainer.currentNodes[1],
                             trainer.currentNodes[2] );

        // Agent1 vs Agent3
        trainer.currentNodes[0] = trainer.agentTrees[0].getNextNodeToExplore();
        currentRatings[0] = trainer.currentNodes[0].getCurrentState();

        trainer.currentNodes[2] = trainer.agentTrees[2].getNextNodeToExplore();
        currentRatings[2] = trainer.currentNodes[2].getCurrentState();

        trainer.runTraining( trainer.ratingToArguments( currentRatings[0] ),
                             trainer.ratingToArguments( currentRatings[2] ), trainer.currentNodes[0],
                             trainer.currentNodes[2] );
      }

      trainer.currentNodes[0] = trainer.agentTrees[0].getNextNodeToExplore();
      trainer.currentNodes[0].logPath();

      trainer.currentNodes[1] = trainer.agentTrees[1].getNextNodeToExplore();
      trainer.currentNodes[1].logPath();

      trainer.currentNodes[2] = trainer.agentTrees[2].getNextNodeToExplore();
      trainer.currentNodes[2].logPath();
    }
    catch ( IOException | InterruptedException e )
    {
      e.printStackTrace();
    }
  }

  /**
   * Creates a trainer object.
   * 
   * @param refereePath The path to the LoCM referee jar file.
   * @param agentPath The path to the agent jar file.
   */
  public Trainer( String refereePath, String agentPath )
  {
    this.refereePath = refereePath;
    this.agentPath = agentPath;

    this.agentTrees = new Tree[3];
    this.currentNodes = new Node[3];
  }

  /**
   * Runs one episode of training for the two specified agents.
   * 
   * @param agent1Args Arguments that should be passed to the first agent.
   * @param agent2Args Arguments that should be passed to the second agent.
   * @param player1 Current Node of the first agent.
   * @param player2 Current Node of the second agent.
   * @throws IOException Thrown if the built command could not be found or executed.
   * @throws InterruptedException Thrown an error occured while waiting for the executed process to finish.
   */
  public void runTraining( String agent1Args, String agent2Args, Node player1, Node player2 )
    throws IOException, InterruptedException
  {
    System.out.println( this.buildCommand( agent1Args, agent2Args ) );
    Runtime run = Runtime.getRuntime();
    Process pr = run.exec( this.buildCommand( agent1Args, agent2Args ) );
    int code = pr.waitFor();

    if ( code == 0 )
    {
      JSONParser parser = new JSONParser();
      try
      {
        JSONObject trainingData = (JSONObject) parser.parse( new FileReader( "logs/trainer-log.json" ) );
        JSONObject scores = (JSONObject) trainingData.get( "scores" );
        Long player1Score = (Long) scores.get( "0" );
        Long player2Score = (Long) scores.get( "1" );

        if ( player1Score == 1 )
        {
          player1.addWin();
          player2.addLoss();
          System.out.println( "Player 1 won!" );
        }
        else if ( player2Score == 1 )
        {
          player2.addWin();
          player1.addLoss();
          System.out.println( "Player 2 won!" );
        }
        else
        {
          System.out.println( "Draw? Player 1: " + player1Score + " Player 2: " + player2Score );
        }
      }
      catch ( Exception e )
      {
        e.printStackTrace();
      }
    }
  }

  /**
   * Builds the command used to start a single game simulation.
   * 
   * @param agent1Args Arguments that should be passed to the first agent.
   * @param agent2ArgsArguments that should be passed to the second agent.
   * @return Returns the built command as a string.
   */
  private String buildCommand( String agent1Args, String agent2Args )
  {
    String cmd = "java -jar " + this.refereePath + " -p1 \"" + this.buildAgentCommand( agent1Args ) + "\" -p2 \""
      + this.buildAgentCommand( agent2Args ) + "\" -l .\\logs\\trainer-log.json";

    return cmd;
  }

  /**
   * Builds the command to start a single agent instance.
   * 
   * @param agentArgs Arguments that should be passed to the agent.
   * @return Returns the built command as a string.
   */
  private String buildAgentCommand( String agentArgs )
  {
    return "java -jar " + this.agentPath + " " + agentArgs;
  }

  /**
   * Converts the rating to a string of arguments suitable for the usage in the {@link #buildCommand(String, String)}
   * and {@link #buildAgentCommand(String)} functions.
   * 
   * @param rating The rating that should be converted.
   * @return Returns an arguments string based on the supplied rating.
   */
  public String ratingToArguments( Rating rating )
  {
    String args = "";

    for ( double value : rating.allValues )
    {
      args = args + value + " ";
    }

    return args.substring( 0, args.length() - 1 );
  }

  public String getRefereePath()
  {
    return this.refereePath;
  }

  public void setRefereePath( String refereePath )
  {
    this.refereePath = refereePath;
  }

  public String getAgentPath()
  {
    return this.agentPath;
  }

  public void setAgentPath( String agentPath )
  {
    this.agentPath = agentPath;
  }
}

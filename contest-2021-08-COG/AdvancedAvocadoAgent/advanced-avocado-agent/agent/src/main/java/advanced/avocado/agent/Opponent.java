package advanced.avocado.agent;

import java.util.Scanner;

public class Opponent
    extends BasePlayer
{
    private int handSize;

    private int actionAmount;

    private Action[] lastActions;

    /**
     * empty constructor
     */
    public Opponent()
    {
        super();
    }

    /**
     * Reads additional data for opponents
     */
    @Override
    public void getRoundData( Scanner in )
    {
        super.getRoundData( in );
        this.handSize = in.nextInt();
        this.actionAmount = in.nextInt();
    }

    /**
     * Used to save the last actions
     * 
     * @param in Scanner from which to use data
     */
    public void parseLastActions( Scanner in )
    {
        this.lastActions = new Action[this.actionAmount];

        for ( int i = 0; i < this.actionAmount; i++ )
        {
            this.lastActions[i] = new Action( in );
        }
    }

    public int getHandSize()
    {
        return this.handSize;
    }

    public int getActionAmount()
    {
        return this.actionAmount;
    }
}

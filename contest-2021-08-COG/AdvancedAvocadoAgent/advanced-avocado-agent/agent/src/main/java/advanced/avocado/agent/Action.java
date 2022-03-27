package advanced.avocado.agent;

import java.util.Scanner;

enum ActionType
{
    SUMMON, ATTACK, USE, PASS
}

public class Action
{
    private ActionType actionType;

    private int playedCard;

    private int target;

    private int playedCardNumber;

    /**
     * constructor which takes data from a scanner input
     * 
     * @param in Scanner used to initialize the action
     */
    public Action( Scanner in )
    {
        this.parseActionData( in );
    }

    /**
     * constructor which takes data from the arguments
     * 
     * @param actionType type of the action
     * @param playedCard card which is played
     * @param target target of the action
     */
    public Action( ActionType actionType, int playedCard, int target )
    {
        this.actionType = actionType;
        this.playedCard = playedCard;
        this.target = target;
    }

    /**
     * parses Action from the input
     * 
     * @param in Scanner whichs input will be used
     */
    public void parseActionData( Scanner in )
    {
        String cardNumberAndAction = in.nextLine();
        String[] action = cardNumberAndAction.split( " " );

        this.playedCardNumber = Integer.parseInt( action[0] );

        if ( action[1] == "PASS" )
        {
            this.actionType = ActionType.PASS;
        }
        else
        {
            if ( action[1] == "SUMMON" )
            {
                this.actionType = ActionType.SUMMON;
            }
            else if ( action[1] == "ATTACK" )
            {
                this.actionType = ActionType.ATTACK;
            }
            else if ( action[1] == "USE" )
            {
                this.actionType = ActionType.USE;
            }

            this.playedCard = Integer.parseInt( action[2] );
            this.target = Integer.parseInt( action[3] );
        }
    }

    public ActionType getActionType()
    {
        return this.actionType;
    }

    public void setActionType( ActionType actionType )
    {
        this.actionType = actionType;
    }

    public int getPlayedCard()
    {
        return this.playedCard;
    }

    public void setPlayedCard( int playedCard )
    {
        this.playedCard = playedCard;
    }

    public int getTarget()
    {
        return this.target;
    }

    public void setTarget( int target )
    {
        this.target = target;
    }

    public String toString()
    {
        switch ( actionType )
        {
            case SUMMON:
                return "SUMMON " + playedCard + " " + target;

            case USE:
                return "USE " + playedCard + " " + target;

            case ATTACK:
                return "ATTACK " + playedCard + " " + target;

            case PASS:
                return "PASS";

            default:
                return "PASS";
        }
    }

    public int getPlayedCardNumber()
    {
        return this.playedCardNumber;
    }

    public void setPlayedCardNumber( int playedCardNumber )
    {
        this.playedCardNumber = playedCardNumber;
    }

}

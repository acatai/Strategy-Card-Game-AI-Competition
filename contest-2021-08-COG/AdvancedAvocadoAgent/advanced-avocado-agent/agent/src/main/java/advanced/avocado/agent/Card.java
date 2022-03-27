package advanced.avocado.agent;

import java.util.Scanner;

public class Card
{
    boolean canAttack;

    int cardNumber;

    int instanceId;

    int location;

    int cardType;

    int cost;

    int attack;

    int defense;

    String abilities;

    int myHealthChange;

    int opponentHealthChange;

    int cardDraw;

    int lane;

    /**
     * standard constructor which uses an inout to initalize all values
     * 
     * @param in Scanner which input is used
     */
    public Card( Scanner in )
    {
        this.cardNumber = in.nextInt();
        this.instanceId = in.nextInt();
        this.location = in.nextInt();
        this.cardType = in.nextInt();
        this.cost = in.nextInt();
        this.attack = in.nextInt();
        this.defense = in.nextInt();
        this.abilities = in.next();
        this.myHealthChange = in.nextInt();
        this.opponentHealthChange = in.nextInt();
        this.cardDraw = in.nextInt();
        this.lane = in.nextInt();

        if ( this.cardType == 0 && location != 0 && ( abilities.contains( "C" ) == false ) )
        {
            canAttack = true;
        }
        else
        {
            canAttack = false;
        }
    }
}

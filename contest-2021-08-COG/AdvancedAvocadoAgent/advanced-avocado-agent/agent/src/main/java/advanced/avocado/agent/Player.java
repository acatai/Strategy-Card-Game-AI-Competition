package advanced.avocado.agent;

import java.util.ArrayList;

public class Player
    extends BasePlayer
{

    private ArrayList<Card> cards;

    /**
     * empty constructor
     */
    public Player()
    {
        super();
    }

    public void setCards( ArrayList<Card> cards )
    {
        this.cards = cards;
    }

    public ArrayList<Card> getCards()
    {
        return this.cards;
    }
}

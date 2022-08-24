package advanced.avocado.agent;

import java.util.ArrayList;
import java.util.Scanner;

public abstract class BasePlayer
{
	private int health;

	private int mana;

	private int deckSize;

	private int rune;

	private int additionalDraw;

	private ArrayList<Card> laneCreatures;

	/**
	 * Empty constructor
	 */
	public BasePlayer()
	{

	}

	/**
	 * Reads data from the input and saves it
	 * 
	 * @param in scanner whichs input to use
	 */
	public void getRoundData( Scanner in )
	{
		this.health = in.nextInt();
		this.mana = in.nextInt();
		this.deckSize = in.nextInt();
		this.rune = in.nextInt();
		this.setAdditionalDraw( in.nextInt() );
	}

	public int getHealth()
	{
		return health;
	}

	public void setHealth( int health )
	{
		this.health = health;
	}

	public int getDeckSize()
	{
		return deckSize;
	}

	public void setDeckSize( int deckSize )
	{
		this.deckSize = deckSize;
	}

	public int getRune()
	{
		return rune;
	}

	public void setRune( int rune )
	{
		this.rune = rune;
	}

	public void setMana( int mana )
	{
		this.mana = mana;
	}

	public int getMana()
	{
		return this.mana;
	}

	public int getAdditionalDraw()
	{
		return additionalDraw;
	}

	public void setAdditionalDraw( int additionalDraw )
	{
		this.additionalDraw = additionalDraw;
	}

	public void setLaneCreatures( ArrayList<Card> laneCreatures )
	{
		this.laneCreatures = laneCreatures;
	}

	public ArrayList<Card> getLaneCreatures()
	{
		return this.laneCreatures;
	}

}

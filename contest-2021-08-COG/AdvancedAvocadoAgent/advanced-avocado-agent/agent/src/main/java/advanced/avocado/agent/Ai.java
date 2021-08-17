package advanced.avocado.agent;

import java.util.ArrayList;
import java.util.Scanner;

public class Ai
{
	private Scanner in;

	private Player player;

	private Opponent opponent;

	private Rating rater;

	/**
	 * The Main function of the agent. If the arguments for this function are empty, all factors will be initialized with
	 * 1.
	 * 
	 * @param args The factors given by the MCTS
	 */
	public static void main( String args[] )
	{
		Rating ratingThing;
		if ( args.length > 0 )
		{
			ratingThing = new Rating( args );
		}
		else
		{
			ratingThing = new Rating();
		}
		Ai agent = new Ai( ratingThing );
		agent.play();
	}

	/**
	 * Constructor for the Ai class. Initalizes the Scanner, Player, Opponent and rater.
	 * 
	 * @param rater The Rating system used to evaluate the state of the game
	 */
	public Ai( Rating rater )
	{
		in = new Scanner( System.in );
		player = new Player();
		opponent = new Opponent();
		this.rater = rater;
	}

	/**
	 * Starts the game. Now the input will be read, the according Actions will be choosen and printed. This will be
	 * repeated until the game is finished.
	 */
	public void play()
	{
		while ( true )
		{

			player.getRoundData( in );
			opponent.getRoundData( in );

			if ( in.hasNextLine() )
			{
				in.nextLine();
			}

			opponent.parseLastActions( in );

			parseCardData( in );

			// Setup complete
			// Let's hope we don't die

			if ( player.getMana() == 0 )
			{
				draftCard();
			}
			else
			{
				String actionCode = "";

				while ( true )
				{
					ArrayList<Card> currentCards = player.getCards();
					BestAction bestAction = new BestAction();

					bestAction = getBestAction( currentCards, bestAction );

					if ( bestAction.action != null )
					{
						simulateAction( currentCards, bestAction.action );
					}
					else
					{
						break;
					}

					actionCode = actionCode + bestAction.action.toString() + ";";
				}

				while ( true )
				{
					Action bestAttack = getBestAttack();
					if ( bestAttack == null )
					{
						break;
					}

					actionCode = actionCode + bestAttack.toString() + ";";
					executeAttack( bestAttack );
				}

				if ( actionCode.length() == 0 )
				{
					System.out.println( "PASS" );
				}
				else
				{
					System.out.println( actionCode.substring( 0, actionCode.length() - 1 ) );
				}
			}
		}
	}

	/**
	 * This function evaluates every possible Attack, using the rating. Once all Actions have been evaluated, it will
	 * return the best one
	 * 
	 * @return The best Attack possible
	 */
	public Action getBestAttack()
	{
		double bestValue = -Double.MAX_VALUE;
		double difference = -Double.MAX_VALUE;
		Action bestAction = null;

		boolean hasGuardCreatures = false;

		for ( Card opponentCreature : opponent.getLaneCreatures() )
		{
			hasGuardCreatures = hasGuardCreatures || opponentCreature.abilities.contains( "G" );
		}

		for ( Card playerCreature : player.getLaneCreatures() )
		{
			if ( playerCreature.canAttack == false )
			{
				continue;
			}

			for ( Card opponentCreature : opponent.getLaneCreatures() )
			{

				if ( hasGuardCreatures && !opponentCreature.abilities.contains( "G" ) )
				{
					continue;
				}

				// Check attacking each enemy creature
				if ( playerCreature.lane == opponentCreature.lane )
				{

					int opponentCreaturehealthDiff = playerCreature.attack;
					int opponentCreatureattackDiff = 0;
					int playerCreaturehealthDiff = opponentCreature.attack;
					int playerCreatureattackDiff = 0;

					if ( playerCreature.attack >= opponentCreature.defense || playerCreature.abilities.contains( "L" ) )
					{
						opponentCreaturehealthDiff = opponentCreature.defense;
						opponentCreatureattackDiff = opponentCreature.attack;
					}
					if ( opponentCreature.attack >= playerCreature.defense || opponentCreature.abilities.contains( "L" ) )
					{
						playerCreaturehealthDiff = playerCreature.defense;
						playerCreaturehealthDiff = playerCreature.attack;
					}
					if ( playerCreature.lane == 0 )
					{
						difference = -opponentCreatureattackDiff * rater.opponentLane1CreatureAtk
							- opponentCreaturehealthDiff * rater.opponentLane1CreatureHp
							- playerCreatureattackDiff * rater.playerLane1CreatureAtk
							+ playerCreaturehealthDiff * rater.playerLane1CreatureHp;
					}
					else if ( playerCreature.lane == 1 )
					{
						difference = -opponentCreatureattackDiff * rater.opponentLane2CreatureAtk
							- opponentCreaturehealthDiff * rater.opponentLane2CreatureHp
							- playerCreatureattackDiff * rater.playerLane2CreatureAtk
							+ playerCreaturehealthDiff * rater.playerLane2CreatureHp;
					}

					if ( difference > bestValue )
					{
						bestValue = difference;
						bestAction = new Action( ActionType.ATTACK, playerCreature.instanceId, opponentCreature.instanceId );
					}
				}
			}

			// Check going face
			if ( !hasGuardCreatures )
			{
				difference = -rater.opponentHp * playerCreature.attack;
				if ( difference > bestValue )
				{
					bestValue = difference;
					bestAction = new Action( ActionType.ATTACK, playerCreature.instanceId, -1 );
				}
			}
		}

		return bestAction;
	}

	/**
	 * Simulates an attack by altering all invovled parts of the game. This can NOT be undone.
	 * 
	 * @param attack The attack which should be simulated
	 */
	public void executeAttack( Action attack )
	{
		Card attackingCreature = null;
		Card defendingCreature = null;
		ArrayList<Card> playerCreatures = player.getLaneCreatures();
		ArrayList<Card> opponentCreatures = opponent.getLaneCreatures();
		int attackingIndex = 0;
		int defenseIndex = 0;

		for ( int i = 0; i < playerCreatures.size(); i++ )
		{
			if ( playerCreatures.get( i ).instanceId == attack.getPlayedCard() )
			{
				attackingIndex = i;
				attackingCreature = playerCreatures.get( i );
				attackingCreature.canAttack = false;
				break;
			}
		}

		if ( attack.getTarget() == -1 )
		{
			opponent.setHealth( opponent.getHealth() - attackingCreature.attack );
			return;
		}

		for ( int i = 0; i < opponentCreatures.size(); i++ )
		{
			if ( opponentCreatures.get( i ).instanceId == attack.getTarget() )
			{
				defenseIndex = i;
				defendingCreature = opponentCreatures.get( i );
				break;
			}
		}

		attackingCreature.defense = defendingCreature.attack;
		defendingCreature.defense = attackingCreature.attack;

		if ( attackingCreature.defense <= 0 || defendingCreature.abilities.contains( "L" ) )
		{
			playerCreatures.remove( attackingIndex );
		}
		else
		{
			attackingCreature.canAttack = false;
			playerCreatures.set( attackingIndex, attackingCreature );
		}
		player.setLaneCreatures( playerCreatures );

		if ( defendingCreature.defense <= 0 || attackingCreature.abilities.contains( "L" ) )
		{
			opponentCreatures.remove( defenseIndex );
		}
		else
		{
			opponentCreatures.set( defenseIndex, defendingCreature );
		}
		opponent.setLaneCreatures( opponentCreatures );
	}

	/**
	 * Reads the input and calls all functions, so that the current state of the game is represented by the programm.
	 * 
	 * @param in Scanner from which the function will get the input
	 */
	public void parseCardData( Scanner in )
	{
		int cardCount = in.nextInt();
		ArrayList<Card> handCards = new ArrayList<Card>();
		ArrayList<Card> playerLaneCards = new ArrayList<Card>();
		ArrayList<Card> opponentLaneCards = new ArrayList<Card>();

		for ( int i = 0; i < cardCount; i++ )
		{
			Card card = new Card( in );
			if ( card.location == 0 )
			{
				handCards.add( card );
			}
			else if ( card.location == 1 )
			{
				playerLaneCards.add( card );
			}
			else if ( card.location == -1 )
			{
				opponentLaneCards.add( card );
			}
		}

		player.setLaneCreatures( playerLaneCards );
		opponent.setLaneCreatures( opponentLaneCards );
		player.setCards( handCards );
	}

	/**
	 * Chooses a card out of the 3 offered.
	 */
	public void draftCard()
	{
		System.err.println( player.getCards().get( 0 ).cardNumber );
		System.err.println( player.getCards().get( 1 ).cardNumber );
		System.err.println( player.getCards().get( 2 ).cardNumber );
		for ( int cardType : Rating.draftOrder )
		{
			// System.err.println(cardType);
			for ( int i = 0; i < 3; i++ )
			{
				if ( cardType == player.getCards().get( i ).cardNumber )
				{
					System.out.println( "PICK " + i );
					return;
				}
			}
		}
		System.out.println( "PICK " + (int) ( Math.random() * 3 ) );
	}

	/**
	 * This method is used to find the best Action avaiable, from both the given cards, as well as the Action parsed. The
	 * parsed Action allows to compare the Action with the Actions viable through the given Cards
	 * 
	 * @param currentCards All cards that are in the Hand and avaiable for playing
	 * @param bestAction The currentl best Action
	 * @return The best Action possible
	 */
	public BestAction getBestAction( ArrayList<Card> currentCards, BestAction bestAction )
	{
		for ( Card card : currentCards )
		{
			if ( card.cost <= player.getMana() )
			{
				if ( card.cardType == 0 )
				{
					bestAction = summonCardAction( card, bestAction );
				}
				else if ( card.cardType == 1 || card.cardType == 2 || card.cardType == 3 )
				{
					bestAction = useCardAction( card, bestAction );
				}
			}

		}

		return bestAction;
	}

	/**
	 * This method i used, to compare the summoning of a creature to a given action
	 * 
	 * @param card The creature to be summoned
	 * @param bestAction An Action to be compared with
	 * @return The best Action possible
	 */
	public BestAction summonCardAction( Card card, BestAction bestAction )
	{
		if ( card.cardType == 0 )
		{

			ArrayList<Card> laneCreatures = this.player.getLaneCreatures();
			int lane1Count = 0;
			int lane2Count = 0;

			for ( Card creature : laneCreatures )
			{
				if ( creature.lane == 0 )
				{
					lane1Count++;
				}
				else if ( creature.lane == 1 )
				{
					lane2Count++;
				}
			}

			double difference = rater.playerLane1CreatureAtk * card.attack + rater.playerLane1CreatureHp * card.defense
				- rater.playerMana * card.cost - rater.playerHandSize;

			if ( difference > bestAction.value && lane1Count < 3 )
			{
				bestAction.value = difference;
				bestAction.action = new Action( ActionType.SUMMON, card.instanceId, 0 );
			}

			difference = rater.playerLane2CreatureAtk * card.attack + rater.playerLane2CreatureHp * card.defense
				- rater.playerMana * card.cost - rater.playerHandSize;

			if ( difference > bestAction.value && lane2Count < 3 )
			{
				bestAction.value = difference;
				bestAction.action = new Action( ActionType.SUMMON, card.instanceId, 1 );
			}
		}

		return bestAction;
	}

	/**
	 * This Method allows the comparison of summoning a card to a given action
	 * 
	 * @param card The Card to be used
	 * @param bestAction The Action to be compared with
	 * @return The best Action possible
	 */
	public BestAction useCardAction( Card card, BestAction bestAction )
	{
		double difference1 = -rater.playerMana * card.cost - rater.playerHandSize;
		double difference2 = -rater.playerMana * card.cost - rater.playerHandSize;

		if ( card.cardType == 1 )
		{
			difference1 =
				difference1 + rater.playerLane1CreatureAtk * card.attack + rater.playerLane1CreatureHp * card.defense;
			difference2 =
				difference2 + rater.playerLane2CreatureAtk * card.attack + rater.playerLane2CreatureHp * card.defense;
		}
		else if ( card.cardType == 2 )
		{
			difference1 =
				difference1 + rater.opponentLane1CreatureAtk * card.attack + rater.opponentLane1CreatureHp * card.defense;
			difference2 =
				difference2 + rater.opponentLane2CreatureAtk * card.attack + rater.opponentLane2CreatureHp * card.defense;
		}
		else if ( card.cardType == 3 )
		{
			double difference =
				rater.playerHp * card.myHealthChange - rater.opponentHp * ( card.opponentHealthChange + card.defense )
					- rater.opponentHandSize + rater.playerCardDraw * card.cardDraw - rater.playerMana * card.cost;

			if ( difference > bestAction.value )
			{
				bestAction.value = difference;
				bestAction.action = new Action( ActionType.USE, card.instanceId, -1 );
			}

			difference1 = difference1 + rater.opponentLane1CreatureHp * card.defense + rater.playerHp * card.myHealthChange
				- rater.opponentHp * card.opponentHealthChange;
			difference2 = difference2 + rater.opponentLane2CreatureHp * card.defense + rater.playerHp * card.myHealthChange
				- rater.opponentHp * card.opponentHealthChange;
		}

		int bestLane = 0;
		double difference = difference1;

		if ( difference2 > difference1 )
		{
			bestLane = 1;
			difference = difference2;
		}

		if ( difference > bestAction.value )
		{
			ArrayList<Card> targets = card.cardType == 1 ? player.getLaneCreatures() : opponent.getLaneCreatures();
			Card strongest = null;

			for ( int i = 1; i < targets.size(); i++ )
			{
				Card target = targets.get( i );

				boolean isStrongest = false;

				if ( card.cardType == 3 )
				{
					isStrongest = target.lane == bestLane
						&& ( strongest == null || ( target.attack + target.defense > strongest.attack + strongest.defense )
							&& target.defense <= card.defense );
				}
				else
				{
					isStrongest = target.lane == bestLane
						&& ( strongest == null || target.attack + target.defense > strongest.attack + strongest.defense );
				}

				if ( isStrongest )
				{
					strongest = target;
				}
			}

			if ( strongest != null )
			{
				bestAction.value = difference;
				bestAction.action = new Action( ActionType.USE, card.instanceId, strongest.instanceId );
			}
		}

		return bestAction;
	}

	/**
	 * This method simulates an action by updating all data holding opponents. Note: this action can not be undone
	 * 
	 * @param currentCards the card currently in the players hand
	 * @param action The action to be performed
	 */
	public void simulateAction( ArrayList<Card> currentCards, Action action )
	{
		Card chosenCard = null;
		int chosenCardIndex = -1;

		for ( int i = 0; i < currentCards.size(); i++ )
		{
			Card card = currentCards.get( i );
			if ( card.instanceId == action.getPlayedCard() )
			{
				chosenCard = card;
				chosenCardIndex = i;
				break;
			}
		}

		if ( action.getActionType() == ActionType.SUMMON )
		{
			ArrayList<Card> playerLaneCreatures = player.getLaneCreatures();
			chosenCard.lane = action.getTarget();
			playerLaneCreatures.add( chosenCard );
			player.setLaneCreatures( playerLaneCreatures );
		}
		else if ( action.getActionType() == ActionType.USE )
		{
			simulateUseAction( action, chosenCard );
		}

		ArrayList<Card> playerCards = player.getCards();
		playerCards.remove( chosenCardIndex );
		player.setCards( playerCards );

		player.setMana( player.getMana() - chosenCard.cost );
	}

	/**
	 * This method simulates an use action by updating all data holding opponents. Note: this action can not be undone
	 * 
	 * @param action The action to be performed
	 * @param chosenCard The choosen Target for the action
	 */
	public void simulateUseAction( Action action, Card chosenCard )
	{
		player.setHealth( player.getHealth() + chosenCard.myHealthChange );
		player.setAdditionalDraw( player.getAdditionalDraw() + chosenCard.cardDraw );
		opponent.setHealth( opponent.getHealth() + chosenCard.opponentHealthChange );

		if ( action.getTarget() == -1 )
		{
			opponent.setHealth( opponent.getHealth() + chosenCard.defense );
		}
		else
		{
			Card targetCreature = null;
			int targetCreatureIndex = -1;
			ArrayList<Card> opponentLaneCreatures = opponent.getLaneCreatures();
			ArrayList<Card> playerLaneCreatures = player.getLaneCreatures();

			boolean isPlayerCreature = false;

			for ( int i = 0; i < opponentLaneCreatures.size(); i++ )
			{
				Card opponentCreature = opponentLaneCreatures.get( i );
				if ( opponentCreature.instanceId == action.getTarget() )
				{
					targetCreature = opponentCreature;
					targetCreatureIndex = i;
					break;
				}
			}

			if ( targetCreature == null )
			{
				for ( int i = 0; i < playerLaneCreatures.size(); i++ )
				{
					Card playerCreature = playerLaneCreatures.get( i );
					if ( playerCreature.instanceId == action.getTarget() )
					{
						targetCreature = playerCreature;
						targetCreatureIndex = i;
						isPlayerCreature = true;
						break;
					}
				}
			}

			targetCreature.attack += chosenCard.attack;
			targetCreature.defense += chosenCard.defense;

			if ( targetCreature.defense <= 0 )
			{
				if ( isPlayerCreature )
				{
					playerLaneCreatures.remove( targetCreatureIndex );
				}
				else
				{
					opponentLaneCreatures.remove( targetCreatureIndex );
				}
			}
			else
			{
				if ( isPlayerCreature )
				{
					playerLaneCreatures.set( targetCreatureIndex, targetCreature );
				}
				else
				{
					opponentLaneCreatures.set( targetCreatureIndex, targetCreature );
				}
			}

			player.setLaneCreatures( playerLaneCreatures );
			opponent.setLaneCreatures( opponentLaneCreatures );
		}
	}
}

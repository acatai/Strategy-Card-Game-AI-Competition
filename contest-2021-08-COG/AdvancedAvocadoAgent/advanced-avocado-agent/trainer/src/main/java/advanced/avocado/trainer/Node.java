package advanced.avocado.trainer;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;

import advanced.avocado.agent.Rating;

public class Node
{
	public static int idCounter = 0;

	private int treeId;

	private int id;

	private Node parent;

	private ArrayList<Node> childs;

	private int amountVisitations;

	private int amountWins;

	private Rating currentState;

	/**
	 * constructor without parent or state
	 * 
	 * @param treeId id of the tree
	 */
	public Node( int treeId )
	{
		this.parent = null;
		this.treeId = treeId;
		id = idCounter;
		idCounter++;
		this.amountVisitations = 0;
		this.amountWins = 0;
		currentState = new Rating();
		logState();
	}

	/**
	 * constructor with parent but without state
	 * 
	 * @param treeId id of the tree
	 * @param parent The parentnode of the node
	 */
	public Node( Node parent, int treeId )
	{
		this.parent = parent;
		this.treeId = treeId;
		id = idCounter;
		idCounter++;
		this.amountVisitations = 0;
		this.amountWins = 0;
		currentState = new Rating();
		logState();
	}

	/**
	 * constructor without parent but with state
	 * 
	 * @param treeId id of the tree
	 * @loadedState stateOfTheRating
	 */
	public Node( Rating loadedState, int treeId )
	{
		this.parent = null;
		this.treeId = treeId;
		id = idCounter;
		idCounter++;
		this.amountVisitations = 0;
		this.amountWins = 0;
		currentState = loadedState;
		logState();
	}

	/**
	 * constructor with parent and state
	 * 
	 * @param treeId id of the tree
	 * @param parent The parentnode of the node
	 * @loadedState stateOfTheRating
	 */
	public Node( Node parent, Rating loadedState, int treeId )
	{
		this.parent = parent;
		this.treeId = treeId;
		id = idCounter;
		idCounter++;
		this.amountVisitations = 0;
		this.amountWins = 0;
		currentState = loadedState;
		logState();
	}

	/**
	 * Increases amountWins and amountVisitations and calls this functions for the parentnode
	 */
	public void addWin()
	{
		amountVisitations++;
		amountWins++;

		if ( parent != null )
		{
			parent.addWin();
		}
	}

	/**
	 * Increases amountVisitations and calls this functions for the parentnode
	 */
	public void addLoss()
	{
		amountVisitations++;

		if ( parent != null )
		{
			parent.addLoss();
		}
	}

	/**
	 * logs all Data of the Node
	 */
	public void logState()
	{
		/*
		 * File logFile = new File(String.valueOf(treeId) + "\\" + String.valueOf(id) + ".txt"); FileWriter writer; try {
		 * writer = new FileWriter(logFile); writer.write("id: " + idCounter + "\n"); writer.write("wins: " + amountWins +
		 * "\n"); writer.write("visits: " + amountVisitations + "\n"); if(parent != null) { writer.write("parentId: " +
		 * String.valueOf(parent.getId()) + "\n"); } else { writer.write("No parent" + "\n"); } for (double value :
		 * currentState.allValues) { writer.write(String.valueOf(value) + "\n"); } writer.close(); } catch (IOException e) {
		 * e.printStackTrace(); }
		 */

	}

	/**
	 * logs all Data of the Nodes and calls this function for the parent
	 */
	public void logPath()
	{
		File logFile = new File( "logs\\" + String.valueOf( treeId ) + "\\" + String.valueOf( id ) + ".log" );
		logFile.getParentFile().mkdirs();
		FileWriter writer;
		try
		{
			writer = new FileWriter( logFile );
			writer.write( "id: " + id + "\n" );
			writer.write( "wins: " + amountWins + "\n" );
			writer.write( "visits: " + amountVisitations + "\n" );
			if ( parent != null )
			{
				writer.write( "parentId: " + String.valueOf( parent.getId() ) + "\n" );
			}
			else
			{
				writer.write( "No parent" + "\n" );
			}
			for ( double value : currentState.allValues )
			{
				writer.write( String.valueOf( value ) + "\n" );
			}
			writer.close();
		}
		catch ( IOException e )
		{
			e.printStackTrace();
		}

		if ( parent != null )
		{
			parent.logPath();
		}
	}

	public int getAmountVisitations()
	{
		return this.amountVisitations;
	}

	public int getAmountWins()
	{
		return this.amountWins;
	}

	public Node getParent()
	{
		return this.parent;
	}

	/**
	 * Returns all child notes. If there are no child nodes yet, all possible child notes will be created
	 * 
	 * @return all childs in an ArrayList
	 */
	public ArrayList<Node> getChilds()
	{
		if ( childs == null )
		{
			childs = new ArrayList<Node>();

			for ( int i = 10; i < currentState.allValues.length; i++ )
			{
				if ( currentState.allValues[i] == 1 )
				{
					currentState.allValues[i] = currentState.allValues[i] + 0.5;
					currentState.allValues[i - 10] = currentState.allValues[i - 10] - 0.5;
					Rating copy = new Rating( currentState.allValues );
					Node newChild = new Node( this, copy, treeId );
					childs.add( newChild );

					currentState.allValues[i] = currentState.allValues[i] - 1.0;
					currentState.allValues[i - 10] = currentState.allValues[i - 10] + 1.0;
					Rating anotherCopy = new Rating( currentState.allValues );
					Node anotherNewChild = new Node( this, anotherCopy, treeId );
					childs.add( anotherNewChild );

					currentState.allValues[i] = currentState.allValues[i] + 0.5;
					currentState.allValues[i - 10] = currentState.allValues[i - 10] - 0.5;

				}
				else if ( currentState.allValues[i] > 1 )
				{
					currentState.allValues[i] = currentState.allValues[i] + 0.5;
					currentState.allValues[i - 10] = currentState.allValues[i - 10] - 0.5;
					Rating copy = new Rating( currentState.allValues );
					Node newChild = new Node( this, copy, treeId );
					childs.add( newChild );
					currentState.allValues[i] = currentState.allValues[i] - 0.5;
					currentState.allValues[i - 10] = currentState.allValues[i - 10] + 0.5;
				}
				else if ( currentState.allValues[i] < 1 )
				{
					currentState.allValues[i] = currentState.allValues[i] - 0.5;
					currentState.allValues[i - 10] = currentState.allValues[i - 10] + 0.5;
					Rating copy = new Rating( currentState.allValues );
					Node newChild = new Node( this, copy, treeId );
					childs.add( newChild );
					currentState.allValues[i] = currentState.allValues[i] + 0.5;
					currentState.allValues[i - 10] = currentState.allValues[i - 10] - 0.5;
				}
			}
		}

		return childs;
	}

	public void setParent( Node parent )
	{
		this.parent = parent;
	}

	public void setChilds( ArrayList<Node> childs )
	{
		this.childs = childs;
	}

	public void setAmountVisitations( int amountVisitations )
	{
		this.amountVisitations = amountVisitations;
	}

	public void setAmountWins( int amountWins )
	{
		this.amountWins = amountWins;
	}

	public Rating getCurrentState()
	{
		return this.currentState;
	}

	public void setCurrentState( Rating currentState )
	{
		this.currentState = currentState;
	}

	public int getId()
	{
		return this.id;
	}

}

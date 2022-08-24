package advanced.avocado.trainer;

import java.io.File;

public class Tree
{
	public static int id = 0;

	private Node startNode;

	private double explorationParameter;

	/**
	 * default constructor. Creates a folder for the logs, as well as the start node.
	 * 
	 * @param explorationParameter decides how much the Tree should be explored
	 */
	public Tree( double explorationParameter )
	{
		File treeFolder = new File( "logs\\" + String.valueOf( id ) );
		treeFolder.mkdirs();
		this.explorationParameter = explorationParameter;
		startNode = new Node( id );
		id++;
	}

	/**
	 * uses the starting node to call getNextNodeToExplore
	 * 
	 * @return The Node that should be explored next
	 */
	public Node getNextNodeToExplore()
	{
		return this.getNextNodeToExplore( this.getStartNode() );
	}

	/**
	 * Recursive method. Determines which note under the given node should be explored next and calls this method with
	 * this node again. Stops if it hits a node which has not been explored yet.
	 * 
	 * @param nodeToExplore The node under which exploartion should be
	 * @return The node which should be explored next
	 */
	public Node getNextNodeToExplore( Node nodeToExplore )
	{
		if ( nodeToExplore.getAmountVisitations() == 0 )
		{
			return nodeToExplore;
		}

		Node nextNodeToExplore = null;
		double biggestFactor = -Double.MAX_VALUE;

		for ( Node node : nodeToExplore.getChilds() )
		{
			double factor;
			if ( node.getAmountVisitations() == 0 )
			{
				factor = explorationParameter * Math.sqrt( Math.log( node.getParent().getAmountVisitations() ) / 1 );

			}
			else
			{
				factor = (double) node.getAmountWins() / (double) node.getAmountVisitations() + explorationParameter
					* Math.sqrt( Math.log( node.getParent().getAmountVisitations() ) / (double) node.getAmountVisitations() );
			}

			if ( factor > biggestFactor )
			{
				biggestFactor = factor;
				nextNodeToExplore = node;
			}
		}

		return getNextNodeToExplore( nextNodeToExplore );
	}

	/**
	 * uses the starting node to call getBestNode
	 * 
	 * @return The node with the best winrate
	 */
	public Node getBestNode()
	{
		return this.getBestNode( this.getStartNode() );
	}

	/**
	 * Recursive method. Determines which note under the given node has the highest win ratio and calls this method with
	 * this node again. Stops if it hits a node which has not been explored yet.
	 * 
	 * @param nodeToExplore The node under which exploartion should be
	 * @return The node which should be explored next
	 */
	public Node getBestNode( Node nodeToExplore )
	{
		if ( nodeToExplore.getAmountVisitations() == 0 )
		{
			return nodeToExplore;
		}

		Node nextNodeToExplore = null;
		double biggestFactor = 0;

		for ( Node node : nodeToExplore.getChilds() )
		{
			if ( node.getAmountVisitations() == 0 )
			{
				break;
			}

			double factor = (double) node.getAmountWins() / (double) node.getAmountVisitations();

			if ( factor > biggestFactor )
			{
				biggestFactor = factor;
				nextNodeToExplore = node;
			}
		}

		if ( nextNodeToExplore == null )
		{
			return nodeToExplore;
		}

		return getBestNode( nextNodeToExplore );
	}

	public Node getStartNode()
	{
		return this.startNode;
	}
}

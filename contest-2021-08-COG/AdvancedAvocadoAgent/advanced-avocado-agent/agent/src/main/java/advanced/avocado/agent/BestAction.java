package advanced.avocado.agent;

public class BestAction
{
  public Action action;

  public double value;

  /**
   * standard constructor. Initalizes action with null and value with the smallest value possible.
   */
  public BestAction()
  {
    this.action = null;
    this.value = -Double.MAX_VALUE;
  }
}

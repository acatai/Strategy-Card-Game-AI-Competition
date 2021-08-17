import java.util.stream.Collectors;
import java.util.stream.Stream;

/** AI description
 * Draft phase:
 *  - always pick the first card
 * Game phase:
 *  - do nothing (outputs single ';')
 */
public class PlayerEmpty
{
  public static void main(String[] args)
  {
      System.out.println(Stream.generate(() -> "PASS").limit(30).collect(Collectors.joining(" ; ")));

    while (true)
      System.out.println(";");
  }
}

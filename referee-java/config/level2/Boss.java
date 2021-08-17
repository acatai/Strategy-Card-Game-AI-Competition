import java.util.stream.Collectors;
import java.util.stream.Stream;

/** AI description
 * Draft phase:
 *  - 30x choose default card
 * Game phase:
 *  - do nothing (outputs single ';')
 */
class Player
{
  public static void main(String[] args)
  {
    System.out.println(Stream.generate(() -> "PASS _").limit(30).collect(Collectors.joining(" ; "))+" lvl2");

    while (true)
      System.out.println(";");
  }
}

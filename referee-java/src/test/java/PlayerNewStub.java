import java.util.*;
import java.io.*;
import java.math.*;

/**
 * Auto-generated code below aims at helping you parse
 * the standard input according to the problem statement.
 **/
class Player {
    public static void main(String args[]) {
        Scanner in = new Scanner(System.in);

        // game loop
        while (true) {
            for (int i = 0; i < 2; i++) {
                int playerHealth = in.nextInt();
                int playerMana = in.nextInt();
                int playerDeck = in.nextInt();
                int playerDraw = in.nextInt();
            }
            int opponentHand = in.nextInt();
            int opponentActions = in.nextInt();
            if (in.hasNextLine()) {
                in.nextLine();
            }
            for (int i = 0; i < opponentActions; i++) {
                String cardNumberAndAction = in.nextLine();
            }
            int cardCount = in.nextInt();
            for (int i = 0; i < cardCount; i++) {
                int cardNumber = in.nextInt();
                int instanceId = in.nextInt();
                int location = in.nextInt();
                int cardType = in.nextInt();
                int cost = in.nextInt();
                int attack = in.nextInt();
                int defense = in.nextInt();
                String abilities = in.next();
                int myHealthChange = in.nextInt();
                int opponentHealthChange = in.nextInt();
                int cardDraw = in.nextInt();
//                int lane = in.nextInt();
            }

            // Write an action using System.out.println()
            // To debug: System.err.println("Debug messages...");

            System.out.println("PASS");
        }
    }
}
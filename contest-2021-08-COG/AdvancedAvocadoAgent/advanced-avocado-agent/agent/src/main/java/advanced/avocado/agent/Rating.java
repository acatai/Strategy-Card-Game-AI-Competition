package advanced.avocado.agent;

public class Rating
{
	// public static int[] draftOrder = {15, 17, 9, 5, 22, 1, 3, 7, 18, 19, 13, 6,
	// 12, 21, 8, 16, 14, 20, 11, 10, 4, 2};

	public static int[] draftOrder = { 48, 49, 51, 52, 15, 17, 69, 18, 68, 9, 70, 13, 53, 19, 109, 44, 75, 21, 105, 67,
		91, 39, 29, 7, 26, 106, 103, 25, 33, 73, 151, 30, 6, 32, 50, 54, 11, 10, 1, 5, 121, 148, 128, 129, 37, 22, 147, 150,
		31, 97, 99, 88, 98, 42, 93, 111, 112, 96, 95, 45, 12, 14, 43, 72, 56, 104, 66, 74, 8, 40, 47, 84, 28, 27, 65, 118,
		35, 152, 82, 36, 58, 76, 135, 23, 59, 62, 77, 41, 100, 16, 2, 130, 101, 102, 57, 92, 144, 141, 34, 114, 94, 4, 3,
		127, 46, 157, 122, 79, 38, 134, 154, 117, 119, 123, 158, 155, 115, 60, 153, 160, 89, 156, 113, 64, 85, 126, 124,
		131, 125, 108, 80, 159, 78, 145, 20, 146, 86, 71, 81, 61, 90, 63, 87, 55, 116, 136, 107, 110, 132, 133, 24, 83, 138,
		120, 139, 137, 149, 140, 142, 143 };

	public double[] allValues;

	public double opponentHp;

	public double opponentMana;

	public double opponentRunes;

	public double opponentDecksize;

	public double opponentCardDraw;

	public double opponentHandSize;

	public double opponentLane1CreatureHp;

	public double opponentLane1CreatureAtk;

	public double opponentLane2CreatureHp;

	public double opponentLane2CreatureAtk;

	public double playerHp;

	public double playerMana;

	public double playerRunes;

	public double playerDecksize;

	public double playerCardDraw;

	public double playerHandSize;

	public double playerLane1CreatureHp;

	public double playerLane1CreatureAtk;

	public double playerLane2CreatureHp;

	public double playerLane2CreatureAtk;

	/**
	 * constructor initalizes all data from an string array
	 * 
	 * @param multiplier list of multiplier
	 */
	public Rating( String[] multiplier )
	{
		playerHp = Double.parseDouble( multiplier[10] );
		playerMana = Double.parseDouble( multiplier[11] );
		playerRunes = Double.parseDouble( multiplier[12] );
		playerDecksize = Double.parseDouble( multiplier[13] );
		playerCardDraw = Double.parseDouble( multiplier[14] );
		playerHandSize = Double.parseDouble( multiplier[15] );
		playerLane1CreatureAtk = Double.parseDouble( multiplier[16] );
		playerLane1CreatureHp = Double.parseDouble( multiplier[17] );
		playerLane2CreatureAtk = Double.parseDouble( multiplier[18] );
		playerLane2CreatureHp = Double.parseDouble( multiplier[19] );

		opponentHp = -playerHp;
		opponentMana = -playerMana;
		opponentRunes = -playerRunes;
		opponentDecksize = -playerDecksize;
		opponentCardDraw = -playerCardDraw;
		opponentHandSize = -playerHandSize;
		opponentLane1CreatureAtk = -playerLane1CreatureAtk;
		opponentLane1CreatureHp = -playerLane1CreatureHp;
		opponentLane2CreatureAtk = -playerLane2CreatureAtk;
		opponentLane2CreatureHp = -playerLane2CreatureHp;

		double[] allValuesInit = { opponentHp, opponentMana, opponentRunes, opponentDecksize, opponentCardDraw,
			opponentHandSize, opponentLane1CreatureAtk, opponentLane1CreatureHp, opponentLane2CreatureAtk,
			opponentLane2CreatureHp, playerHp, playerMana, playerRunes, playerDecksize, playerCardDraw, playerHandSize,
			playerLane1CreatureAtk, playerLane1CreatureHp, playerLane2CreatureAtk, playerLane2CreatureHp };

		allValues = allValuesInit;
	}

	/**
	 * constructor initalizes all data from an double array
	 * 
	 * @param multiplier list of multiplier
	 */
	public Rating( double[] multiplier )
	{
		playerHp = ( (double) Math.round( multiplier[10] * 10 ) ) / 10.0;
		playerMana = ( (double) Math.round( multiplier[11] * 10 ) ) / 10.0;
		playerRunes = ( (double) Math.round( multiplier[12] * 10 ) ) / 10.0;
		playerDecksize = ( (double) Math.round( multiplier[13] * 10 ) ) / 10.0;
		playerCardDraw = ( (double) Math.round( multiplier[14] * 10 ) ) / 10.0;
		playerHandSize = ( (double) Math.round( multiplier[15] * 10 ) ) / 10.0;
		playerLane1CreatureAtk = ( (double) Math.round( multiplier[16] * 10 ) ) / 10.0;
		playerLane1CreatureHp = ( (double) Math.round( multiplier[17] * 10 ) ) / 10.0;
		playerLane2CreatureAtk = ( (double) Math.round( multiplier[18] * 10 ) ) / 10.0;
		playerLane2CreatureHp = ( (double) Math.round( multiplier[19] * 10 ) ) / 10.0;

		opponentHp = -playerHp;
		opponentMana = -playerMana;
		opponentRunes = -playerRunes;
		opponentDecksize = -playerDecksize;
		opponentCardDraw = -playerCardDraw;
		opponentHandSize = -playerHandSize;
		opponentLane1CreatureAtk = -playerLane1CreatureAtk;
		opponentLane1CreatureHp = -playerLane1CreatureHp;
		opponentLane2CreatureAtk = -playerLane2CreatureAtk;
		opponentLane2CreatureHp = -playerLane2CreatureHp;

		double[] allValuesInit = { opponentHp, opponentMana, opponentRunes, opponentDecksize, opponentCardDraw,
			opponentHandSize, opponentLane1CreatureAtk, opponentLane1CreatureHp, opponentLane2CreatureAtk,
			opponentLane2CreatureHp, playerHp, playerMana, playerRunes, playerDecksize, playerCardDraw, playerHandSize,
			playerLane1CreatureAtk, playerLane1CreatureHp, playerLane2CreatureAtk, playerLane2CreatureHp };

		allValues = allValuesInit;
	}

	/**
	 * default constructor
	 */
	public Rating()
	{
		playerHp = 3.5;
		playerMana = 0.5;
		playerRunes = 0.5;
		playerDecksize = 1.5;
		playerCardDraw = 1;
		playerHandSize = 0.5;
		playerLane1CreatureAtk = 1;
		playerLane1CreatureHp = 1;
		playerLane2CreatureAtk = 1;
		playerLane2CreatureHp = 1;

		opponentHp = -3.5;
		opponentMana = -0.5;
		opponentRunes = -0.5;
		opponentDecksize = -1.5;
		opponentCardDraw = -1;
		opponentHandSize = -0.5;
		opponentLane1CreatureAtk = -1;
		opponentLane1CreatureHp = -1;
		opponentLane2CreatureAtk = -1;
		opponentLane2CreatureHp = -1;

		double[] allValuesInit = { opponentHp, opponentMana, opponentRunes, opponentDecksize, opponentCardDraw,
			opponentHandSize, opponentLane1CreatureAtk, opponentLane1CreatureHp, opponentLane2CreatureAtk,
			opponentLane2CreatureHp, playerHp, playerMana, playerRunes, playerDecksize, playerCardDraw, playerHandSize,
			playerLane1CreatureAtk, playerLane1CreatureHp, playerLane2CreatureAtk, playerLane2CreatureHp };

		allValues = allValuesInit;
	}
}

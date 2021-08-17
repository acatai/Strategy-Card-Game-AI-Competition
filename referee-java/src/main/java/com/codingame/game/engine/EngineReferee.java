package com.codingame.game.engine;

import java.util.ArrayList;
import java.util.List;

import com.codingame.game.Player;
import com.codingame.game.engine.Action.Type;
import com.codingame.game.ui.ConstantsUI;
import com.codingame.game.ui.RefereeUI;
import com.codingame.gameengine.core.AbstractPlayer.TimeoutException;
import com.codingame.gameengine.core.MultiplayerGameManager;

public class EngineReferee {
    //private MultiplayerGameManager<Player> gameManager; // @Inject ?

    public ConstructPhase constr;
    public GameState state = null;

    public int gamePlayer = 0;
    public int gameTurn = 0;
    public int initGameTurn = 0;

    public List<Action> actionsToHandle = new ArrayList<>();

    private boolean showBattleStart = true;
    private boolean showDraftStart = true;
    public int showdraftSizechoice = 0;
    public int expectedConstructionFrames = 0;

    static final int ILLEGAL_ACTION_SUMMARY_LIMIT =3;

    public void refereeInit(MultiplayerGameManager<Player> gameManager) {
        if (Constants.VERBOSE_LEVEL > 1) System.out.println("New game");

        RefereeParams params = new RefereeParams(gameManager);

        ConstructPhase.Difficulty difficulty;
        switch (gameManager.getLeagueLevel()) {
            case 1:
                difficulty = ConstructPhase.Difficulty.VERY_EASY;
                break;
            case 2:
                difficulty = ConstructPhase.Difficulty.EASY;
                break;
            case 3:
                difficulty = ConstructPhase.Difficulty.LESS_EASY;
                break;
            default:
                difficulty = ConstructPhase.Difficulty.NORMAL;
                break;
        }

        if (Constants.LANES>1)
        {
            difficulty = ConstructPhase.Difficulty.NORMAL;
        }

        Constants.LoadCardlist("cardlist.txt");
        if (Constants.VERBOSE_LEVEL > 1) System.out.println("   CARDSET with " + Constants.CARDSET.size() + " cards loaded.");
        if (Constants.VERBOSE_LEVEL > 1) System.out.println("   Difficulty is set to: " + difficulty.name() + ".");

        constr = new ConstructPhase(difficulty, params);
        constr.PrepareConstructed();

        for (int i=0; i < ConstantsUI.SHOWDRAFT_SIZECHOICE.length; i++)
        {
            if (constr.cardsForConstruction.size() > ConstantsUI.SHOWDRAFT_SIZECHOICE[i])
              break;
            showdraftSizechoice = i;
        }
        //System.out.println(showdraftSizechoice);
        gameTurn = -1 - (int)Math.ceil(Math.max(0,(constr.cardsForConstruction.size() - ConstantsUI.SHOWDRAFT_ROWSIZE[showdraftSizechoice])) / (double)ConstantsUI.SHOWDRAFT_ROWSIZE[showdraftSizechoice]);
        initGameTurn = gameTurn;

        expectedConstructionFrames = (int) Math.ceil((double)Constants.CARDS_IN_CONSTRUCTED/Constants.MAX_CARDS_IN_FRAME);
        if (Constants.VERBOSE_LEVEL > 1) System.out.println("   Draw Phase Prepared. " + constr.allowedCards.size() + " cards allowed. ");
        if (Constants.VERBOSE_LEVEL > 1) System.out.println("   " + constr.cardsForConstruction.size() + " cards selected to the draft.");

        gameManager.setMaxTurns(Constants.MAX_TURNS_HARDLIMIT); // should be never reached, not handled on the referee's side
    }


    public boolean refereeGameTurn(MultiplayerGameManager<Player> gameManager, RefereeUI ui)
    {
        if (showDraftStart && gameTurn ==0) {
            showDraftStart = false;
            if (Constants.HANDLE_UI)
                gameManager.addTooltip(gameManager.getPlayer(0), "Draft phase.");
        }
        if (showBattleStart && gameTurn == expectedConstructionFrames) {
            showBattleStart = false;
            if (Constants.HANDLE_UI)
                gameManager.addTooltip(gameManager.getPlayer(0), "Battle phase.");
        }

        if (gameTurn < 0)
        {
            //System.out.format("    /// %d\n", gameTurn);
//            if (Constants.HANDLE_UI)
//                ui.showDraftCards(gameTurn, false);
            gameManager.getPlayer(0).expectedOutputLines = 0;
            gameManager.getPlayer(0).execute();
            gameManager.getPlayer(0).expectedOutputLines = 1;
            gameTurn++;

//            if (Constants.HANDLE_UI && gameTurn==0)
//                ui.showDraftCards(0, false); // clearing ??

            return false;
        }


        if (gameTurn < expectedConstructionFrames)
        {
            if (gameTurn == 0)
                ConstructTurn(gameManager, () -> ui.constructPhase(gameTurn));
            else
                VisualTurn(gameManager, () -> ui.constructPhase(gameTurn));
            return false;
        }
        else
        {
            return GameTurn(gameManager, () -> ui.battle(gameTurn));
        }
    }

    private void VisualTurn(MultiplayerGameManager<Player> gameManager, Runnable render) {
        for (int player = 0; player < 2; player++) {
            Player sdkplayer = gameManager.getPlayer(player);
            sdkplayer.expectedOutputLines = 0;
            sdkplayer.execute();
            sdkplayer.expectedOutputLines = 1;
        }
        render.run();
        gameTurn++;
    }

    private void ConstructTurn(MultiplayerGameManager<Player> gameManager, Runnable render)
    {
        if (Constants.VERBOSE_LEVEL > 1 && gameTurn == 0) System.out.println("   Construct phase");
        if (Constants.VERBOSE_LEVEL > 2) System.out.println("      Construct turn " + gameTurn + "/" + Constants.CARDS_IN_DECK);

        gameManager.setFrameDuration(Constants.FRAME_DURATION_CONSTRUCTED);

        if (Constants.IS_HUMAN_PLAYING)
            gameManager.setTurnMaxTime(20 * Constants.TIMELIMIT_CONSTRUCTPHASE);
        else
            gameManager.setTurnMaxTime(Constants.TIMELIMIT_CONSTRUCTPHASE);

        for (int player = 0; player < 2; player++) {
            Player sdkplayer = gameManager.getPlayer(player);
            for (String line : constr.getMockPlayersInput(player, gameTurn)) {
                sdkplayer.sendInputLine(line);
            }
            for (Card card : constr.cardsForConstruction)
                sdkplayer.sendInputLine(card.getAsInput());
            sdkplayer.execute();
        }
        for (int player = 0; player < 2; player++) {
            Player sdkplayer = gameManager.getPlayer(player);
            try {
                String output = sdkplayer.getOutputs().get(0);
                for (String action : output.split(";")) {
                    action = action.trim();
                    if (action.isEmpty())
                        continue; // empty action is a valid action
                    ConstructPhase.ChoiceResultPair choice = constr.PlayerChoice(action, player);
                    if (!choice.text.isEmpty())
                        constr.text[player] += choice.text + " ";
                    gameManager.addToGameSummary(
                            String.format("Player %s chose %s", sdkplayer.getNicknameToken(), choice.card.toDescriptiveString())
                    );
                }
            } catch (TimeoutException e) {
                HandleError(gameManager, sdkplayer, sdkplayer.getNicknameToken() + " timeout!");
                return;
            } catch (InvalidActionHard e) {
                HandleError(gameManager, sdkplayer, sdkplayer.getNicknameToken() + ": " + e.getMessage());
                return;
            }
            if (constr.chosenCards[player].size() != Constants.CARDS_IN_DECK){
                HandleError(gameManager, sdkplayer, sdkplayer.getNicknameToken() + " didn't choose correct number of cards!");
                return;
            }
        }

        if (Constants.HANDLE_UI)
            render.run();
        gameTurn++;
    }

    private boolean GameTurn(MultiplayerGameManager<Player> gameManager, Runnable render) {
        Player sdkplayer = gameManager.getPlayer(gamePlayer);
        gameManager.setFrameDuration(Constants.FRAME_DURATION_BATTLE);

        if (state == null) // frame-only turn for showing the initial state
        {
            constr.ShuffleDecks();
            if (Constants.VERBOSE_LEVEL > 1) System.out.println("   Decks shuffled.");
            if (Constants.VERBOSE_LEVEL > 1) System.out.println("   Game phase");
            state = new GameState(constr);

            //gameManager.setTurnMaxTime(1); // weird try but works ^^
            sdkplayer.expectedOutputLines = 0;
            sdkplayer.execute();
            sdkplayer.expectedOutputLines = 1;

            if (Constants.HANDLE_UI)
                render.run();
            return false;
        }

        if (!actionsToHandle.isEmpty()) // there is a legal action on top of the list
        {
            //gameManager.setTurnMaxTime(1); // weird try but works ^^
            sdkplayer.expectedOutputLines = 0;
            sdkplayer.execute();
            sdkplayer.expectedOutputLines = 1;

            Action a = actionsToHandle.remove(0);
            gameManager.addToGameSummary("Player " + sdkplayer.getNicknameToken() + " performed action: " + a.toStringNoText());

            state.AdvanceState(a);
            if (a.type == Action.Type.SUMMON) {
                gameManager.setFrameDuration(Constants.FRAME_DURATION_SUMMON);
            }
        } else // it's time to actually call a player
        {
            if (Constants.VERBOSE_LEVEL > 2) System.out.print("      Game turn " + (gameTurn - Constants.CARDS_IN_DECK) + ", player " + gamePlayer);

            if (Constants.IS_HUMAN_PLAYING)
                gameManager.setTurnMaxTime(200 * Constants.TIMELIMIT_GAMETURN);
            else
                gameManager.setTurnMaxTime(gameTurn <= Constants.CARDS_IN_DECK + 1 ? Constants.TIMELIMIT_FIRSTGAMETURN : Constants.TIMELIMIT_GAMETURN);

            state.AdvanceState();

            for (String line : state.getPlayersInput())
                sdkplayer.sendInputLine(line);
            for (String line : state.getCardsInput())
                sdkplayer.sendInputLine(line);
            sdkplayer.execute();

            try {
                String output = sdkplayer.getOutputs().get(0);
                actionsToHandle = Action.parseSequence(output);
                if (Constants.VERBOSE_LEVEL > 2) System.out.println(" (returned " + actionsToHandle.size() + " actions)");
            } catch (InvalidActionHard e) {
                HandleError(gameManager, sdkplayer, sdkplayer.getNicknameToken() + ": " + e.getMessage());
            } catch (TimeoutException e) {
                HandleError(gameManager, sdkplayer, sdkplayer.getNicknameToken() + " timeout!");
            }
        }

        // now we roll-out actions until next legal is found
        List<Action> legals = state.computeLegalActions(); //System.out.println(gameTurn + " "+ state.players[state.currentPlayer].currentMana +"/"+state.players[state.currentPlayer].maxMana + "->"+legals);
        int illegalActions = 0;

        while (!actionsToHandle.isEmpty()) {
            Action a = actionsToHandle.get(0);
            if (a.type == Type.PASS) {
                actionsToHandle.remove(0); // pop
                continue;
            }
            if (legals.contains(a))
                break;
            actionsToHandle.remove(0); // pop
            illegalActions++;
            if (illegalActions <= ILLEGAL_ACTION_SUMMARY_LIMIT) {
                gameManager.addToGameSummary("[Warning] " + sdkplayer.getNicknameToken() + " Action is not legal: " + a.toString());
            }
        }
        if (illegalActions > ILLEGAL_ACTION_SUMMARY_LIMIT) {
            gameManager.addToGameSummary("[Warning] " + sdkplayer.getNicknameToken() + " Performed another " + (illegalActions - ILLEGAL_ACTION_SUMMARY_LIMIT) + " illegalActions");
        }

        if (Constants.HANDLE_UI)
            render.run();

        if (CheckAndHandleEndgame(gameManager, state))
            return true;

        if (actionsToHandle.isEmpty()) // player change
        {
            gameTurn++;
            gamePlayer = (gamePlayer + 1) % 2;
        }

        return false;
    }

    private void HandleError(MultiplayerGameManager<Player> gameManager, Player sdkplayer, String errmsg) {
        gameManager.addToGameSummary(MultiplayerGameManager.formatErrorMessage(errmsg));
        sdkplayer.deactivate(errmsg);
        sdkplayer.setScore(-1);
        gameManager.endGame();
    }

    // returns true if the game ends
    private boolean CheckAndHandleEndgame(MultiplayerGameManager<Player> gameManager, GameState state) {
        if (state.winner == -1)
            return false;

        //gameManager.addToGameSummary("!\n" + state.toString());

        if (Constants.VERBOSE_LEVEL > 1) System.out.println("   Game finished in turn " + (int)Math.ceil(((float)gameTurn - expectedConstructionFrames + 1) / 2) + ".");
        if (Constants.VERBOSE_LEVEL > 1) System.out.print("   Scores: ");
        if (Constants.VERBOSE_LEVEL > 0) System.out.println((state.winner == 0 ? "1" : "0") + " " + (state.winner == 1 ? "1" : "0"));

        gameManager.addToGameSummary(MultiplayerGameManager.formatSuccessMessage(gameManager.getPlayer(state.winner).getNicknameToken() + " won!"));
        gameManager.getPlayer(state.winner).setScore(1);
        gameManager.endGame();
        return true;
    }

}

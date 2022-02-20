package com.codingame.game.ui;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

import com.codingame.game.Player;
import com.codingame.game.engine.*;
import com.codingame.game.engine.Card.Type;
import com.codingame.gameengine.core.MultiplayerGameManager;
import com.codingame.gameengine.module.entities.GraphicEntityModule;
import com.codingame.gameengine.module.entities.Rectangle;
import com.codingame.gameengine.module.entities.Sprite;
import com.codingame.gameengine.module.entities.Text;
import com.codingame.view.FXModule;
import com.codingame.view.tooltip.TooltipModule;

public class RefereeUI {
    private static final double EPSILON = 0.001;

    public EngineReferee engine;
    public MultiplayerGameManager<Player> gameManager;
    public GraphicEntityModule graphicEntityModule;
    public FXModule fxModule;

    private TooltipModule tooltipModule;

    private Map<Integer, CardUI> cardsPool = new HashMap<>();
    private static PlayerUI[] players = new PlayerUI[2];

    private Text[][] constructedCardsQuantity = new Text[2][Constants.MAX_CARDS_IN_FRAME];

    private Text[] deck = new Text[2];

    private Text[][] manaCurveCosts = new Text[2][8];
    private Rectangle[][] manaCurve = new Rectangle[2][8];
    private Text[][] manaCurveQuantity = new Text[2][8];

    private Text[] cardTypesInfo = new Text[2];
    private Text[] cardTypesQuantity = new Text[2];

    private Sprite[] separators;
    private Sprite newTurnBackground;
    private Text newTurn;
    private int lastturn = -1;


    public void init() {
        tooltipModule = new TooltipModule(gameManager);
        gameManager.setFrameDuration(Constants.FRAME_DURATION_SHOWDRAFT);

        graphicEntityModule.createSpriteSheetSplitter()
            .setName("atlas-")
            .setSourceImage("atlas.png")
            .setWidth(468 / 4)
            .setHeight(264 / 4)
            .setOrigRow(0)
            .setOrigCol(0)
            .setImageCount(160)
            .setImagesPerRow(10)
            .split();

        graphicEntityModule.createSprite()
            .setAnchor(0)
            .setImage("board.jpg")
            .setX(0)
            .setY(0);

        if (Constants.LANES > 1) {
            separators = new Sprite[Constants.LANES - 1];
            for (int lane = 0; lane < Constants.LANES - 1; ++lane) {
                separators[lane] = graphicEntityModule.createSprite()
                    .setAnchorX(0.75)
                    .setAnchorY(0.5)
                    .setImage("separator.png")
                    .setX(ConstantsUI.BOARD.x + lane * ConstantsUI.BOARD_DIM.x / Constants.LANES)
                    .setY(ConstantsUI.BOARD.y)
                    .setAlpha(0);
            }
        }

        newTurnBackground = graphicEntityModule.createSprite()
            .setAnchor(0)
            .setImage("newturn.png")
            .setX(78)
            .setY(482)
            .setAlpha(0);

        for (Player player : gameManager.getPlayers()) {
            players[player.getIndex()] = new PlayerUI(graphicEntityModule, player);
            fxModule.registerNickname(players[player.getIndex()].getNick());
        }

        newTurn = graphicEntityModule.createText("");
        deck[0] = graphicEntityModule.createText("");
        deck[1] = graphicEntityModule.createText("");
        initManaCurve();

        for (int index = 0; index < Constants.MAX_CARDS_IN_FRAME; ++index) {
            getCardFromPool(-(index + 1)).setVisible(false);

            for (Player player : gameManager.getPlayers()) {
                int playerIndex = player.getIndex();
                constructedCardsQuantity[playerIndex][index] =
                    graphicEntityModule.createText("")
                    .setAnchorX(0.5)
                    .setFontSize(20)
                    .setFillColor(player.getColorToken())
                    .setStrokeColor(0x000000)
                    .setStrokeThickness(3.5)
                    .setVisible(false);
            }
        }
    }

    public void constructPhase(int turn) {
        int constructionCardSpaceX = (int) ((ConstantsUI.CARD_BOARD_SPACE + ConstantsUI.CARD_DIM.x) * ConstantsUI.CARD_CONSTRUCTED_SCALE);
        int constructionCardSpaceY = (int) ((ConstantsUI.CARD_BOARD_SPACE + ConstantsUI.CARD_DIM.y) * ConstantsUI.CARD_CONSTRUCTED_SCALE);
        int constructionAreaX = ConstantsUI.BOARD.x - 5 * constructionCardSpaceX + (int) (ConstantsUI.CARD_BOARD_SPACE * ConstantsUI.CARD_CONSTRUCTED_SCALE/2);
        int constructionAreaY = ConstantsUI.BOARD.y - 2 * constructionCardSpaceY + (int) (ConstantsUI.CARD_BOARD_SPACE * ConstantsUI.CARD_CONSTRUCTED_SCALE/2);

        List<Card> picks = engine.constr.cardsForConstruction;

        for (int frameIndex = 0; frameIndex < Constants.MAX_CARDS_IN_FRAME; ++frameIndex) {
            int index = turn * Constants.MAX_CARDS_IN_FRAME + frameIndex;
            int cardX = constructionAreaX + (int) (constructionCardSpaceX * ((frameIndex) % 10));
            int cardY = constructionAreaY + (int) (constructionCardSpaceY * Math.floor((frameIndex) / 10));

            CardUI cardUi = getCardFromPool(-(frameIndex+1));
            if (index >= picks.size()) {
                for (Player player : gameManager.getPlayers()) {
                    int playerIndex = player.getIndex();
                    constructedCardsQuantity[playerIndex][frameIndex]
                        .setVisible(false)
                        .setAlpha(0);
                    graphicEntityModule.commitEntityState(0.0, constructedCardsQuantity[playerIndex][frameIndex]);
                }
                cardUi
                    .setVisible(false)
                    .commit(0.0);
            } else {
                Card card = picks.get(index);
                for (Player player : gameManager.getPlayers()) {
                    int playerIndex = player.getIndex();
                    constructedCardsQuantity[playerIndex][frameIndex]
                        .setVisible(false);
                    graphicEntityModule.commitEntityState(0.0, constructedCardsQuantity[playerIndex][frameIndex]);
                    if (engine.constr.chosenQuantities[playerIndex][card.baseId] > 0) {
                        constructedCardsQuantity[playerIndex][frameIndex]
                            .setText("x" + engine.constr.chosenQuantities[playerIndex][card.baseId])
                            .setX(cardX + (playerIndex * 2 - 1) * (ConstantsUI.CARD_BOARD_SPACE - 20) + 42)
                            .setY(cardY-5)
                            .setScaleY(0.0)
                            .setVisible(true);
                        graphicEntityModule.commitEntityState(0.0, constructedCardsQuantity[playerIndex][frameIndex]);
                        constructedCardsQuantity[playerIndex][frameIndex]
                            .setScaleY(1.0);
                        graphicEntityModule.commitEntityState(0.2, constructedCardsQuantity[playerIndex][frameIndex]);
                    }
                    getCardFromPool(-(frameIndex+1))
                        .setScaleY(0)
                        .setScaleX(ConstantsUI.CARD_CONSTRUCTED_SCALE)
                        .move(cardX, cardY, card)
                        .commit(0.0)
                        .setScaleY(ConstantsUI.CARD_CONSTRUCTED_SCALE)
                        .commit(0.2);
                }
            }

        }
        if (turn == 0) {
            for (Player player : gameManager.getPlayers()) {
                int playerIndex = player.getIndex();
                Vector2D offset = Vector2D.mult(ConstantsUI.PLAYER_OFFSET, 1 - playerIndex);

                if (!engine.constr.text[playerIndex].isEmpty()) {
                    players[playerIndex].talk(engine.constr.text[playerIndex], true);
                } else {
                    players[playerIndex].hideBubble();
                }

                deck[1 - playerIndex]
                        .setText(Integer.toString(Constants.CARDS_IN_DECK))
                        .setAnchor(0.5)
                        .setFillColor(0xffffff)
                        .setFontSize(40)
                        .setStrokeColor(0x000000)
                        .setStrokeThickness(4.0)
                        .setX(Vector2D.add(ConstantsUI.PLAYER_DECK_TXT, offset).x)
                        .setY(Vector2D.add(ConstantsUI.PLAYER_DECK_TXT, offset).y);
            }

            newTurnBackground
                    .setX(78)
                    .setY(482)
                    .setAlpha(1);

            newTurn
                    .setText("Cards: " + Integer.toString(Constants.CARDS_IN_DECK))
                    .setAnchor(0.5)
                    .setFontSize(50)
                    .setFillColor(0xffffff)
                    .setStrokeColor(0x000000)
                    .setStrokeThickness(4.0)
                    .setX(78+314/2)
                    .setY(ConstantsUI.BOARD.y);

            graphicEntityModule.commitEntityState(0,  newTurnBackground, newTurn);
            drawManaCurve();
        }
    }

    private void initManaCurve() {
        for (int p=0; p<2; p++) {
            cardTypesInfo[p] = graphicEntityModule.createText("     Creatures:\nGreen Items:\n     Red Items:\n    Blue Items:")
                    .setAnchor(0.5)
                    .setFontSize(ConstantsUI.MC_COST_FONTSIZE)
                    .setFillColor(0xffffff)
                    .setStrokeColor(0x000000)
                    .setStrokeThickness(4.0)
                    .setX(ConstantsUI.MC_TYINFO_X)
                    .setY( ConstantsUI.MC_PLAYERS_OFFSET[p] + ConstantsUI.MC_TYINFO_Y);

            cardTypesQuantity[p] = graphicEntityModule.createText("0\n0\n0\n0")
                    .setAnchor(0.5)
                    .setFontSize(ConstantsUI.MC_COST_FONTSIZE)
                    .setFillColor(0xffffff)
                    .setStrokeColor(0x000000)
                    .setStrokeThickness(4.0)
                    .setX(ConstantsUI.MC_TYINFO_X + ConstantsUI.MC_TYINFO_X_QUANTITY_OFFS)
                    .setY(ConstantsUI.MC_PLAYERS_OFFSET[p] + ConstantsUI.MC_TYINFO_Y);

            for (int m = 0; m < 8; m++) {
                manaCurveCosts[p][m] = graphicEntityModule.createText(m < 7 ? Integer.toString(m) : "7+")
                        .setAnchor(0.5)
                        .setFontSize(ConstantsUI.MC_COST_FONTSIZE)
                        .setFillColor(0xffffff)
                        .setStrokeColor(0x000000)
                        .setStrokeThickness(4.0)
                        .setX(ConstantsUI.MC_COST_X + (m * ConstantsUI.MC_COST_WIDTH) + ConstantsUI.MC_COST_WIDTH / 2)
                        .setY(ConstantsUI.MC_PLAYERS_OFFSET[p] + ConstantsUI.MC_GRAPH_LOWY + (ConstantsUI.SCREEN_DIM.y - ConstantsUI.MC_GRAPH_LOWY) / 2);

                manaCurve[p][m] = graphicEntityModule.createRectangle()
                        .setFillColor(0x4d79d0)
                        .setHeight(0)
                        .setWidth(ConstantsUI.MC_GRAPH_WIDTH)
                        .setX(ConstantsUI.MC_COST_X + m * ConstantsUI.MC_COST_WIDTH + (ConstantsUI.MC_COST_WIDTH-ConstantsUI.MC_GRAPH_WIDTH)/2)
                        .setY(ConstantsUI.MC_PLAYERS_OFFSET[p] + ConstantsUI.MC_GRAPH_LOWY);

                manaCurveQuantity[p][m] = graphicEntityModule.createText("")
                        .setAnchor(0.5)
                        .setFontSize(ConstantsUI.MC_QUANTITY_FONTSIZE)
                        .setFillColor(0xffffff)
                        .setStrokeColor(0x000000)
                        .setStrokeThickness(4.0)
                        .setX(ConstantsUI.MC_COST_X + (m * ConstantsUI.MC_COST_WIDTH) + ConstantsUI.MC_COST_WIDTH/2)
                        .setY(ConstantsUI.MC_PLAYERS_OFFSET[p] + ConstantsUI.MC_GRAPH_LOWY + (ConstantsUI.SCREEN_DIM.y - ConstantsUI.MC_GRAPH_LOWY)/2);
            }
        }
    }

    private void drawManaCurve() {
        for (int p=0; p<2; p++) {
            int[] mc = new int[8];
            int[] ct = new int[4];

            for (Card c : engine.constr.chosenCards[p]) {
                if (c.cost < 7) mc[c.cost]++;
                else            mc[7]++;

                switch (c.type) {
                    case CREATURE: ct[0]++; break;
                    case ITEM_GREEN: ct[1]++; break;
                    case ITEM_RED: ct[2]++; break;
                    case ITEM_BLUE: ct[3]++; break;
                }
            }
            String[] cts = new String[4];
            for (int i=0; i < 4; i++) cts[i] = ct[i] +  (ct[i] < 10 ? " " : "");
            cardTypesQuantity[p].setText(String.join("\n", cts));

            int maxmc = Arrays.stream(mc).max().getAsInt();
            boolean overflow = maxmc  * ConstantsUI.MC_GRAPH_STEP > ConstantsUI.MC_GRAPH_MAXSIZE;

            for (int m = 0; m < 8; m++) {
                int h = mc[m] * ConstantsUI.MC_GRAPH_STEP;
                if (overflow)
                    h = ConstantsUI.MC_GRAPH_MAXSIZE * mc[m] / maxmc;
                if (h == 0)
                    h = ConstantsUI.MC_GRAPH_ZEROSIZE;

                manaCurve[p][m]
                        .setHeight(h)
                        .setY(ConstantsUI.MC_PLAYERS_OFFSET[p] + ConstantsUI.MC_GRAPH_LOWY - h);

                int texty = ConstantsUI.MC_GRAPH_LOWY - h + ConstantsUI.MC_QUANTITY_FONTSIZE / 2; // text below
                if (h < ConstantsUI.MC_QUANTITY_FONTSIZE)
                    texty = ConstantsUI.MC_GRAPH_LOWY - h - ConstantsUI.MC_QUANTITY_FONTSIZE / 2; // text above

                manaCurveQuantity[p][m]
                        .setText(mc[m] > 0 ? Integer.toString(mc[m]) : "")
                        .setY(ConstantsUI.MC_PLAYERS_OFFSET[p] + texty);
            }
        }
    }

    public void cleanupAfterConstruction() {
        for (int p=0; p<2; p++) {
            cardTypesInfo[p].setAlpha(0);
            cardTypesQuantity[p].setAlpha(0);
            for (int m = 0; m < 8; m++) {
                manaCurveCosts[p][m].setAlpha(0);
                manaCurve[p][m].setAlpha(0);
                manaCurveQuantity[p][m].setAlpha(0);
            }
            for (int index = 0; index < Constants.MAX_CARDS_IN_FRAME; ++index) {
                getCardFromPool(-(index + 1)).setVisible(false);
                if (constructedCardsQuantity[p][index] != null)
                    constructedCardsQuantity[p][index].setAlpha(0);
            }
        }
        for (int i = 0; i<Constants.MAX_CREATURES_IN_LINE; i++)
            getCardFromPool(-(i+1))
                .setVisible(false)
                .setScale(ConstantsUI.CARD_HAND_SCALE);
    }

    public void battle(int turn) {
        prepareForBattleTurn(turn);

        ArrayList<Action> actions = engine.state.players[turn % 2].performedActions;
        Action action = actions.size() == 0 ? null : actions.get(actions.size() - 1);

        if (action != null && action.type == Action.Type.SUMMON)
            handleSummonAction(action);

        for (Player player : gameManager.getPlayers()) {
            int playerIndex = player.getIndex();

            // Expose an API in the engine?
            Gamer gamer = engine.state.players[playerIndex];

            // Update player.
            players[playerIndex]
                    .setActive(turn % 2 == playerIndex)
                    .updateStats(gamer);

            updateBoard(playerIndex, gamer.board);
            updateHand(playerIndex, gamer.hand);
        }

        int playerIndex = turn % 2;

        if (action != null && action.text != null && !action.text.isEmpty())
            players[playerIndex].talk(action.text, false);
        else
            players[playerIndex].hideBubble();

        if (action != null && action.type == Action.Type.ATTACK)
            handleAttackAction(playerIndex, action);
        else if (action != null && (action.type == Action.Type.USE))
            handleUseAction(playerIndex, action);

        if (action != null) {
            players[playerIndex].attacker(action.result);
            players[1 - playerIndex].defender(action.result);
        }
    }

    private void prepareForBattleTurn(int turn) {
        for (int playerIndex = 0; playerIndex < 2; ++playerIndex) {
            players[playerIndex].hideBubble();
        }

        newTurn.setAlpha(0);
        deck[0].setAlpha(0);
        deck[1].setAlpha(0);

        if (Constants.LANES > 1)
            for (Sprite separator : separators)
                separator.setAlpha(1);

        if (turn != lastturn) {
            lastturn = turn;

            newTurnBackground
                    .setX(78)
                    .setAlpha(1);

            newTurn
                    .setText("Turn " + Integer.toString((turn - engine.expectedConstructionFrames) / 2))
                    .setAnchor(0.5)
                    .setFontSize(50)
                    .setFillColor(gameManager.getPlayers().get(turn % 2).getColorToken())
                    .setStrokeColor(0x000000)
                    .setStrokeThickness(4.0)
                    .setX(78 + 314 / 2)
                    .setY(ConstantsUI.BOARD.y)
                    .setAlpha(1);
        } else {
            newTurnBackground.setAlpha(0);
            newTurn.setText("");
        }

        graphicEntityModule.commitEntityState(0, newTurn, newTurnBackground);

        for (CardUI card : cardsPool.values())
            if (!card.isVisible())
                card.setVisible(false);
    }

    private void updateBoard(int playerIndex, ArrayList<CreatureOnBoard> board) {
        int boardX = ConstantsUI.BOARD.x;
        int boardY = ConstantsUI.BOARD.y + (int) (ConstantsUI.BOARD_DIM.y * (0.5 - playerIndex) / 2.0);
        int bcw = (int) (ConstantsUI.CARD_BOARD_SCALE * ConstantsUI.CARD_DIM.x * 0.8);
        int bch = (int) (ConstantsUI.CARD_BOARD_SCALE * ConstantsUI.CARD_DIM.y);
        int bcs = ConstantsUI.CARD_BOARD_SPACE;

        for (int lane = 0; lane < Constants.LANES; ++lane) {
            // We love Java, right?
            final int _lane = lane;
            ArrayList<CreatureOnBoard> cardsInLane = board
                    .stream()
                    .filter(card -> card.lane == _lane)
                    .collect(Collectors.toCollection(ArrayList::new));

            int laneX = Constants.LANES == 1 ? 0 : (int) ((lane - 0.5) * ConstantsUI.BOARD_DIM.x / Constants.LANES);
            int boardCenterX = ((bcw + bcs) * cardsInLane.size() + (cardsInLane.size() % 2) * bcs / 2) / 2;

            for (int index = 0; index < cardsInLane.size(); ++index) {
                int cardXOffset = (bcw + bcs) * index;
                int cardX = boardX - laneX - boardCenterX + cardXOffset;
                int cardY = boardY - bch / 2;

                CreatureOnBoard card = cardsInLane.get(index);
                Card base = Constants.CARDSET.values().stream()
                        .filter(x -> x.baseId == card.baseId)
                        .findAny()
                        .get();

                getCardFromPool(card.id)
                        .setScale(ConstantsUI.CARD_BOARD_SCALE)
                        .move(cardX, cardY, base, card, true);
            }
        }
    }

    private void updateHand(int playerIndex, ArrayList<Card> hand) {
        int handX = ConstantsUI.BOARD.x;
        int handY = ConstantsUI.BOARD.y + (ConstantsUI.BOARD_DIM.y + ConstantsUI.CARD_HAND_DIM.y + 20) * ((1 - playerIndex) * 2 - 1) / 2;
        int hcw = (int) (ConstantsUI.CARD_HAND_SCALE * ConstantsUI.CARD_DIM.x);
        int hch = (int) (ConstantsUI.CARD_HAND_SCALE * ConstantsUI.CARD_DIM.y);
        int hcs = ConstantsUI.CARD_HAND_SPACE;
        int handCenterX = ((hcw + hcs) * hand.size() + (hand.size() % 2) * hcs / 2) / 2;
        Vector2D offset = Vector2D.mult(ConstantsUI.PLAYER_OFFSET, 1 - playerIndex);

        for (int index = 0; index < hand.size(); ++index) {
            int cardXOffset = (hcw + hcs) * index;
            int cardX = handX - handCenterX + cardXOffset;
            int cardY = handY - hch / 2;

            Card card = hand.get(index);
            CardUI cardUI = getCardFromPool(card.id);

            if (cardUI.getX() == 0) {
                cardUI
                        .lift()
                        .setScale(ConstantsUI.CARD_DECK_SCALE)
                        .move(
                                Vector2D.add(Vector2D.sub(ConstantsUI.PLAYER_DRAW_TXT, Vector2D.div(ConstantsUI.PLAYER_DECK_DIM, 2)), offset).x,
                                Vector2D.add(Vector2D.sub(ConstantsUI.PLAYER_DRAW_TXT, Vector2D.div(ConstantsUI.PLAYER_DECK_DIM, 2)), offset).y,
                                card
                        )
                        .commit(0.0);
            }

            cardUI
                    .setScale(ConstantsUI.CARD_HAND_SCALE)
                    .move(cardX, cardY, card)
                    .ground();
        }

    }

    private void handleSummonAction(Action action) {
        SummonResult result = (SummonResult) action.result;
        for (CreatureOnBoard copyCreature : result.summonedCreatures) {
            if (copyCreature.id == result.originalCreature.id)
                continue;
            CardUI cardUI1 = getCardFromPool(result.originalCreature.id);
            CardUI cardUI2 = getCardFromPool(copyCreature.id);
            Card card = engine.state.cardIdMap.get(action.arg1);
            cardUI2
                    .move(cardUI1.getX(), cardUI1.getY(), card)
                    .setScale(ConstantsUI.CARD_HAND_SCALE)
                    .commit(0.0);
        }
    }

    private void handleAttackAction(int playerIndex, Action action) {
        Vector2D offset = Vector2D.mult(ConstantsUI.PLAYER_OFFSET, playerIndex);
        CardUI cardUI1 = cardsPool.get(action.arg1);

        int x1 = cardUI1.getX();
        int y1 = cardUI1.getY();

        Card card = engine.state.cardIdMap.get(action.arg1);
        Optional<CreatureOnBoard> creature = engine.state.players[playerIndex].board.stream()
                .filter(x -> x.id == card.id)
                .findAny();

        CardUI cardUI2 = action.arg2 == -1 ? null : cardsPool.get(action.arg2);
        int x2 = cardUI2 == null
                ? ConstantsUI.PLAYER_AVATAR.x - cardUI1.getWidth() / 2 + offset.x
                : cardUI2.getX() + (cardUI2.getWidth() - cardUI1.getWidth()) / 2;
        int y2 = cardUI2 == null
                ? ConstantsUI.PLAYER_AVATAR.y - cardUI1.getHeight() / 2 + offset.y
                : cardUI2.getY() + (cardUI2.getHeight() - cardUI1.getHeight()) / 2;

        if (creature.isPresent()) {
            animateAttackAndLive(cardUI1, card, creature.get(), action, card.id, x1, y1, x2, y2);
        } else {
            Optional<CreatureOnBoard> graveyardCreature = searchCreatureInGraveyard(playerIndex, card.id);
            boolean isOnBoard = graveyardCreature.isPresent();
            assert isOnBoard : "Attacking creature should to be alive or on graveyard";
            CreatureOnBoard realCreature = graveyardCreature.get();
            animateAttackAndDie(cardUI1, card, realCreature, action, card.id, x1, y1, x2, y2);
        }

        if (cardUI2 != null) {
            Optional<CreatureOnBoard> graveyardCreature2 = searchCreatureInGraveyard(1 - playerIndex, action.arg2);
            if (graveyardCreature2.isPresent()) {
                forceCommitAlpha1(cardUI2, 0.5);
                cardUI2.setVisible(false);
                cardUI2.commit(1);
            }
            cardUI2.action((AttackResult) action.result, action.arg2);
        }
    }

    private void handleUseAction(int playerIndex, Action action) {
        Vector2D offset = Vector2D.mult(ConstantsUI.PLAYER_OFFSET, playerIndex);
        if (actionPlayedOnSelf(action)) {
            offset = Vector2D.mult(ConstantsUI.PLAYER_OFFSET, 1 - playerIndex);
        }
        CardUI cardUI1 = cardsPool.get(action.arg1);
        int x1 = cardUI1.getX();
        int y1 = cardUI1.getY();
        Card card = engine.state.cardIdMap.get(action.arg1);
        Optional<CreatureOnBoard> graveyardCreature = searchCreatureInGraveyard(playerIndex, card.id);
        CreatureOnBoard realCreature = graveyardCreature.orElseGet(() -> new CreatureOnBoard(card));

        UseResult result = (UseResult) action.result;

        if (action.arg2 == -1) {
            int x2 = ConstantsUI.PLAYER_AVATAR.x - cardUI1.getWidth() / 2 + offset.x;
            int y2 = ConstantsUI.PLAYER_AVATAR.y - cardUI1.getHeight() / 2 + offset.y;
            animateUse(cardUI1, card, realCreature, x1, y1, x2, y2);
        } else {
            for (int i = 0; i < result.targets.size(); i++) {
                UseResult.CreatureUseResult partialResult = result.targets.get(i);
                CardUI itemCopyUI = cardsPool.get(-(i + 1));
                itemCopyUI
                        .move(x1, y1, card, realCreature, false)
                        .commit(0.0);

                CardUI cardUI2 = cardsPool.get(partialResult.target.id);
                int x2 = cardUI2.getX() + (cardUI2.getWidth() - cardUI1.getWidth()) / 2;
                int y2 = cardUI2.getY() + (cardUI2.getHeight() - cardUI1.getHeight()) / 2;

                animateUse(itemCopyUI, card, realCreature, x1, y1, x2, y2);

                Optional<CreatureOnBoard> graveyardCreature2 = searchCreatureInGraveyard(1 - playerIndex, partialResult.target.id);
                if (graveyardCreature2.isPresent()) {
                    forceCommitAlpha1(cardUI2, 0.5);
                    cardUI2.setVisible(false);
                    cardUI2.commit(1);
                }
                cardUI2.action(partialResult, action.arg2);
            }
        }
    }

    private Optional<CreatureOnBoard> searchCreatureInGraveyard(int playerIndex, int searchedId) {
        return engine.state.players[playerIndex].graveyard.stream()
                .filter(x -> x.id == searchedId)
                .findAny();
    }

    private boolean actionPlayedOnSelf(Action action) {
        Card card = engine.state.cardIdMap.get(action.arg1);

        return card.type == Type.ITEM_BLUE &&
            action.result.attackingPlayerHealthChange > 0 &&
            action.result.defendingPlayerHealthChange == 0;
    }

    private void animateUse(CardUI cardUI, Card card, CreatureOnBoard creature, int x1, int y1, int x2, int y2) {
        cardUI
        .lift()
        .move(x1, y1, card, creature, false)
        .commitGroup(0.0)
        .zoom(x1, y1, (cardUI.getScaleX() + cardUI.getScaleY()) / 2)
        .commitGroup(0.1)
        .move(x2, y2, card, creature, false)
        .setVisible(true)
        .commit(0.5)
        .ground()
        .setVisible(false)
        .commit(1);
    }

    private void animateAttackAndDie(CardUI cardUI, Card card, CreatureOnBoard creature, Action action, int attackerId, int x1, int y1, int x2, int y2) {
        cardUI
            .lift()
            .action((AttackResult) action.result, card.id)
            .move(x1, y1, card, creature, true)
            .commitGroup(0.0)
            .zoom(x1 + ConstantsUI.ZOOM_OFFSET.x, y1 + ConstantsUI.ZOOM_OFFSET.y, ConstantsUI.LIFTED_CARD_BOARD_SCALE)
            .commitGroup(0.1)
            .move(x2 + ConstantsUI.ZOOM_OFFSET.x, y2 + ConstantsUI.ZOOM_OFFSET.y, card, creature, true)
            .commitGroup(0.5)
            .move(x1 + ConstantsUI.ZOOM_OFFSET.x, y1 + ConstantsUI.ZOOM_OFFSET.y, card, creature, true)
            .ground()
            .setVisibility(0.1)
            .commitGroup(0.9)
            .zoom(x1, y1, ConstantsUI.CARD_BOARD_SCALE)
            .setVisible(false)
            .commit(1.0);
    }

    private void animateAttackAndLive(CardUI cardUI, Card card, CreatureOnBoard creature, Action action, int attackerId, int x1, int y1, int x2, int y2) {
        cardUI
        .lift()
        .action((AttackResult) action.result, attackerId)
        .move(x1, y1, card, creature, true)
        .commitGroup(0.0)
        .zoom(x1 + ConstantsUI.ZOOM_OFFSET.x, y1 + ConstantsUI.ZOOM_OFFSET.y, ConstantsUI.LIFTED_CARD_BOARD_SCALE)
        .commitGroup(0.1)
        .move(x2 + ConstantsUI.ZOOM_OFFSET.x, y2 + ConstantsUI.ZOOM_OFFSET.y, card, creature, true)
        .commitGroup(0.5)
        .move(x1 + ConstantsUI.ZOOM_OFFSET.x, y1 + ConstantsUI.ZOOM_OFFSET.y, card, creature, true)
        .ground()
        .commitGroup(0.9)
        .zoom(x1, y1, ConstantsUI.CARD_BOARD_SCALE)
        .commit(1.0);
    }

    /**
     * Work-around a limitation of the SDK in its current state. <br>
     * It is not possible to start value interpolation at a given t if the value has not changed at t
     * (unless a different property is changed too).<br>
     * This method changes the value of alpha by an imperceptable amount <br>
     * It assumes alpha is currently set to 1
     */
    private void forceCommitAlpha1(CardUI card, double t) {
        card.setVisibility(1-EPSILON);
        card.commit(t);
    }

    private CardUI getCardFromPool(int cardId) {
        if (cardsPool.containsKey(cardId))
            return cardsPool.get(cardId).setVisible(true);

        CardUI card = new CardUI(graphicEntityModule, tooltipModule);
        cardsPool.put(cardId, card);
        return card;
    }
}

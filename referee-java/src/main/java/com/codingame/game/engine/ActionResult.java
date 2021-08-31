package com.codingame.game.engine;

public class ActionResult {
    public final int attackingPlayerHealthChange;
    public final int defendingPlayerHealthChange;
    public final int cardDraw;

    public ActionResult(int attackingPlayerHealthChange, int defendingPlayerHealthChange, int cardDraw) {
        this.attackingPlayerHealthChange = attackingPlayerHealthChange;
        this.defendingPlayerHealthChange = defendingPlayerHealthChange;
        this.cardDraw = cardDraw;
    }
}

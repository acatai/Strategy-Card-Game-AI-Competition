package com.codingame.game.engine;

import java.util.List;

public class SummonResult extends ActionResult {
    public final List<CreatureOnBoard> summonedCreatures;
    public final CreatureOnBoard originalCreature;

    public SummonResult(List<CreatureOnBoard> summonedCreatures, int attackingPlayerHealthChange, int defendingPlayerHealthChange, int cardDraw) {
        super(attackingPlayerHealthChange, defendingPlayerHealthChange, cardDraw);
        this.summonedCreatures = summonedCreatures;
        this.originalCreature = summonedCreatures.get(0);
    }
}

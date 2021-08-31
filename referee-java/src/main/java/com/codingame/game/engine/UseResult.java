package com.codingame.game.engine;

import java.util.ArrayList;
import java.util.List;

public class UseResult extends ActionResult {
    public static class CreatureUseResult {
        public final CreatureOnBoard target;
        public final boolean targetDied;
        public final int targetAttackChange;
        public final int targetDefenseChange;

        public CreatureUseResult(CreatureOnBoard target, boolean targetDied, int targetAttackChange, int targetDefenseChange) {
            this.target = target;
            this.targetDied = targetDied;
            this.targetAttackChange = targetAttackChange;
            this.targetDefenseChange = targetDefenseChange;
        }
    }

    public final CreatureOnBoard item;
    public final List<CreatureUseResult> targets;

    public UseResult(CreatureOnBoard item, List<CreatureUseResult> targets,
                     int attackingPlayerHealthChange, int defendingPlayerHealthChange, int cardDraw) {
        super(attackingPlayerHealthChange, defendingPlayerHealthChange, cardDraw);
        this.item = item;
        this.targets = targets;
    }

    public UseResult(CreatureOnBoard item, int attackingPlayerHealthChange, int defendingPlayerHealthChange, int cardDraw) {
        super(attackingPlayerHealthChange, defendingPlayerHealthChange, cardDraw);
        this.item = item;
        this.targets = new ArrayList<>();
    }
}

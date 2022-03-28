package com.codingame.game.engine;

public class AttackResult extends ActionResult {
    public final CreatureOnBoard attacker;
    public final CreatureOnBoard defender;
    public final boolean attackerDied;
    public final boolean defenderDied;
    public final int attackerDefenseChange;
    public final int defenderDefenseChange;

    public AttackResult(CreatureOnBoard attacker, CreatureOnBoard defender, boolean attackerDied, boolean defenderDied,
                        int attackingPlayerHealthChange, int defendingPlayerHealthChange, int cardDraw,
                        int attackerDefenseChange, int defenderDefenseChange) {
        super(attackingPlayerHealthChange, defendingPlayerHealthChange, cardDraw);
        this.attacker = attacker;
        this.defender = defender;
        this.attackerDied = attackerDied;
        this.defenderDied = defenderDied;
        this.attackerDefenseChange = attackerDefenseChange;
        this.defenderDefenseChange = defenderDefenseChange;
    }

    public AttackResult(CreatureOnBoard attacker, int attackingPlayerHealthChange, int defendingPlayerHealthChange, int cardDraw) {
        super(attackingPlayerHealthChange, defendingPlayerHealthChange, cardDraw);
        this.attacker = attacker;
        this.defender = null;
        this.attackerDied = false;
        this.defenderDied = false;
        this.attackerDefenseChange = 0;
        this.defenderDefenseChange = 0;
    }
}

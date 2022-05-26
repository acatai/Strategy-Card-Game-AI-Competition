package com.codingame.game.engine.cardgenerator;

import com.codingame.game.engine.Card;

import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

class CardBuilder {
    private double budget;
    private final Map<String, String> properties;

    CardBuilder(String type, double mana) {
        this.budget = mana;
        this.properties = new HashMap<>();
        properties.put("type", type);
        properties.put("mana", Integer.toString((int) mana));
    }

    public double getCost() {
        return Double.parseDouble(properties.get("mana"));
    }

    private void changeMana(Property prop) {
        this.budget = this.budget * prop.getMultCost() - prop.getAddCost();
    }

    private void reverseChangeMana(Property prop) {
        this.budget = (this.budget + prop.getAddCost()) / prop.getMultCost();
    }

    void addBaseId(int id) {
        properties.put("id", Integer.toString(id));
    }

    boolean addProperty(String name, Property prop) {
        changeMana(prop);
        if (budget < 0) {
            reverseChangeMana(prop);
            return false;
        } else {
            properties.put(name, prop.getName());
            return true;
        }
    }

    void addAttackAndDefense(NormalDistributionGenerator bonusAttackGenerator, NormalDistributionGenerator bonusDefenseGenerator) {
        int attack = (int) (budget + bonusAttackGenerator.next());
        int defense = (int) (budget + bonusDefenseGenerator.next());
        if (Objects.equals(properties.get("type"), "creature")) {
            attack = Math.max(attack, 0);
            defense = Math.max(defense, 1);
        } else if (Objects.equals(properties.get("type"), "itemBlue")) {
            attack = 0;
            defense = Math.max(defense, 0);
        } else {
            attack = Math.max(attack, 0);
            defense = Math.max(defense, 0);
        }

        if (Objects.equals(properties.get("type"), "itemRed") || Objects.equals(properties.get("type"), "itemBlue")) {
            attack *= -1;
            defense *= -1;
        }
        properties.put("attack", Integer.toString(attack));
        properties.put("defense", Integer.toString(defense));
    }

    private String readKeywords() {
        return
                (properties.containsKey("breakthrough") ? "B" : "-") +
                (properties.containsKey("charge") ? "C" : "-") +
                (properties.containsKey("drain") ? "D" : "-") +
                (properties.containsKey("guard") ? "G" : "-") +
                (properties.containsKey("lethal") ? "L" : "-") +
                (properties.containsKey("ward") ? "W" : "-");
    }

    Card createCard() {
        return new Card(new String[]{
                properties.getOrDefault("id", "-1"),
                "#" + properties.getOrDefault("id", "-1"),
                properties.getOrDefault("type", "creature"),
                properties.getOrDefault("mana", "0"),
                properties.getOrDefault("attack", "0.0"),
                properties.getOrDefault("defense", "0.0"),
                readKeywords(),
                properties.getOrDefault("myHealthChange", "0"),
                properties.getOrDefault("oppHealthChange", "0"),
                properties.getOrDefault("draw", "0"),
                properties.getOrDefault("area", "target")
        });
    }
}

package com.codingame.game.engine.cardgenerator;

class Property {
    private final String name;
    private final double weight;
    private final double multCost;
    private final double addCost;

    Property(String name, double weight, double multCost, double addCost) {
        this.name = name;
        this.weight = weight;
        this.multCost = multCost;
        this.addCost = addCost;
    }

    public String getName() {
        return name;
    }

    public double getWeight() {
        return weight;
    }

    public double getMultCost() {
        return multCost;
    }

    public double getAddCost() {
        return addCost;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj)
            return true;
        if (obj == null)
            return false;
        if (getClass() != obj.getClass())
            return false;
        Property other = (Property) obj;
        return name.equals(other.name);
    }
}

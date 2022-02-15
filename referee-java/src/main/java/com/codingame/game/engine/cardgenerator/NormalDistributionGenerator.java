package com.codingame.game.engine.cardgenerator;

import java.util.Random;

class NormalDistributionGenerator {
    private final Random RNG;
    private final double mean;
    private final double std;

    NormalDistributionGenerator(Random originalRNG, double mean, double std) {
        this.RNG = new Random(originalRNG.nextInt());
        this.mean = mean;
        this.std = std;
    }

    double next() {
        return RNG.nextDouble() * std + mean;
    }
}

package com.codingame.game.engine.cardgenerator;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Random;

class PropertiesOrderGenerator<T> {
    private final List<T> elements;
    private final Random RNG;

    PropertiesOrderGenerator(Random originalRNG, List<T> elements) {
        this.elements = elements;
        this.RNG = new Random(originalRNG.nextInt());
    }

    List<T> shuffle() {
        Collections.shuffle(elements, RNG);
        return new ArrayList<>(elements);
    }
}

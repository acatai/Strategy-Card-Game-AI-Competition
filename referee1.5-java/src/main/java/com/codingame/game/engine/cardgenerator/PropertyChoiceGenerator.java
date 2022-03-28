package com.codingame.game.engine.cardgenerator;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.stream.Collectors;

class PropertyChoiceGenerator extends WeightedChoiceGenerator<Property> {
    PropertyChoiceGenerator(Random originalRNG, List<Property> values) {
        super(originalRNG,
                values,
                values.stream().map(Property::getWeight).collect(Collectors.toCollection(ArrayList::new)));
    }
}

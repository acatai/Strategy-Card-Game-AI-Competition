package com.codingame.game.engine.cardgenerator;

import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

class WeightedChoiceGenerator<T> {
    private final List<T> values;
    private final List<Double> weights;
    private final double sumOfWeights;
    private final Random RNG;

    WeightedChoiceGenerator(Random originalRNG, List<T> values, List<Double> weights) {
        List<Integer> sortedIndices = IntStream.range(0, weights.size())
                .boxed().sorted(Comparator.comparingDouble(weights::get))
                .collect(Collectors.toList());
        this.values = sortedIndices.stream().map(values::get).collect(Collectors.toCollection(ArrayList::new));
        this.weights = sortedIndices.stream().map(weights::get).collect(Collectors.toCollection(ArrayList::new));
        this.sumOfWeights = weights.stream().mapToDouble(x -> x).sum();
        this.RNG = new Random(originalRNG.nextInt());
    }

    WeightedChoiceGenerator(Random originalRNG, Map<T, Double> m) {
        this(originalRNG, new ArrayList<>(m.keySet()), new ArrayList<>(m.values()));
    }

    T randomChoice() {
        double choice = RNG.nextDouble() * sumOfWeights;
        for (int i = 0; i < values.size(); i++) {
            choice -= weights.get(i);
            if (choice <= 0)
                return values.get(i);
        }
        return values.get(values.size() - 1);
    }

    T randomChoiceWithBlacklist(List<T> blacklist) {
        List<Integer> whitelistIndices = IntStream.range(0, weights.size())
                .filter(i -> !blacklist.contains(values.get(i))).boxed()
                .collect(Collectors.toCollection(ArrayList::new));
        double whitelistedWeights = whitelistIndices.stream().mapToDouble(weights::get).sum();
        double choice = RNG.nextDouble() * (whitelistedWeights);
        for (int id : whitelistIndices) {
            choice -= weights.get(id);
            if (choice <= 0)
                return values.get(id);
        }
        if (whitelistIndices.size() == 0)
            return null;
        else
            return values.get(whitelistIndices.get(whitelistIndices.size() - 1));
    }
}

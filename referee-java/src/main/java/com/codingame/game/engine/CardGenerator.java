package com.codingame.game.engine;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.lang.reflect.Type;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Random;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import com.google.common.reflect.TypeToken;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;


public class CardGenerator
{
    static class Property {
        public final String name;
        public final double weight;
        public final double multCost;
        public final double addCost;

        public Property(String name, double weight, double multCost, double addCost) {
            this.name = name;
            this.weight = weight;
            this.multCost = multCost;
            this.addCost = addCost;
        }
    }

    static class PropertyChoiceGenerator {
        private final List<Property> values;
        private final double sumOfWeights;
        private final Random RNG;

        public PropertyChoiceGenerator(Random originalRNG, List<Property> values) {
            List<Integer> sortedIndices = IntStream.range(0, values.size())
                    .boxed().sorted(Comparator.comparingDouble(i -> values.get(i).weight))
                    .collect(Collectors.toList());
            this.values = sortedIndices.stream().map(values::get).collect(Collectors.toCollection(ArrayList::new));
            this.sumOfWeights = values.stream().mapToDouble(v -> v.weight).sum();
            this.RNG = new Random(originalRNG.nextInt());
        }

        public Property randomChoice() {
            double choice = RNG.nextDouble() * sumOfWeights;
            for (Property value : values) {
                choice -= value.weight;
                if (choice <= 0)
                    return value;
            }
            return values.get(values.size() - 1);
        }

        public Property randomChoiceWithBlacklist(List<String> blacklist) {
            List<Property> whitelist = values.stream().filter(p -> !blacklist.contains(p.name)).collect(Collectors.toCollection(ArrayList::new));
            double whitelistedWeights = whitelist.stream().mapToDouble(p -> p.weight).sum();
            double choice = RNG.nextDouble() * (whitelistedWeights);
            for (Property property : whitelist) {
                choice -= property.weight;
                if (choice <= 0)
                    return property;
            }
            return whitelist.get(whitelist.size() - 1);
        }
    }

    static class WeightedChoiceGenerator<T> {
        private final List<T> values;
        private final List<Double> weights;
        private final double sumOfWeights;
        private final Random RNG;

        public WeightedChoiceGenerator(Random originalRNG, List<T> values, List<Double> weights) {
            List<Integer> sortedIndices = IntStream.range(0, weights.size())
                    .boxed().sorted(Comparator.comparingDouble(weights::get))
                    .collect(Collectors.toList());
            this.values = sortedIndices.stream().map(values::get).collect(Collectors.toCollection(ArrayList::new));
            this.weights = sortedIndices.stream().map(weights::get).collect(Collectors.toCollection(ArrayList::new));
            this.sumOfWeights = weights.stream().mapToDouble(x -> x).sum();
            this.RNG = new Random(originalRNG.nextInt());
        }

        public WeightedChoiceGenerator(Random originalRNG, Map<T, Double> m) {
            this(originalRNG, new ArrayList<>(m.keySet()), new ArrayList<>(m.values()));
        }

        public T randomChoice() {
            double choice = RNG.nextDouble() * sumOfWeights;
            for (int i=0; i<values.size(); i++) {
                choice -= weights.get(i);
                if (choice <= 0)
                    return values.get(i);
            }
            return values.get(values.size() - 1);
        }
    }

    static class NormalDistributionGenerator {
        private final Random RNG;
        private final double mean;
        private final double std;

        public NormalDistributionGenerator(Random originalRNG, double mean, double std) {
            this.RNG = new Random(originalRNG.nextInt());
            this.mean = mean;
            this.std = std;
        }
        public double next() {
            return RNG.nextDouble() * std + mean;
        }
    }

    WeightedChoiceGenerator<String> typeGenerator;
    WeightedChoiceGenerator<String> manaGenerator;
    PropertyChoiceGenerator areaGenerator;
    WeightedChoiceGenerator<String> keywordCountGenerator;
    PropertyChoiceGenerator drawGenerator;
    PropertyChoiceGenerator keywordGenerator;
    PropertyChoiceGenerator myHealthChangeGenerator;
    PropertyChoiceGenerator oppHealthChangeGenerator;
    NormalDistributionGenerator bonusAttackGenerator;
    NormalDistributionGenerator bonusDefenseGenerator;

    public CardGenerator(Random RNG, String path) {
        Type mapType = new TypeToken<Map<String, Double>>(){}.getType();
        Type listType = new TypeToken<List<Property>>(){}.getType();
        BufferedReader br = new BufferedReader(new InputStreamReader(
                Objects.requireNonNull(ClassLoader.getSystemResourceAsStream(path)), StandardCharsets.UTF_8));
        JsonParser parser = new JsonParser();
        Gson gson = new Gson();
        JsonObject root = parser.parse(br).getAsJsonObject();

        typeGenerator = new WeightedChoiceGenerator<>(RNG, gson.fromJson(root.get("typeProbabilities"), mapType));
        manaGenerator = new WeightedChoiceGenerator<>(RNG, gson.fromJson(root.get("manaCurve"), mapType));
        areaGenerator = new PropertyChoiceGenerator(RNG, gson.fromJson(root.get("areaProbabilities"), listType));

        keywordCountGenerator = new WeightedChoiceGenerator<>(RNG, gson.fromJson(root.get("keywordNumberProbabilities"), mapType));
        keywordGenerator = new PropertyChoiceGenerator(RNG, gson.fromJson(root.get("keywordProbabilities"), listType));

        drawGenerator = new PropertyChoiceGenerator(RNG, gson.fromJson(root.get("drawProbabilities"), listType));
        myHealthChangeGenerator = new PropertyChoiceGenerator(RNG, gson.fromJson(root.get("myHealthProbabilities"), listType));
        oppHealthChangeGenerator = new PropertyChoiceGenerator(RNG, gson.fromJson(root.get("oppHealthProbabilities"), listType));

        bonusAttackGenerator = new NormalDistributionGenerator(RNG,
                Double.parseDouble(root.getAsJsonObject("bonusAttackDistribution").get("mean").getAsString()),
                Double.parseDouble(root.getAsJsonObject("bonusAttackDistribution").get("std").getAsString()));
        bonusDefenseGenerator = new NormalDistributionGenerator(RNG,
                Double.parseDouble(root.getAsJsonObject("bonusDefenseDistribution").get("mean").getAsString()),
                Double.parseDouble(root.getAsJsonObject("bonusDefenseDistribution").get("std").getAsString()));
    }

    static private double changeMana(double mana, Property prop) {
        return mana * prop.multCost - prop.addCost;
    }
    static private double reverseChangeMana(double mana, Property prop) {
        return (mana + prop.addCost) / prop.multCost;
    }

    public Card genCard(int id) {
        String type = typeGenerator.randomChoice();
        double mana = Integer.parseInt(manaGenerator.randomChoice());
        int cost = (int) mana;

        Property area = areaGenerator.randomChoice();
        mana = changeMana(mana, area);

        int count = Integer.parseInt(keywordCountGenerator.randomChoice());
        List<String> keywordsList = new ArrayList<>();
        for (int i=0; i<count; i++) {
            Property newKeyword = keywordGenerator.randomChoiceWithBlacklist(keywordsList);
            mana = changeMana(mana, newKeyword);
            if (mana < 0) {
                mana = reverseChangeMana(mana, newKeyword);
                break;
            }
            keywordsList.add(newKeyword.name);
        }

        String keywords =
                (keywordsList.contains("breakthrough") ? "B" : "-") +
                (keywordsList.contains("charge") ? "C" : "-") +
                (keywordsList.contains("drain") ? "D" : "-") +
                (keywordsList.contains("guard") ? "G" : "-") +
                (keywordsList.contains("lethal") ? "L" : "-") +
                (keywordsList.contains("ward") ? "W" : "-");

        Property draw = drawGenerator.randomChoice();
        mana = changeMana(mana, draw);
        if (mana < 0) {
            mana = reverseChangeMana(mana, draw);
            draw = null;
        }
        Property myHealthChange = myHealthChangeGenerator.randomChoice();
        mana = changeMana(mana, myHealthChange);
        if (mana < 0) {
            mana = reverseChangeMana(mana, myHealthChange);
            myHealthChange = null;
        }
        Property oppHealthChange = oppHealthChangeGenerator.randomChoice();
        mana = changeMana(mana, oppHealthChange);
        if (mana < 0) {
            mana = reverseChangeMana(mana, oppHealthChange);
            oppHealthChange = null;
        }

        int attack = (int)(mana+bonusAttackGenerator.next());
        int defense = (int)(mana+bonusDefenseGenerator.next());
        if (Objects.equals(type, "creature")) {
            attack = Math.max(attack, 0);
            defense = Math.max(defense, 1);
        } else {
            attack = Math.max(attack, 0);
            defense = Math.max(defense, 0);
        }

        if (Objects.equals(type, "itemRed") || Objects.equals(type, "itemBlue")) {
            attack *= -1;
            defense *= -1;
        }

        return new Card(new String[]{
                Integer.toString(id),
                "very creative temporary name",
                type,
                Integer.toString(cost),
                Integer.toString(attack),
                Integer.toString(defense),
                keywords,
                myHealthChange == null ? "0" : myHealthChange.name,
                oppHealthChange == null ? "0" : oppHealthChange.name,
                draw == null ? "0" : draw.name,
                area.name
        });
    }

    public void generateCardList() {
        for (int i=0; i<Constants.CARDS_IN_CONSTRUCTED; i++) {
            Card c = this.genCard(i);
            Constants.CARDSET.put(c.baseId, c);
        }
    }
}
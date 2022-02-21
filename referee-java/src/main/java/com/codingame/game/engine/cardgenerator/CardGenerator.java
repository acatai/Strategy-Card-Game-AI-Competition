package com.codingame.game.engine.cardgenerator;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.lang.reflect.Type;
import java.nio.charset.StandardCharsets;
import java.util.*;

import com.codingame.game.engine.Card;
import com.codingame.game.engine.Constants;

import com.google.common.reflect.TypeToken;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;


public class CardGenerator {
    private final WeightedChoiceGenerator<String> typeGenerator;
    private final WeightedChoiceGenerator<String> manaGenerator;
    private final PropertiesOrderGenerator<String> propertyOrderGenerator;
    private final PropertyChoiceGenerator areaGenerator;
    private final PropertyChoiceGenerator drawGenerator;
    private final KeywordsGenerator keywordsGenerator;
    private final PropertyChoiceGenerator myHealthChangeGenerator;
    private final PropertyChoiceGenerator oppHealthChangeGenerator;
    private final NormalDistributionGenerator bonusAttackGenerator;
    private final NormalDistributionGenerator bonusDefenseGenerator;

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

        propertyOrderGenerator = new PropertiesOrderGenerator<>(RNG,
                Arrays.asList("area", "keywords", "draw", "myHealthChange", "oppHealthChange"));

        keywordsGenerator = new KeywordsGenerator(
                new WeightedChoiceGenerator<>(RNG, gson.fromJson(root.get("keywordNumberProbabilities"), mapType)),
                new PropertyChoiceGenerator(RNG, gson.fromJson(root.get("keywordProbabilities"), listType)));

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

    public Card generateCard(int id) {
        String type = typeGenerator.randomChoice();
        double mana = Integer.parseInt(manaGenerator.randomChoice());

        CardBuilder builder = new CardBuilder(id, type, mana);

        for (String nextProperty : propertyOrderGenerator.shuffle()) {
            switch (nextProperty) {
                case "area":
                    builder.addProperty(nextProperty, areaGenerator.randomChoice());
                    break;
                case "draw":
                    builder.addProperty(nextProperty, drawGenerator.randomChoice());
                    break;
                case "myHealthChange":
                    builder.addProperty(nextProperty, myHealthChangeGenerator.randomChoice());
                    break;
                case "oppHealthChange":
                    builder.addProperty(nextProperty, oppHealthChangeGenerator.randomChoice());
                    break;
                case "keywords":
                    keywordsGenerator.generateKeywords(builder);
                    break;
                default:
                    throw new IllegalStateException("Unexpected value: " + nextProperty);
            }
        }
        builder.addAttackAndDefense(bonusAttackGenerator, bonusDefenseGenerator);
        return builder.createCard();
    }

    public void generateCardList() {
        for (int i = 0; i < Constants.CARDS_IN_CONSTRUCTED; i++) {
            Card c = this.generateCard(i);
            Constants.CARDSET.put(c.baseId, c);
        }
    }
}

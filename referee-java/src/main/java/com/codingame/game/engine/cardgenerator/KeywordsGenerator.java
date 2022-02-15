package com.codingame.game.engine.cardgenerator;

import java.util.ArrayList;
import java.util.List;

class KeywordsGenerator {
    private final WeightedChoiceGenerator<String> keywordCountGenerator;
    private final PropertyChoiceGenerator keywordGenerator;

    KeywordsGenerator(WeightedChoiceGenerator<String> keywordCountGenerator, PropertyChoiceGenerator keywordGenerator) {
        this.keywordCountGenerator = keywordCountGenerator;
        this.keywordGenerator = keywordGenerator;
    }

    void generateKeywords(CardBuilder builder) {
        int count = Integer.parseInt(keywordCountGenerator.randomChoice());
        List<Property> keywordsPropertiesList = new ArrayList<>();
        for (int i=0; i<count; i++) {
            Property newKeyword = keywordGenerator.randomChoiceWithBlacklist(keywordsPropertiesList);
            if (!builder.addProperty(newKeyword.getName(), newKeyword))
                break;
            keywordsPropertiesList.add(newKeyword);
        }
    }
}

/**
 * Auto-generated code below aims at helping you parse
 * the standard input according to the problem statement.
 **/

let players;
let allCards;
let cardsInMyHand;
let cardsOnBoard;
let cardsEnemys;

// game loop
while (true) {
    players = [];
    for (let i = 0; i < 2; i++) {
        var inputs = readline().split(' ');
        players[i] = {
            playerHealth: parseInt(inputs[0]),
            playerMana: parseInt(inputs[1]),
            playerDeck: parseInt(inputs[2]),
            playerRune: parseInt(inputs[3]),
            playerDraw: parseInt(inputs[4])
        };
    }
    var inputs = readline().split(' ');
    const opponentHand = parseInt(inputs[0]);
    const opponentActions = parseInt(inputs[1]);
    for (let i = 0; i < opponentActions; i++) {
        const cardNumberAndAction = readline();
    }

    allCards = [];
    cardsInMyHand = [];
    cardsOnBoard = [[], []];
    cardsEnemys = [[], []];
    const cardCount = parseInt(readline());
    for (let i = 0; i < cardCount; i++) {
        var inputs = readline().split(' ');
        let card = {
            cardNumber: parseInt(inputs[0]),
            instanceId: parseInt(inputs[1]),
            location: parseInt(inputs[2]),
            cardType: parseInt(inputs[3]),
            cost: parseInt(inputs[4]),
            attack: parseInt(inputs[5]),
            defense: parseInt(inputs[6]),
            abilities: inputs[7],
            myHealthChange: parseInt(inputs[8]),
            opponentHealthChange: parseInt(inputs[9]),
            cardDraw: parseInt(inputs[10]),
            lane: parseInt(inputs[11])
        };

        allCards.push(card);

        if (card.location === 0)
            cardsInMyHand.push(card);
        else if (card.location === 1) {
            cardsOnBoard[card.lane].push(card);
        }
        else {
            cardsEnemys[card.lane].push(card);
        }
    }

    // Write an action using print()
    // To debug: printErr('Debug messages...');

    if (isDraftPhase(cardCount))
        print(pickCard());
    else {
        print(getActions());
    }
}

function isDraftPhase(cardCount) {
    return cardCount === 3;
}

function pickCard() {
    let chosen = pickTheBestCard(allCards);
    if (chosen === null)
        return 'PICK 0';
    return `PICK ${chosen.index}`;
}

function pickTheBestCard(cards) {
    let chosen = null;
    for (let i = 0; i < cards.length; i++) {
        if (cards[i].cardType !== 0) continue; //TODO
        if (chosen === null ||
            (Math.abs(cards[i].attack - cards[i].defense) < Math.abs(chosen.card.attack - chosen.card.defense)))
            chosen = {
                card: cards[i],
                index: i
            };
    }

    return chosen;
}

function getActions() {
    let actions = '';
    let usedMana = 0;
    let cardsPlayable = getPlayableCards(usedMana);
    let laneId = cardsOnBoard[0].length < cardsOnBoard[1].length ? 0 : 1;
    while (cardsOnBoard[laneId].length < 3 && cardsPlayable.length > 0) {
        let chosen = choseTheBestCard(cardsPlayable);
        if (chosen !== null) {
            actions += `SUMMON ${chosen.instanceId} ${laneId}; `;
            usedMana += chosen.cost;
            // printErr(JSON.stringify(cardsInMyHand.map(card => card.instanceId)));
            // printErr('Reomve :', JSON.stringify(chosen));
            let index = cardsInMyHand.findIndex(el => el === chosen);
            cardsInMyHand.splice(index, 1);
            // printErr(JSON.stringify(cardsInMyHand.map(card => card.instanceId)));
            // printErr('-----------');
            if (chosen.abilities[1] === 'C')
                cardsOnBoard[laneId].push(chosen);
                chosen.lane = laneId;
        }
        cardsPlayable = getPlayableCards(usedMana);
        laneId = cardsOnBoard[0].length < cardsOnBoard[1].length ? 0 : 1;
    }

    for (let laneId = 0; laneId < 2; laneId++) {
        while (cardsOnBoard[laneId].length > 0) {
            let card = cardsOnBoard[laneId].pop();
            let targetId = getTarget(card);
            actions += `ATTACK ${card.instanceId} ${targetId}; `;
        }
    }

    return actions || 'PASS';
}

function getPlayableCards(usedMana) {
    return cardsInMyHand.filter(card => {
        return card.cost <= players[0].playerMana - usedMana
            && card.cardType === 0; //TODO
    });
}

function choseTheBestCard(cards) {
    let chosen = null;
    for (let i = 0; i < cards.length; i++) {
        if (cards[i].cardType !== 0) continue; //TODO
        if (chosen === null ||
            Math.abs(cards[i].attack - cards[i].defense) < Math.abs(chosen.attack - chosen.defense))
            chosen = cards[i]
    }

    return chosen;
}

function getTarget(attacker) {
    for (let card of cardsEnemys[attacker.lane]) {
        if (card.abilities[3] === 'G' && !card.isKilled) {
            if (attacker.attack >= card.defense || attacker.abilities[4] === 'L')
                card.isKilled = true;
            else
                card.defense -= attacker.attack;

            return card.instanceId;
        }
    }

    return -1;
}
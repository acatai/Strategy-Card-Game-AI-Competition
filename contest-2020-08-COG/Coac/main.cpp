#pragma clang diagnostic ignored "-Wmissing-noreturn"
#pragma GCC optimize("-O3")
#pragma GCC optimize("inline")
#pragma GCC optimize("omit-frame-pointer")
#pragma GCC optimize("unroll-loops")

#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <tuple>
#include <climits>
#include <chrono>

using namespace std;
using namespace std::chrono;


// #####################################################################################################################
// ######### GLOBALS ###################################################################################################
// #####################################################################################################################

high_resolution_clock::time_point roundStart;
bool no_attack = false;

// #####################################################################################################################
// ######### UTILS #####################################################################################################
// #####################################################################################################################

void trap() {
    *(int *) 0 = 0;
}

template<typename Enumeration>
auto as_integer(Enumeration const value)
-> typename std::underlying_type<Enumeration>::type {
    return static_cast<typename std::underlying_type<Enumeration>::type>(value);
}

double elapsed_time() {
    duration<double> time_span = duration_cast<duration<double>>(high_resolution_clock::now() - roundStart);
    return time_span.count() * 1000;
}

// #####################################################################################################################
// ######### CONSTANTS #################################################################################################
// #####################################################################################################################

constexpr int MAX_MONSTERS_BOARD = 6;
constexpr int MAX_MONSTERS_PER_LANE = 3;
constexpr int MAX_HAND = 8;
constexpr int TIME_LIMIT = 190;
constexpr int NUMBER_OF_CARDS = 160;


// #####################################################################################################################
// ######### CARD ######################################################################################################
// #####################################################################################################################

enum class CardType {
    Monster = 0, GreenItem = 1, RedItem = 2, BlueItem = 3
};

enum class CardLocation {
    PlayerHand = 0, PlayerBoard = 1, EnemyBoard = -1, Graveyard = -2, EnemyHand = -3
};

struct Card {
    friend ostream &operator<<(ostream &os, const Card &card) {
        os << "index: " << card.index << " attack: " << card.attack << " defense: " << card.defense
           << " location: " << as_integer(card.location) << " lane: " << card.lane;
        return os;
    }

    int id;
    int instanceId;
    int index;
    CardLocation location;
    int lane;
    CardType type;
    int cost;
    int attack;
    int defense;

    int playerHpChange;
    int enemyHpChange;
    int cardDraw;

    bool breakthrough = false;
    bool charge = false;
    bool drain = false;
    bool guard = false;
    bool lethal = false;
    bool ward = false;

    bool attacked = false;
    bool canAttack = true;

    bool passed = false;

    int monsterEval() {
        int score = 0;
        if (attack > 0) {
            score += (defense + attack * 2 + ward * attack + lethal * 4) * 5;
            score += 20;
        }
        score += guard * 9;

        return score;
    }
};

// #####################################################################################################################
// ######### PLAYER ####################################################################################################
// #####################################################################################################################

struct Player {
    int hp;
    int mana;
    int handCount;
    int cardsToDraw;
    int cardsRemaining;
    int rune;
    CardLocation handLocation;
    CardLocation boardLocation;
    int guardsCount;
    int guardsLaneCount[2];
    int boardCount;
    int boardLaneCount[2];
    bool firstPlayer;
};

// #####################################################################################################################
// ######### ACTION ####################################################################################################
// #####################################################################################################################

enum class ActionType {
    Pass,
    Summon,
    Attack,
    Use,
    Pick,
    PassCard,
    Null
};

struct Action {
    Action();

    ActionType type = ActionType::Null;
    int index = -1;
    int targetIndex = -1;

    Action(ActionType type, int id, int targetId);

    Action(ActionType type, int id);

    void print(const vector<Card> &cards);

    void printErr(const vector<Card> &cards);

    friend ostream &operator<<(ostream &os, const Action &action);
};

void Action::print(const vector<Card> &cards) {
    int instanceId = (index == -1 ? -1 : cards[index].instanceId);
    int targetInstanceId = (targetIndex == -1 ? -1 : cards[targetIndex].instanceId);

    switch (type) {
        case ActionType::Pass:
            cout << "PASS";
            break;
        case ActionType::Attack:
            cout << "ATTACK " << instanceId << " " << targetInstanceId << ";";
            break;
        case ActionType::Summon:
            cout << "SUMMON " << instanceId << " " << targetIndex << ";";
            break;
        case ActionType::Use:
            cout << "USE " << instanceId << " " << targetInstanceId << ";";
            break;
        case ActionType::Pick:
            cout << "PICK " << index;
            break;
        case ActionType::PassCard:
            break;
        default:
            cerr << as_integer(type) << endl;
            cerr << "Error: Action not is not defined" << endl;
            trap();
    }
}

void Action::printErr(const vector<Card> &cards) {
    int instanceId = (index == -1 ? -1 : cards[index].instanceId);
    int targetInstanceId = (targetIndex == -1 ? -1 : cards[targetIndex].instanceId);

    switch (type) {
        case ActionType::Pass:
            cerr << "PASS";
            break;
        case ActionType::Attack:
            cerr << "ATTACK " << instanceId << " " << targetInstanceId << ";";
            break;
        case ActionType::Summon:
            cerr << "SUMMON " << instanceId << " " << targetIndex << ";";
            break;
        case ActionType::Use:
            cerr << "USE " << instanceId << " " << targetInstanceId << ";";
            break;
        case ActionType::Pick:
            cerr << "PICK " << index;
            break;
        case ActionType::PassCard:
            break;
        default:
            cerr << as_integer(type) << endl;
            cerr << "Error: Action not is not defined" << endl;
            trap();
    }
}

Action::Action(ActionType type, int id, int targetId) : type(type), index(id), targetIndex(targetId) {}

Action::Action(ActionType type, int id) : type(type), index(id) {}

ostream &operator<<(ostream &os, const Action &action) {
    os << "type: " << as_integer(action.type) << " index: " << action.index << " targetIndex: " << action.targetIndex;
    return os;
}

Action::Action() {
}

// #####################################################################################################################
// ######### STATE #####################################################################################################
// #####################################################################################################################

struct State {
    Player player;
    Player enemy;

    int turn = 0;

    vector<Card> cards;
    bool isDraft;

    vector<Action> legalActions;
    Action lastAction;

    void executeAction(const Action &action);

    void executeActions(const vector<Action> &actions);

    void attack(int index, int targetIndex);

    void summon(int index, int lane);

    void use(int index, int targetIndex);

    int evaluate();

    vector<Action> legalMoves();

    void passCard(int index);

    void swapPlayers();

    bool isEnemyTurn = false;
};

// Assume the action is valid
void State::executeAction(const Action &action) {
    lastAction = action;
    switch (action.type) {
        case ActionType::Pass:
            break;
        case ActionType::Attack:
            this->attack(action.index, action.targetIndex);
            break;
        case ActionType::Summon:
            this->summon(action.index, action.targetIndex);
            break;
        case ActionType::Use:
            this->use(action.index, action.targetIndex);
            break;
        case ActionType::Pick:
            break;
        case ActionType::PassCard:
            this->passCard(action.index);
            break;
        default:
            cerr << as_integer(action.type) << endl;
            cerr << "Error: Action not is not defined" << endl;
            trap();
    }

}

void State::executeActions(const vector<Action> &actions) {
    for (auto &action : actions) {
        executeAction(action);
    }
}

void State::attack(int index, int targetIndex) {
    Card &monster = cards[index];
    monster.attacked = true;

    if (targetIndex == -1) {
        enemy.hp -= monster.attack;
        return;
    }

    Card &target = cards[targetIndex];

    if (!monster.ward) {
        monster.defense -= target.attack;
        if ((target.lethal && target.attack > 0) || monster.defense <= 0) {
            monster.defense = 0;
            monster.location = CardLocation::Graveyard;
            if (monster.guard) {
                --player.guardsCount;
                --player.guardsLaneCount[monster.lane];
            }
            --player.boardCount;
            --player.boardLaneCount[monster.lane];
        }
    } else {
        monster.ward = target.attack == 0;
    }

    if (!target.ward) {
        target.defense -= monster.attack;
        if ((monster.lethal && monster.attack > 0) || target.defense <= 0) {
            if (monster.breakthrough) {
                enemy.hp -= min(target.defense, 0);
            }
            target.defense = 0;
            target.location = CardLocation::Graveyard;
            if (target.guard) {
                --enemy.guardsCount;
                --enemy.guardsLaneCount[target.lane];
            }
            --enemy.boardCount;
            --enemy.boardLaneCount[target.lane];
        }
        if (monster.drain) {
            player.hp += monster.attack;
        }
    } else {
        target.ward = monster.attack == 0;
    }
}

void State::summon(int index, int lane) {
    auto &card = cards[index];
    card.location = player.boardLocation;
    player.mana -= card.cost;
    player.cardsToDraw += card.cardDraw;
    player.hp += card.playerHpChange;
    enemy.hp += card.enemyHpChange;
    --player.handCount;

    ++player.boardCount;
    ++player.boardLaneCount[lane];

    card.canAttack = card.charge;
    card.lane = lane;

    if (card.guard) {
        ++player.guardsCount;
        ++player.guardsLaneCount[lane];
    }
}

void State::use(int index, int targetIndex) {
    auto &item = cards[index];

    --player.handCount;
    player.mana -= item.cost;
    player.cardsToDraw += item.cardDraw;
    item.location = CardLocation::Graveyard;

    if (targetIndex != -1) {
        auto &target = cards[targetIndex];

        if (item.type == CardType::GreenItem) {
            target.breakthrough = item.breakthrough || target.breakthrough;
            target.charge = item.charge || target.charge;
            if (target.charge) {
                target.canAttack = true;
            }
            target.drain = item.drain || target.drain;

            if (!target.guard && item.guard) {
                target.guard = true;
                ++player.guardsCount;
                ++player.guardsLaneCount[target.lane];
            }

            target.lethal = item.lethal || target.lethal;
            target.ward = item.ward || target.ward;
        } else {
            target.breakthrough = item.breakthrough && target.breakthrough;
            target.charge = !item.charge && target.charge;
            target.drain = !item.drain && target.drain;

            if (target.guard && item.guard) {
                target.guard = false;
                --enemy.guardsCount;
                --enemy.guardsLaneCount[target.lane];
            }

            target.lethal = !item.lethal && target.lethal;
            target.ward = !item.ward && target.ward;
        }

        target.attack = max(0, target.attack + item.attack);

        if (target.ward && item.defense < 0) {
            target.ward = false;
        } else {
            target.defense += item.defense;
        }

        if (target.defense <= 0) {
            target.defense = 0;
            target.location = CardLocation::Graveyard;
            --enemy.boardCount;
            --enemy.boardLaneCount[target.lane];
            if (target.guard) {
                --enemy.guardsCount;
                --enemy.guardsLaneCount[target.lane];
            }
        }

        player.hp += item.playerHpChange;
        enemy.hp += item.enemyHpChange;
    } else if (item.type == CardType::BlueItem) {
        player.hp += item.playerHpChange;
        enemy.hp += item.enemyHpChange;
        enemy.hp += item.defense;
    }
}

void State::passCard(int index) {
    auto &card = cards[index];
    card.passed = true;
}

int State::evaluate() {
    int score = 0;
    int enemySumAttack = 0;

    for (auto &card : cards) {
        if (card.location == player.boardLocation) {
            score += card.monsterEval();
        } else if (card.location == enemy.boardLocation) {
            score -= card.monsterEval();
            enemySumAttack += card.attack;
        }

        if (card.location == player.boardLocation) {
//            score += card.passed * 3;
        } else if (card.location == player.handLocation) {
            if (card.type != CardType::Monster) {
                score += card.passed * 21;
            }
        }
    }

    if (player.handCount + player.cardsToDraw <= MAX_HAND) {
        score += player.cardsToDraw * 5;
    }

    score += player.hp * 2;
    score -= enemy.hp * 2;

    if (player.hp < 5) {
        score -= 100;
    }

    if (enemy.hp <= 0) {
        score += 100000;
    } else if (player.hp <= 0) {
        score -= 100000;
    }

    return score;
}

vector<Action> State::legalMoves() {
    // Remove actions to avoid regenerating each time
    // TODO Fix the remove actions
//    draftChoicesSeed=-876250167555862261
//    shufflePlayer0Seed=-4422762594392573393
//    seed=4882437402899864600
//    shufflePlayer1Seed=2206163186945330453

    if (false && !legalActions.empty() && !isEnemyTurn) {
        if (lastAction.type == ActionType::Use) {
            bool defenderDead =
                    lastAction.targetIndex != -1 && cards[lastAction.targetIndex].location == CardLocation::Graveyard;
            bool defenderGuard = lastAction.targetIndex != -1 && cards[lastAction.targetIndex].guard;
//            bool guardRemoved = lastAction.targetIndex != -1 && !cards[lastAction.targetIndex].guard && cards[lastAction.index].guard; // TODO

            if (!(defenderGuard && defenderDead)) {
                if (defenderDead) {
                    legalActions.erase(remove_if(legalActions.begin(),
                                                 legalActions.end(),
                                                 [&](Action action) {
                                                     return (action.index == lastAction.index) ||
                                                            (action.targetIndex == lastAction.targetIndex) ||
                                                            ((action.type == ActionType::Summon ||
                                                              action.type == ActionType::Use) &&
                                                             cards[action.index].cost > player.mana);
                                                 }), legalActions.end());
                } else {
                    legalActions.erase(remove_if(legalActions.begin(),
                                                 legalActions.end(),
                                                 [&](Action action) {
                                                     return (action.index == lastAction.index) ||
                                                            ((action.type == ActionType::Summon ||
                                                              action.type == ActionType::Use) &&
                                                             cards[action.index].cost > player.mana);
                                                 }), legalActions.end());
                }
                return legalActions;
            }

        } else if (lastAction.type == ActionType::Attack) {
            // TODO ward lose, ward item
            // TODO dead can summon
            bool defenderDead =
                    lastAction.targetIndex != -1 && cards[lastAction.targetIndex].location == CardLocation::Graveyard;
            bool attackerDead = cards[lastAction.index].location == CardLocation::Graveyard;

            bool defenderGuard = lastAction.targetIndex != -1 && cards[lastAction.targetIndex].guard;

            if (!defenderGuard || !defenderDead) {
                if (defenderDead && !attackerDead) {
                    legalActions.erase(remove_if(legalActions.begin(),
                                                 legalActions.end(),
                                                 [&](Action action) {
                                                     return (action.index == lastAction.index) ||
                                                            (action.targetIndex == lastAction.targetIndex);
                                                 }), legalActions.end());
                } else if (defenderDead && attackerDead) {
                    legalActions.erase(remove_if(legalActions.begin(),
                                                 legalActions.end(),
                                                 [&](Action action) {
                                                     return (action.index == lastAction.index) ||
                                                            (action.targetIndex == lastAction.targetIndex) ||
                                                            (action.targetIndex == lastAction.index);
                                                 }), legalActions.end());
                } else if (!defenderDead && attackerDead) {
                    legalActions.erase(remove_if(legalActions.begin(),
                                                 legalActions.end(),
                                                 [&](Action action) {
                                                     return (action.index == lastAction.index) ||
                                                            (action.targetIndex == lastAction.index);
                                                 }), legalActions.end());
                } else if (!defenderDead && !attackerDead) {
                    legalActions.erase(remove_if(legalActions.begin(),
                                                 legalActions.end(),
                                                 [&](Action action) {
                                                     return (action.index == lastAction.index);
                                                 }), legalActions.end());
                }


//                    cerr << "---------" << endl;
//                    cerr << lastAction << endl;
//                    cerr << "defenderDead: " << defenderDead << " attackerDead: " << attackerDead << " defenderGuard: "
//                         << defenderGuard << " " << endl;

                return legalActions;
            } else if (lastAction.type == ActionType::Summon && !cards[lastAction.index].charge) { // TODO item
                legalActions.erase(remove_if(legalActions.begin(),
                                             legalActions.end(),
                                             [&](Action action) {
                                                 return (action.index == lastAction.index) ||
                                                        ((action.type == ActionType::Summon ||
                                                          action.type == ActionType::Use) &&
                                                         cards[action.index].cost > player.mana);
                                             }), legalActions.end());
                return legalActions;
            }
        }
    }
    vector<Action> actions;

    for (auto &card1 : cards) {
        if (card1.passed) {
            continue;
        }

        // Check for monster attacks
        if (card1.location == player.boardLocation && card1.attack > 0 && card1.canAttack && !card1.attacked) {
            for (auto &enemyMonster : cards) {
                if (enemyMonster.location != enemy.boardLocation || enemyMonster.lane != card1.lane) {
                    continue;
                }
                if (enemy.guardsLaneCount[card1.lane] > 0) {
                    if (enemyMonster.guard) {
                        actions.emplace_back(ActionType::Attack, card1.index, enemyMonster.index);
                    }
                } else {
                    actions.emplace_back(ActionType::Attack, card1.index, enemyMonster.index);
                }
            }

            if (isEnemyTurn && enemy.guardsLaneCount[card1.lane] == 0) {
                actions.emplace_back(ActionType::Attack, card1.index, -1);
            }

            actions.emplace_back(ActionType::PassCard, card1.index);

            // Check for spells and summon
        } else if (card1.location == player.handLocation && card1.cost <= player.mana) {

            if (card1.type == CardType::Monster) {
                if (player.boardLaneCount[0] < MAX_MONSTERS_PER_LANE) {
                    actions.emplace_back(ActionType::Summon, card1.index, 0);
                }

                if (player.boardLaneCount[1] < MAX_MONSTERS_PER_LANE) {
                    actions.emplace_back(ActionType::Summon, card1.index, 1);
                }
            } else if (card1.type == CardType::GreenItem) {
                for (auto &allyMonster : cards) {
                    if (allyMonster.location != player.boardLocation) {
                        continue;
                    }
                    if (allyMonster.attacked) {
                        continue;
                    }

                    actions.emplace_back(ActionType::Use, card1.index, allyMonster.index);
                }
            } else if (card1.type == CardType::RedItem) {
                for (auto &enemyMonster : cards) {
                    if (enemyMonster.location != enemy.boardLocation ||
                        (enemyMonster.attack == 0 && !enemyMonster.guard)) {
                        continue;
                    }

                    // Staff of Suppression or Rootkin Ritual
                    if (card1.id == 142 || card1.id == 149) {
                        if (!enemyMonster.breakthrough && !enemyMonster.drain && !enemyMonster.guard &&
                            !enemyMonster.lethal && !enemyMonster.ward) {
                            continue;
                        }
                        // Pierce Armour
                    } else if (card1.id == 143) {
                        if (!enemyMonster.guard) {
                            continue;
                        }
                        // Decimate
                    } else if (card1.id == 151) {
                        if (enemyMonster.attack < 4 && enemyMonster.defense < 4 && !enemyMonster.ward &&
                            !enemyMonster.lethal && !enemyMonster.guard) {
                            continue;
                        }
                    }
                    actions.emplace_back(ActionType::Use, card1.index, enemyMonster.index);
                }
            } else if (card1.type == CardType::BlueItem) {
                for (auto &enemyMonster : cards) {
                    if (enemyMonster.location != enemy.boardLocation ||
                        (enemyMonster.attack == 0 && !enemyMonster.guard)) {
                        continue;
                    }

                    if (card1.defense == 0) {
                        continue;
                    }

                    actions.emplace_back(ActionType::Use, card1.index, enemyMonster.index);
                }

                actions.emplace_back(ActionType::Use, card1.index, -1);
            }
            actions.emplace_back(ActionType::PassCard, card1.index);
        }
    }

    legalActions = actions;

    return actions;
}

void State::swapPlayers() {
    auto temp = player;
    player = enemy;
    enemy = temp;

    lastAction.type = ActionType::Null;

    isEnemyTurn = !isEnemyTurn;
}


// #####################################################################################################################
// ######### AGENT #####################################################################################################
// #####################################################################################################################


struct Agent {
    State state;
    vector<Action> actions;
    int leaf = 0;
    int manaCurve[13] = {0};
    int monsterCardsCount = 0;
    int greenCardsCount = 0;
    int redCardsCount = 0;
    int blueCardsCount = 0;


    void read();

    void readPlayersInfo();

    void readCards();

    void think();

    void draft();

    int hardcodedDraft();

    int evalDraft();

    int evalCardDraft(const Card &card);

    void allAttackEnemyPlayer(vector<Action> &actions);

    bool checkLethal(State &state);

    void play();

    int bruteForce(State root, int depth, Action &bestAction, int alpha);

    int bruteForceLeaf(State &root, Action &bestAction, int alpha);

    int runBruteForce(State root, int depth, vector<Action> &bestActions, int alpha);

    int randomSearch(const State &root, vector<Action> &bestActions);

    int enemyRandomSearch(const State &root);

    void benchmark();

    void print();
};


void Agent::read() {
    if (!state.isDraft)
        state.turn++;
    state.lastAction.type = ActionType::Null;
    this->readPlayersInfo();
    this->readCards();
    state.isDraft = state.player.mana == 0;
}

void Agent::readPlayersInfo() {
    Player *players[2] = {&state.player, &state.enemy};
    for (auto &player : players) {
        int playerHealth;
        int playerMana;
        int playerDeck;
        int playerRune;
        int playerDraw;
        cin >> playerHealth >> playerMana >> playerDeck >> playerRune >> playerDraw;
        cin.ignore();

        player->hp = playerHealth;
        player->mana = playerMana;
        player->cardsRemaining = playerDeck;
        player->rune = playerRune / 5;
    }

    if (state.isDraft) {
        state.player.firstPlayer = state.player.cardsRemaining == state.enemy.cardsRemaining;
        state.enemy.firstPlayer = !state.player.firstPlayer;
    }

    state.player.handLocation = CardLocation::PlayerHand;
    state.player.boardLocation = CardLocation::PlayerBoard;

    state.enemy.handLocation = CardLocation::EnemyHand;
    state.enemy.boardLocation = CardLocation::EnemyBoard;

    int opponentHand;
    int opponentActions;
    cin >> opponentHand >> opponentActions;
    cin.ignore();

    for (int i = 0; i < opponentActions; i++) {
        string cardNumberAndAction;
        getline(cin, cardNumberAndAction);
    }

    state.enemy.handCount = opponentHand;

    state.player.cardsToDraw = 0;
    state.player.cardsToDraw = 0;
}

void Agent::readCards() {
    state.cards.clear();
    state.enemy.boardCount = 0;
    state.enemy.boardLaneCount[0] = 0;
    state.enemy.boardLaneCount[1] = 0;
    state.enemy.guardsCount = 0;
    state.enemy.guardsLaneCount[0] = 0;
    state.enemy.guardsLaneCount[1] = 0;
    state.enemy.handCount = 0;

    state.player.boardCount = 0;
    state.player.boardLaneCount[0] = 0;
    state.player.boardLaneCount[1] = 0;
    state.player.guardsCount = 0;
    state.player.guardsLaneCount[0] = 0;
    state.player.guardsLaneCount[1] = 0;
    state.player.handCount = 0;

    int cardCount;
    cin >> cardCount;
    cin.ignore();
    for (int i = 0; i < cardCount; i++) {
        state.cards.emplace_back();
        Card &card = state.cards.back();

        int cardNumber;
        int instanceId;
        int location;
        int cardType;
        int cost;
        int attack;
        int defense;
        string abilities;
        int myHealthChange;
        int opponentHealthChange;
        int cardDraw;
        int lane;
        cin >> cardNumber >> instanceId >> location >> cardType >> cost >> attack >> defense >> abilities
            >> myHealthChange >> opponentHealthChange >> cardDraw >> lane;
        cin.ignore();

        card.id = cardNumber;
        card.index = i;
        card.instanceId = instanceId;
        card.location = (CardLocation) location;
        card.type = (CardType) cardType;
        card.cost = cost;
        card.attack = attack;
        card.defense = defense;
        card.lane = lane;

        for (char &ability : abilities) {
            if (ability == 'B') {
                card.breakthrough = true;
            } else if (ability == 'C') {
                card.charge = true;
            } else if (ability == 'D') {
                card.drain = true;
            } else if (ability == 'G') {
                card.guard = true;
            } else if (ability == 'L') {
                card.lethal = true;
            } else if (ability == 'W') {
                card.ward = true;
            }
        }

        if (card.type == CardType::Monster) {
            if (card.location == state.player.boardLocation) {
                ++state.player.boardCount;
                ++state.player.boardLaneCount[card.lane];
            } else if (card.location == state.enemy.boardLocation) {
                ++state.enemy.boardCount;
                ++state.enemy.boardLaneCount[card.lane];
            }
        }

        card.playerHpChange = myHealthChange;
        card.enemyHpChange = opponentHealthChange;
        card.cardDraw = cardDraw;

        if (card.type == CardType::Monster && card.guard) {
            if (card.location == state.player.boardLocation) {
                ++state.player.guardsCount;
                ++state.player.guardsLaneCount[card.lane];
            } else if (card.location == state.enemy.boardLocation) {
                ++state.enemy.guardsCount;
                ++state.enemy.guardsLaneCount[card.lane];
            }

        }

        if (card.location == state.player.handLocation) {
            ++state.player.handCount;
        }
    }
}

void Agent::think() {
    actions.clear();

    if (state.isDraft) {
        draft();
        double sum = 0;
        for (int i = 0; i < 13; ++i) {
            sum += manaCurve[i] * i;
        }
        double average = sum / 30.0;

        average = manaCurve[2];

        if (average > 6 && state.player.firstPlayer) {
            no_attack = false;
        } else if (average > 6 && !state.player.firstPlayer) {
            no_attack = true;
        } else {
            no_attack = false;
        }

        cerr << "average mana: " << average << endl;

    } else {
        play();
    }
}

int Agent::hardcodedDraft() {
    int sorted_cards1[] = {68, 7, 116, 65, 116, 151, 69, 48, 53, 51, 44, 67, 29, 18, 84, 18, 158, 28, 64, 80, 33, 85,
                           32, 147, 103, 37, 54, 52, 50, 99, 23, 87, 66, 81, 148, 88, 150, 121, 82, 95, 115, 133, 152,
                           19, 109, 157, 105, 3, 75, 96, 114, 9, 106, 144, 129, 128, 17, 128, 12, 11, 145, 15, 21, 8,
                           134, 155, 141, 70, 90, 135, 104, 41, 112, 61, 5, 97, 73, 26, 73, 6, 36, 86, 77, 83, 13, 93,
                           93, 93, 149, 59, 159, 74, 94, 38, 98, 126, 39, 30, 137, 100, 22, 62, 118, 22, 118, 1, 47, 71,
                           4, 91, 27, 56, 119, 101, 45, 16, 146, 58, 120, 142, 127, 25, 108, 132, 40, 14, 76, 125, 102,
                           131, 123, 2, 35, 130, 107, 43, 63, 31, 138, 124, 154, 78, 46, 24, 10, 136, 113, 60, 57, 92,
                           55, 117, 55, 153, 20, 156, 143, 110, 160, 140};
    int sorted_cards2[] = {68, 7, 65, 49, 116, 69, 51, 151, 53, 51, 44, 67, 29, 139, 28, 84, 28, 158, 64, 80, 33, 85,
                           32, 147, 103, 37, 50, 54, 50, 99, 23, 87, 66, 81, 148, 88, 150, 121, 82, 95, 115, 133, 152,
                           19, 109, 157, 105, 3, 96, 75, 114, 9, 106, 144, 129, 17, 111, 128, 12, 15, 11, 145, 21, 8,
                           134, 155, 141, 70, 90, 135, 104, 112, 41, 61, 5, 97, 26, 34, 73, 86, 6, 86, 83, 77, 89, 13,
                           79, 93, 59, 149, 159, 74, 94, 38, 126, 98, 39, 30, 100, 62, 137, 122, 22, 72, 118, 1, 47, 71,
                           4, 91, 56, 27, 119, 101, 45, 146, 16, 120, 58, 142, 25, 127, 108, 132, 40, 14, 76, 125, 102,
                           123, 131, 2, 35, 130, 107, 43, 63, 31, 138, 124, 154, 78, 46, 24, 10, 136, 113, 60, 57, 92,
                           117, 55, 42, 153, 20, 156, 143, 110, 160, 140};
    int sorted_cards1Monster[] = {68, 7, 65, 49, 116, 69, 151, 48, 53, 51, 44, 67, 29, 139, 84, 18, 158, 28, 64, 80, 33,
                                  85, 32, 147, 103, 37, 54, 52, 50, 99, 23, 87, 66, 81, 148, 88, 82, 150, 82, 95, 115,
                                  133, 152, 19, 109, 157, 105, 3, 75, 96, 114, 9, 106, 144, 129, 17, 111, 128, 12, 11,
                                  145, 15, 21, 8, 134, 155, 141, 70, 90, 135, 104, 41, 112, 61, 5, 97, 26, 34, 73, 6,
                                  36, 86, 77, 83, 13, 89, 79, 93, 149, 59, 159, 74, 94, 38, 98, 126, 39, 30, 137, 100,
                                  62, 122, 22, 72, 118, 1, 47, 71, 4, 91, 27, 56, 119, 101, 45, 16, 146, 58, 120, 142,
                                  127, 25, 108, 132, 40, 14, 76, 131, 125, 131, 123, 2, 35, 130, 107, 43, 63, 31, 138,
                                  124, 154, 78, 46, 24, 10, 136, 113, 60, 57, 92, 117, 42, 55, 156, 153, 156, 143, 110,
                                  160, 140};
    int sorted_cards2Monster[] = {68, 7, 116, 65, 116, 69, 151, 48, 53, 51, 44, 67, 29, 139, 84, 18, 158, 28, 64, 80,
                                  33, 85, 32, 147, 103, 37, 54, 52, 50, 99, 23, 87, 66, 81, 148, 88, 150, 121, 82, 95,
                                  115, 133, 152, 19, 109, 157, 105, 3, 75, 96, 114, 9, 106, 144, 129, 17, 111, 128, 12,
                                  15, 11, 145, 21, 8, 134, 155, 141, 70, 90, 135, 104, 112, 41, 61, 5, 97, 26, 34, 73,
                                  6, 36, 86, 77, 83, 89, 13, 79, 93, 59, 149, 159, 74, 94, 38, 126, 98, 39, 30, 100, 62,
                                  137, 122, 22, 72, 118, 1, 47, 71, 4, 91, 56, 27, 119, 101, 45, 146, 16, 120, 58, 142,
                                  25, 127, 108, 132, 40, 14, 76, 125, 102, 123, 131, 2, 35, 130, 107, 43, 63, 31, 138,
                                  124, 154, 78, 46, 24, 10, 136, 113, 60, 57, 92, 117, 55, 42, 153, 20, 156, 143, 110,
                                  160, 140};
    auto total = (float) (monsterCardsCount + greenCardsCount + blueCardsCount + redCardsCount);
    if ((float) monsterCardsCount / total < 0.4) {
        copy(begin(sorted_cards1Monster), end(sorted_cards1Monster), begin(sorted_cards1));
        copy(begin(sorted_cards2Monster), end(sorted_cards2Monster), begin(sorted_cards2));
    }

    auto sorted_cards = sorted_cards1;
    if (!state.player.firstPlayer) {
        sorted_cards = sorted_cards2;
    }

    int index = -1;
    int bestIndex = -1;
    int bestRank = INT_MAX;
    for (auto &card : state.cards) {
        ++index;
        for (int cardRank = 0; cardRank < NUMBER_OF_CARDS; ++cardRank) {
            auto card_id = sorted_cards[cardRank];
            if (card_id == card.id && cardRank < bestRank) {
                bestRank = cardRank;
                bestIndex = index;
            }
        }
    }
    return bestIndex;
}

int Agent::evalDraft() {
    int index = -1;
    int bestIndex = -1;
    float bestScore = INT_MIN;
    for (const auto &card : state.cards) {
        ++index;
        float score = evalCardDraft(card);
        cerr << "card score: " << score << endl;
        if (score > bestScore) {
            bestScore = score;
            bestIndex = index;
        }
    }

    if (bestIndex == -1) {
        bestIndex = 1;
    }

    return bestIndex;
}

void Agent::draft() {
    cerr << "---- DRAFT PHASE ----" << endl;

    int bestIndex = hardcodedDraft();

    const Card &card = state.cards[bestIndex];
    ++manaCurve[card.cost];
    if (card.type == CardType::Monster) {
        ++monsterCardsCount;
    } else if (card.type == CardType::GreenItem) {
        ++greenCardsCount;
    } else if (card.type == CardType::RedItem) {
        ++redCardsCount;
    } else if (card.type == CardType::BlueItem) {
        ++blueCardsCount;
    }

    for (int i = 0; i < 13; ++i) {
        cerr << "mana " << i << ": " << manaCurve[i] << endl;
    }

    actions.emplace_back(ActionType::Pick, bestIndex);
}

int Agent::bruteForceLeaf(State &root, Action &bestAction, int alpha) {
    constexpr int ENEMY_DEPTH = 1;

    bestAction.type = ActionType::Null;
    root.swapPlayers();

    if (root.isEnemyTurn) {
        vector<Action> temp;
        return runBruteForce(root, ENEMY_DEPTH, temp, alpha);
    }

    ++leaf;

    return -root.evaluate();
}

int Agent::bruteForce(State root, int depth, Action &bestAction, int alpha) {
    bestAction.type = ActionType::Null;

    if (depth <= 0) {
        return bruteForceLeaf(root, bestAction, alpha);
    }

    vector<Action> legalActions = root.legalMoves();

    if (legalActions.empty()) {
        return bruteForceLeaf(root, bestAction, alpha);
    }

    if (legalActions.size() >= 35) {
        --depth;
    }

    if (elapsed_time() >= TIME_LIMIT) {
        depth = 1;
    }

    int bestScore = INT_MIN;

    for (auto &gameAction : legalActions) {
        State newState = root;
        newState.executeAction(gameAction);

        Action action;

        int score = bruteForce(newState, depth - 1, action, alpha);

        if (root.isEnemyTurn && alpha > -score) {
            bestAction = gameAction;
            return score;
        }

        if (!root.isEnemyTurn) {
            alpha = alpha > score ? alpha : score;
        }

        if (score > bestScore) {
            bestScore = score;
            bestAction = gameAction;
        }
    }

    return bestScore;
}

int Agent::runBruteForce(State root, int depth, vector<Action> &bestActions, int alpha) {
    Action bestAction;

    bruteForce(root, depth, bestAction, alpha);

    if (root.isEnemyTurn && checkLethal(root)) {
        return -100000;
    }

    while (bestAction.type != ActionType::Null) {
        if (bestAction.type != ActionType::PassCard) {
            bestActions.push_back(bestAction);
        }
        root.executeAction(bestAction);

        // DEBUG
//        if (!root.isEnemyTurn && bestAction.type != ActionType::PassCard) {
//            auto legalActions = root.legalMoves();
//            for (auto action : legalActions) {
//                action.printErr(state.cards);
//                cerr << endl;
//            }
//            cerr <<"-------" << endl;
//        }

        if (!root.isEnemyTurn && checkLethal(root)) {
            cerr << "runBruteForce checkLethal" << endl;
            allAttackEnemyPlayer(bestActions);
            return 100000;
        } else if (root.isEnemyTurn && checkLethal(root)) {
            return -100000;
        }

        bruteForce(root, depth, bestAction, alpha);
    }

    if (root.isEnemyTurn) {
        root.swapPlayers();
    }

    return root.evaluate();
}


int Agent::randomSearch(const State &root, vector<Action> &bestActions) {
    int bestScore = INT_MIN;
    leaf = 0;
    while (true) {
        if (elapsed_time() >= TIME_LIMIT) {
            break;
        }

        State currentState = root;
        vector<Action> currentActions;

        while (true) {
            vector<Action> possibleActions = currentState.legalMoves();

            if (possibleActions.empty()) {
                break;
            }

            int rndIndex = static_cast<int>(rand() % possibleActions.size());
            const auto &action = possibleActions[rndIndex];

            currentState.executeAction(action);

            if (action.type != ActionType::PassCard) {
                currentActions.push_back(action);
            }
        }

        ++leaf;

        currentState.swapPlayers();
        auto score = enemyRandomSearch(currentState);
        if (score > bestScore) {
            bestScore = score;
            bestActions = currentActions;
        }

    }

    return bestScore;
}

int Agent::enemyRandomSearch(const State &root) {
    int minScore = INT_MAX;

    State temp = root;
    int movesCount = static_cast<int>(temp.legalMoves().size());

    for (int i = 0; i < movesCount * 1; ++i) {
        State currentState = root;

        while (true) {
            vector<Action> possibleActions = currentState.legalMoves();

            if (possibleActions.empty()) {
                break;
            }

            int rndIndex = static_cast<int>(rand() % possibleActions.size());
            const auto &action = possibleActions[rndIndex];

            currentState.executeAction(action);
        }

        currentState.swapPlayers();
        auto score = currentState.evaluate();
        if (score < minScore) {
            minScore = score;
        }

    }

    if (minScore == INT_MAX) {
        temp.swapPlayers();
        minScore = temp.evaluate();
    }

    return minScore;
}

void Agent::allAttackEnemyPlayer(vector<Action> &actions) {
    for (auto &card : state.cards) {
        if (card.location != CardLocation::PlayerBoard || card.attacked) {
            continue;
        }
        actions.emplace_back(ActionType::Attack, card.index, -1);
    }
}

bool Agent::checkLethal(State &state) {
    if (state.enemy.guardsCount != 0) {
        return false;
    }

    int sumAttack = 0;

    for (auto &card : state.cards) {
        if (card.location != state.player.boardLocation || card.attacked || !card.canAttack) {
            continue;
        }

        sumAttack += card.attack;
    }

    if (sumAttack >= state.enemy.hp) {
        return true;
    }

    int nextNumberRune = (state.enemy.hp - sumAttack) / 5;
    int cardToDraw = 1;
    if (nextNumberRune < state.enemy.rune) {
        cardToDraw += state.enemy.rune - nextNumberRune;
    }

    int overdraw = cardToDraw - state.enemy.cardsRemaining;
    // cerr << "overdraw: " << overdraw << " nextNumberRune: " << nextNumberRune << " cardToDraw: " << cardToDraw << " state.enemy.rune: " << state.enemy.rune << endl;
    return overdraw > 0 && overdraw >= nextNumberRune;
}

void Agent::play() {

    // Debug
//    cerr << "state.enemy.guardsLaneCount[0]: " << state.enemy.guardsLaneCount[0] << endl;
//    cerr << "state.enemy.guardsLaneCount[1]: " << state.enemy.guardsLaneCount[1] << endl;
//    cerr << "state.enemy.boardLaneCount[0]: " << state.enemy.boardLaneCount[0] << endl;
//    cerr << "state.enemy.boardLaneCount[1]: " << state.enemy.boardLaneCount[1] << endl;
//    cerr << "state.enemy.guardsCount: " << state.enemy.guardsCount << endl;
//    cerr << "state.enemy.boardCount: " << state.enemy.boardCount << endl << endl;
//
//    cerr << "state.player.guardsLaneCount[0]: " << state.player.guardsLaneCount[0] << endl;
//    cerr << "state.player.guardsLaneCount[1]: " << state.player.guardsLaneCount[1] << endl;
//    cerr << "state.player.boardLaneCount[0]: " << state.player.boardLaneCount[0] << endl;
//    cerr << "state.player.boardLaneCount[1]: " << state.player.boardLaneCount[1] << endl;
//    cerr << "state.player.guardsCount: " << state.player.guardsCount << endl;
//    cerr << "state.player.boardCount: " << state.player.boardCount << endl;
//
//    cerr << "---- ENEMY MONSTYER " << state.turn << "----" << endl;
//    for (auto &enemyMonster : state.cards) {
//        if (enemyMonster.location != CardLocation::EnemyBoard) {
//            continue;
//        }
//
//        cerr << enemyMonster << endl;
//    }
//
//    cerr << "---- PLAYERR MONSTYER " << state.turn << "----" << endl;
//
//    for (auto &enemyMonster : state.cards) {
//        if (enemyMonster.location != CardLocation::PlayerBoard) {
//            continue;
//        }
//
//        cerr << enemyMonster << endl;
//    }
//
//    cerr << "---- LEGAL ACTIONS " << state.turn << "----" << endl;

    vector<Action> legalActions = state.legalMoves();
    cerr << "legalActions: " << legalActions.size() << endl;
//    for (auto action : legalActions) {
//        action.printErr(state.cards);
//        cerr << endl;
//    }


    cerr << "---- PLAY PHASE TURN " << state.turn << "----" << endl;

    if (checkLethal(state)) {
        cerr << "CHECK LETHAL" << endl;
        allAttackEnemyPlayer(actions);
        return;
    }

    leaf = 0;
    int depth = 3;
    auto score = runBruteForce(state, depth, actions, INT_MIN);
//    auto score = randomSearch(state, actions);
    cerr << "score: " << score << endl;
    cerr << "leaf: " << leaf << endl;
    cerr << "actions: " << actions.size() << endl;
    state.executeActions(actions);

//    if(state.player.firstPlayer) {
//        allAttackEnemyPlayer(actions);
//        return;
//    }

    if (!no_attack) {
        allAttackEnemyPlayer(actions);
        return;
    }

//    if (state.enemy.cardsRemaining < 3 || state.enemy.handCount >= MAX_HAND - 1 ||
//        (state.player.boardCount > state.enemy.boardCount + 3 &&
//         state.player.boardCount + state.player.handCount > state.enemy.boardCount + state.enemy.handCount + 2)) {
//        allAttackEnemyPlayer(actions);
//        no_attack = false;
//        return;
//    }
//
//    if ((state.enemy.handCount > 1 &&
//         (state.player.handCount < state.enemy.handCount || state.player.boardCount < MAX_MONSTERS_BOARD - 1))) {
//        return;
//    }

    allAttackEnemyPlayer(actions);
    no_attack = false;
}

void Agent::print() {
    if (actions.empty()) {
        cout << "PASS";
    } else {
        for (auto &action : actions) {
            action.print(state.cards);
        }
    }

    cout << endl;
}

int Agent::evalCardDraft(const Card &card) {
    int score = 0;
    if (card.cost == 0) {
        return INT_MIN;
    }
    score -= card.cost;
    score += (abs(card.attack) + abs(card.defense)) / card.cost;

    if (abs(card.attack) + abs(card.defense) > 0) {
        score += 2 * abs(card.attack) * abs(card.defense) / (abs(card.attack) + abs(card.defense)); // harmonic mean
    }

    if (card.type == CardType::Monster) {
        score += card.lethal * 4 + card.ward * 4 + card.guard * 2 + card.breakthrough + card.drain;
    } else if (card.type != CardType::GreenItem) {
        score += (abs(card.attack) + abs(card.defense));
    } else {
        score += 2 + card.ward * 5;
    }

    if (card.type == CardType::Monster && card.charge && card.lethal && card.attack > 0) {
        score += 4;
    }

    if (card.type == CardType::Monster && card.attack == 0) {
        score += -2;
    }

    score += card.cardDraw;

    return score;
}

void Agent::benchmark() {
    state.isDraft = false;

    state.player.mana = 10;
    state.enemy.mana = 10;

    state.player.hp = 30;
    state.enemy.hp = 30;

    state.player.handLocation = CardLocation::PlayerHand;
    state.player.boardLocation = CardLocation::PlayerBoard;

    state.enemy.handLocation = CardLocation::EnemyHand;
    state.enemy.boardLocation = CardLocation::EnemyBoard;

    state.enemy.boardCount = 6;
    state.enemy.guardsCount = 6;

    state.player.boardCount = 6;
    state.player.guardsCount = 6;

    state.player.handCount = 8;
    state.enemy.handCount = 8;


    for (int i = 0; i < MAX_MONSTERS_BOARD; ++i) {
        state.cards.emplace_back();
        Card &card = state.cards.back();
        card.location = state.player.boardLocation;
        card.type = CardType::Monster;
        card.attack = i;
        card.defense = i;
        card.guard = true;
        card.ward = true;
        card.canAttack = true;
        card.cost = 1;
        card.index = i;
    }

    for (int i = 0; i < MAX_MONSTERS_BOARD; ++i) {
        state.cards.emplace_back();
        Card &card = state.cards.back();
        card.location = state.enemy.boardLocation;
        card.type = CardType::Monster;
        card.attack = i;
        card.defense = i;
        card.guard = true;
        card.ward = true;
        card.canAttack = true;
        card.cost = 1;
        card.index = i + MAX_MONSTERS_BOARD;
    }


    for (int i = 0; i < MAX_HAND; ++i) {
        state.cards.emplace_back();
        Card &card = state.cards.back();
        card.location = state.player.handLocation;
        card.type = CardType::BlueItem;
        card.enemyHpChange = -1;
        card.attack = -1;
        card.defense = -1;
        card.ward = true;
        card.cost = 1;
        card.index = i + MAX_MONSTERS_BOARD * 2;
    }

    int sumLeaf = 0;
    int numberRun = 10;
    for (int j = 0; j < numberRun; ++j) {
        roundStart = high_resolution_clock::now();
        vector<Action> bestActions;
        leaf = 0;
        int score = runBruteForce(state, 5, bestActions, INT_MIN);

        sumLeaf += leaf;
        cerr << "leaf: " << leaf << " score: " << score << " time: " << elapsed_time() << "ms" << endl;
    }
    cerr << "meanLeaf: " << (float) sumLeaf / (float) numberRun << endl;
}

// #####################################################################################################################
// ######### MAIN ######################################################################################################
// #####################################################################################################################



int main() {
    Agent agent;
//    agent.benchmark();
    while (true) {
        agent.read();

        roundStart = high_resolution_clock::now();

        agent.think();

        cerr << elapsed_time() << "ms" << endl;

        agent.print();
    }
}
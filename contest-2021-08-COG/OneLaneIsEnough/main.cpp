#pragma GCC optimize("Ofast", "omit-frame-pointer" , "inline", "unroll-loops", "restrict")
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <cstdint>
#include <chrono>

using namespace std;

#define WHAT_TO_DO false
#define SHOW_EXPANDING_PHASES WHAT_TO_DO
#define SHOW_APPLY_ACTIONS WHAT_TO_DO
#define SHOW_TO_ACTIONS WHAT_TO_DO

std::chrono::high_resolution_clock::time_point _START;
#define TIME_NOW std::chrono::high_resolution_clock::now()
#define START_TIMER _START = TIME_NOW
#define TIME_ELAPSED std::chrono::duration_cast<std::chrono::milliseconds>(TIME_NOW - _START).count()

void trap() {
	exit(0);
}

//SUBMIT COMMENT. Changed best cards to the ones provided by ClosetAI. Also changed coefficients a little to make enemy creatures more threatening.
//SUBMIT RESULT: 4th place in gold. Mana curve is terrible. Too much high mana cost creatures.
//Enemy turn is not simulated. Coefficients are not tuned, only once checked.
//It is impossible to use two red cards in the same turn. (bug)

//SUBMIT COMMENT V2: dirty fix to draft. 50% of the time we pick according to tier list. 25% lowest cost card. 25% random card.
//RESULT: 29th place... Removing random card picks. Reverting to old tier list


/*


TODO 21.07
A lot depends on card order. It is not clear where to sort or not.

22.07
My idea is to never alter the order of cards on board or in hand (only by adding and removing).
We could sort them elsewhere if we need to, without altering GameState

*/

//static const int COMBINATIONS_SIZES[9];
//static const int(*COMBINATIONS[9])[8];

constexpr int nBits(uint8_t n) {
	int c = 0;
	while (n) {
		n &= (n - 1);
		c++;
	}
	return c;
}
constexpr uint8_t nextNbit(uint8_t number, int N) {
	do {
		number++;
	} while (nBits(number) != N);
	return number;
}

template<int MAX_SIZE, typename T>
struct Vector {
	string _name = "Vector";
	Vector() = default;
	Vector(string name) : _name(name) {}
	T data[MAX_SIZE];
	int size = 0;
	T& newItem() {
		if (size >= MAX_SIZE) {
			cerr << _name << " is full" << endl;
			trap();
		}
		return data[size++];
	}
	void deleteItem(const T& item) {
		int item_index = -1;
		for (int i = 0; i < size; i++) {
			if (data[i] == item) {
				item_index = i;
				break;
			}
		}
		if (item_index == -1) {
			cerr << "Item not in " << _name << " or " << _name << " is empty" << endl;
			trap();
		}
		std::swap(data[size - 1], data[item_index]);
		size--;
	}

	void deleteItem(int idx) {
		if (idx >= size) {
			cerr << '(' << _name << ") Index " << idx << " out of bounds" << endl;
		}
		deleteItem(data[idx]);
	}

	void clear() { size = 0; }

	T& operator [](int idx) {
		if (idx < 0 || idx >= size) {
			cerr << '(' << _name << ") Index " << idx << " out of bounds. Size=" << size << endl;
			trap();
		}
		return data[idx];
	}
};

enum class Ability : uint8_t {
	BREAKTHROUGH = 1,
	CHARGE = 2,
	DRAIN = 4,
	GUARD = 8,
	LETHAL = 16,
	WARD = 32
};

enum class Location {
	PLAYER_HAND = 0,
	PLAYER_BOARD = 1,
	ENEMY_BOARD = -1
};

enum class CardType {
	CREATURE = 0,
	GREEN_ITEM = 1,
	RED_ITEM = 2,
	BLUE_ITEM = 3
};

enum class Lane {
	LEFT = 0,
	RIGHT = 1
};

struct Card {
	Card() { clear(); instance_id = -1; }
	int number;
	int instance_id;
	Location location;
	CardType type;
	int cost;
	int attack;
	int defense;
	uint8_t abilities;
	int my_health_change;
	int opponent_health_change;
	int draw;
	Lane lane;

	int breakthrough_damage = 0; //how much damage should controller take (only check if card is a creature and if defense <= 0)
	bool can_attack_this_turn = false;
	bool passed_attack_or_use = false;
	bool canAttackThisTurn() const { return can_attack_this_turn && !passed_attack_or_use && attack > 0; }
	bool canAttackEnemyHeroThisTurn() const { return (can_attack_this_turn || passed_attack_or_use) && attack > 0; }
	bool canBePlayed() const { return !passed_attack_or_use; }
	void clear() { breakthrough_damage = 0; can_attack_this_turn = true; passed_attack_or_use = false; }

	static void useItemOnCreature(Card& item, Card& creature);
	static void resolveAttack(Card& creature1, Card& creature2);
	static void resolveBreakthrough(Card& attacking, Card& attacked);

	void useOn(Card& card);
	bool hasAbility(Ability a) const { return (uint8_t)a & abilities; }
	void removeAbility(Ability a) { abilities &= ~(uint8_t)a; }
	void addAbility(Ability a) { abilities |= (uint8_t)a; }
	void addAbilities(uint8_t mask) { abilities |= mask; }
	bool isCreature() const { return type == CardType::CREATURE; }
	bool hasWard() const { return hasAbility(Ability::WARD); }
	bool hasBreakthrough() const { return hasAbility(Ability::BREAKTHROUGH); }
	bool hasGuard() const { return hasAbility(Ability::GUARD); }
	bool hasCharge() const { return hasAbility(Ability::CHARGE); }
	bool hasLethal() const { return hasAbility(Ability::LETHAL); }
	bool hasDrain() const { return hasAbility(Ability::DRAIN); }
	void removeWard() { removeAbility(Ability::WARD); }
	void removeBreakthrough() { removeAbility(Ability::BREAKTHROUGH); }
	void removeGuard() { removeAbility(Ability::GUARD); }
	void removeCharge() { removeAbility(Ability::CHARGE); }
	void removeLethal() { removeAbility(Ability::LETHAL); }
	void removeDrain() { removeAbility(Ability::DRAIN); }
	void removeAbilities(uint8_t mask) { abilities &= ~mask; }
	bool isGreenItem() const { return type == CardType::GREEN_ITEM; }
	bool isBlueItem() const { return type == CardType::BLUE_ITEM; }
	bool isRedItem() const { return type == CardType::RED_ITEM; }
	bool isCreatureWithGuard() const { return isCreature() && hasGuard(); }
};

ostream& operator << (ostream& os, const Card& card) {
	os << "Card(instance_id=" << card.instance_id << ")";
	return os;
}

bool operator ==(const Card& a, const Card& b) {
	/* If I understand correctly, the instance_id has to be diffrent for two identical cards, but it can be equal to instance_id of diffrent card*/
	return a.number == b.number && a.instance_id == b.instance_id;
}

using Deck = Vector<30, Card>;
using PlayerHand = Vector<8, Card>;
using Board = Vector<6, Card>;

struct Player {
	int health; //the remaining HP of the player
	int mana; //the current maximum mana of the player
	int deck; //remaining cards in deck. During the Draft phase, the second player has less card in his deck than his opponent
	int rune; //the next remaining rune of a player
	int draw; // the additional number of drawn cards
};

ostream& operator << (ostream& os, const Player& p) {
	os << "Player(hp=" << p.health << ",mana=" << p.mana << ')';
	return os;
}

void Card::useOn(Card& card) {
	//attack target creature/player; use item on target
	if (this->isCreature()) {
		if (card.isCreature())
			Card::resolveAttack(*this, card);
		else //item
			Card::useItemOnCreature(card, *this);
	}
	else if (card.isCreature()) //item on creature
		Card::useItemOnCreature(*this, card);
	else {
		//item on item?
		cerr << "Tried to use item on item" << endl;
		trap();
	}
}

void Card::resolveBreakthrough(Card& attacker, Card& attacked) {
	attacked.breakthrough_damage = 0;
	if (attacker.isCreature() && attacker.hasBreakthrough() && attacked.isCreature() && !attacked.hasWard()) {
		if (attacked.defense < attacker.attack) {
			attacked.breakthrough_damage = attacker.attack - attacked.defense;
		}
	}
}

void Card::useItemOnCreature(Card& item, Card& creature) {
	if (item.type == CardType::GREEN_ITEM)
		creature.addAbilities(item.abilities);
	else //red and blue items
		creature.removeAbilities(item.abilities);
	if (creature.hasWard() && item.defense < 0) {
		//looks like all items that lower defense remove ward. Referee code: https://github.com/CodinGame/LegendsOfCodeAndMagic/blob/1aacfeafcf183b9e3bd79b037391e990b9a49749/src/main/java/com/codingame/game/engine/GameState.java#L430
		creature.removeWard();
	}
	else
		creature.defense += item.defense;
	creature.attack += item.attack;
	if (creature.attack < 0)
		creature.attack = 0;
}

void Card::resolveAttack(Card& a, Card& b) {
	if (a.hasWard()) {
		if (b.attack > 0)
			a.removeWard();
	}
	else {
		if (b.hasLethal() && b.attack > 0) {
			a.defense = 0;
		}
		else {
			a.defense -= b.attack;
		}
	}
	if (b.hasWard()) {
		if (a.attack > 0)
			b.removeWard();
	}
	else {
		if (a.hasLethal() && a.attack > 0) {
			b.defense = 0;
		}
		else {
			b.defense -= a.attack;
		}
	}
}
struct GameTreeAction;
struct GameState {
	// [0] - player, [1] - enemy
	Player _players[2];
	Board _boards[2]{ Board("Player board"), Board("Enemy board") };
	PlayerHand _player_hand{ PlayerHand("Player hand") };
	Deck _decks[2]{ Deck("Player deck"), Deck("Enemy deck") };
	int _current_player = 0;

	bool playingAsEnemy() const { return _current_player == 1; }
	Player& getPlayer() { return _players[_current_player]; }
	Player& getEnemy() { return _players[1 - _current_player]; }
	Board& getPlayerBoard() { return _boards[_current_player]; }
	Board& getEnemyBoard() { return _boards[1 - _current_player]; }
	PlayerHand& getPlayerHand();
	Deck& getPlayerDeck() { return _decks[_current_player]; }
	Deck& getEnemyDeck() { return _decks[1 - _current_player]; }
	void switchSides() /*swaps player and opponent. Used when simulating from enemy perspective */ { _current_player = 1 - _current_player; }
	void addCard(Card card);
	void addToDeck(Card card, bool players_deck);
	float evaluate();
	void clear(); //clears player's hand, and both boards

	void applyAction(GameTreeAction& action);

	bool enemyHasGuard(Lane lane);
	bool IHaveGuard(Lane lane);
	void attackEnemyWithAllCreatures();

	GameState fromAction(GameTreeAction& action);

	//void orderBoards(); //Sort both boards so that attacks can be resolved from left to right
	//void orderCardsInHand(); //from highest cost to lowest cost

	GameState copy() const { return *this; }

	void removeDeadMinions() {
		for (int i = 0; i < 2; i++)
			for (int j = _boards[i].size - 1; j >= 0; j--)
				if (_boards[i][j].defense <= 0)
					_boards[i].deleteItem(j);
	}
	bool playerHasGreenItems() {
		for (int i = 0; i < getPlayerHand().size; i++)
			if (getPlayerHand().data[i].isGreenItem())
				return true;
		return false;
	}
	bool playerHasRedItems() {
		for (int i = 0; i < getPlayerHand().size; i++)
			if (getPlayerHand().data[i].isRedItem())
				return true;
		return false;
	}
};

void GameState::clear() {
	_boards[0].clear(); _boards[1].clear(); _player_hand.clear();
	for (int i = 0; i < 2; i++) {
		for (int j = 0; j < _boards[i].size; j++) {
			_boards[i][j].clear();
			_boards[i][j].can_attack_this_turn = true; //minions on board can attack
		}
	}
}

void GameState::attackEnemyWithAllCreatures()
{
	bool guard_left = enemyHasGuard(Lane::LEFT), guard_right = enemyHasGuard(Lane::RIGHT);
	auto& board = getPlayerBoard();
	for (int i = 0; i < board.size; i++) {
		if (board[i].canAttackEnemyHeroThisTurn() && (board[i].lane == Lane::LEFT && !guard_left || board[i].lane == Lane::RIGHT && !guard_right)) {
			getEnemy().health -= board[i].attack;
			if (board[i].hasDrain())
				getPlayer().health += board[i].attack;
			board[i].can_attack_this_turn = false;
		}
	}
}
bool GameState::enemyHasGuard(Lane lane) {
	auto& board = getEnemyBoard();
	for (int i = 0; i < board.size; i++)
		if (board[i].hasGuard() && board[i].lane == lane)
			return true;
	return false;
}

bool GameState::IHaveGuard(Lane lane) {
	auto& board = getPlayerBoard();
	for (int i = 0; i < board.size; i++)
		if (board[i].hasGuard() && board[i].lane == lane)
			return true;
	return false;
}

PlayerHand& GameState::getPlayerHand() {
	if (_current_player == 1) {
		cerr << "Attempting to access player's from enemy's perspective" << endl;
		trap();
	}
	return _player_hand;
}

float evaluateMonster(const Card& monster) {
	float score = 0;
	score += monster.attack * (2 + monster.hasWard());
	score += monster.defense;
	score += 2 * monster.hasGuard();
	return score;
}

float GameState::evaluate() {
	//todo

	//constants
	constexpr float MY_HEALTH_CONST = 0.1f,
		ENEMY_HEALTH_CONST = -.1f,
		MY_CARDS_IN_HAND_CONST = 0.01f,
		//MY_CREATURE_DEF_CONST = 0.5,
		//MY_CREATURE_ATTACK_CONST = 1,
		//ENEMY_CREATURE_DEF_CONST = -0.6,
		//ENEMY_CREATURE_ATTACK_CONST = -1.1,
		//NUMBER_ENEMY_CREATURES_CONST = 0,
		//NUMBER_MY_CREATURES_CONST = 0,
		//WARD_MULTIPLIER_ATTACK = 1.1, //only if ward present
		//WARD_MULTIPLIER_DEF = 1.1, //only if ward present
		ME_DEAD_CONST = -1000,
		ENEMY_DEAD_CONST = 1000;


	auto& my_hand = getPlayerHand();
	auto& enemy_board = getEnemyBoard();
	auto& my_board = getPlayerBoard();
	auto& me = getPlayer();
	auto enemy = getEnemy();
	float score = 0;
	for (int i = 0; i < enemy_board.size; i++)
	{
		/*
		score +=
			enemy_board[i].attack * ENEMY_CREATURE_ATTACK_CONST * (enemy_board[i].hasWard() ? WARD_MULTIPLIER_ATTACK : 1)
			+ enemy_board[i].defense * ENEMY_CREATURE_DEF_CONST * (enemy_board[i].hasWard() ? WARD_MULTIPLIER_DEF : 1);
		*/
		score -= 1.25 * evaluateMonster(enemy_board[i]);
	}
	for (int i = 0; i < my_board.size; i++) {
		//score +=
		//	my_board[i].attack * MY_CREATURE_ATTACK_CONST * (my_board[i].hasWard() ? WARD_MULTIPLIER_ATTACK : 1)
		//	+ my_board[i].defense * MY_CREATURE_DEF_CONST * (my_board[i].hasWard() ? WARD_MULTIPLIER_DEF : 1);
		score += evaluateMonster(my_board[i]);
	}
	score += my_hand.size * MY_CARDS_IN_HAND_CONST;
	//score += my_board.size * NUMBER_MY_CREATURES_CONST;
	//score += enemy_board.size * NUMBER_ENEMY_CREATURES_CONST;
	//int my_health = min(15, me.health), enemy_health = min(10, enemy.health);
	int my_health = me.health, enemy_health = enemy.health;
	score += my_health * MY_HEALTH_CONST;
	score += enemy_health * ENEMY_HEALTH_CONST;
	score += my_hand.size * MY_CARDS_IN_HAND_CONST;

	if (me.health <= 0)
		score += ME_DEAD_CONST;
	if (enemy.health <= 0)
		score += ENEMY_DEAD_CONST;
	return score;
}

void GameState::addToDeck(Card card, bool players_deck) {
	_decks[players_deck].newItem() = card;
}

void GameState::addCard(Card card) {
	if (card.location == Location::PLAYER_HAND) {
		_player_hand.newItem() = card;
	}
	if (card.location == Location::PLAYER_BOARD) {
		_boards[0].newItem() = card;
	}
	if (card.location == Location::ENEMY_BOARD) {
		_boards[1].newItem() = card;
	}
}

enum class ActionType {
	SUMMON,
	ATTACK,
	USE,
	PASS
};

struct Action {
	int id = -1; //card that you want to use
	int target_id = -1; //target - be it item, opponent etc
	Lane lane;
	ActionType type;
	void pass();
	void attack(int id, int target_id = -1);
	void summon(int id, Lane lane);
	void use(int id, int target_id = -1);
};

void Action::pass() { type = ActionType::PASS; }
void Action::attack(int _id, int _target_id) { type = ActionType::ATTACK; id = _id; target_id = _target_id; }
void Action::summon(int _id, Lane _lane) { type = ActionType::SUMMON; id = _id;  lane = _lane; }
void Action::use(int _id, int _target_id) { type = ActionType::USE; id = _id; target_id = _target_id; }

ostream& operator << (ostream& os, const Action& action) {
	if (action.type == ActionType::SUMMON)
		os << "SUMMON " << action.id << ' ' << (int)action.lane;
	else if (action.type == ActionType::ATTACK)
		os << "ATTACK " << action.id << ' ' << action.target_id;
	else if (action.type == ActionType::USE)
		os << "USE " << action.id << ' ' << action.target_id;
	else if (action.type == ActionType::PASS)
		os << "PASS";
	return os;
}

uint8_t parseAbilities(string abilities) {
	uint8_t bitmap = 0;
	for (char a : abilities) {
		if (a == 'B')
			bitmap |= (uint8_t)Ability::BREAKTHROUGH;
		if (a == 'C')
			bitmap |= (uint8_t)Ability::CHARGE;
		if (a == 'G')
			bitmap |= (uint8_t)Ability::GUARD;
		if (a == 'D')
			bitmap |= (uint8_t)Ability::DRAIN;
		if (a == 'L')
			bitmap |= (uint8_t)Ability::LETHAL;
		if (a == 'W')
			bitmap |= (uint8_t)Ability::WARD;
	}
	return bitmap;
}

/*

"Greedy" alpha-beta minimax.
Pisząc "Greedy" mam na myśli sprawdzanie wszystkich możliwych akcji z pewnymi ograniczeniami.
1. Zaczynając atakować stronnika trzeba go zabić. Nie ma sensu go zaatakować i przestać.
	W tym przypadku tak długo jak atakowany stronnik żyje jedyne rozpatrywane akcje to
	atakowanie, przyzywanie stronników z szarżą, używanie czerwonych/niebieskich przedmiotów.
2. Przyzywanie stronników jeden po drugim. Nie ma sensu rozpatrywać przyzywania między atakami
	(chyba, że zostało zwolnione miejsce). Nie rozpatrujemy ataków stronnikami z szarżą jeśli wcześniej został
	przyzwany stronnik bez szarży.
3. Użycie zielonych przedmiotów rozpatrywane jest za każdym razem tuż po wszystkich przyzwaniach (wszystkich, znaczy tych rozpatrywanych w danym momencie).

4. Kolejność ataków moich stronników... To jest problem.
	MSmits pisał w post-mortem, że rozpatrywał stronników od tych z najmniejszym atakiem do tych z największym (chyba, że ma BREAKTHROUGH to jest wcześniej).
	Myślę o rozpatrywaniu ich w takiej kolejności + może w innych np:
		- Od stronników z największym atakiem
		- Od stronników z najmniejszą/największą ilością życia
		- Od stronników posortowanych po ich "wartości" (np kombinacja liniowa statystyk i mocy).

 Po zakończeniu przeszukiwania po mojej stronie należy zasymulować ataki po stronie przeciwnika. Dopiero po ich rozpatrzeniu można ocenić sytuację na stole i zastosować algorytm alpha-beta!
  Jeśli najlepsze zagranie przeciwnika (najgorsze dla nas) będzie miało ciągle ocenę większą niż nasze inne gałęzie drzewa (bez symulacji przeciwnika), to nie ma sensu ich rozpatrywać (bo przeciwnik może nam jedynie tą ocenę obniżyć)
 Jeśli nie starczy czasu na przeanalizowanie wszystkich możliwości można pomyśleć o wczesnym odcianiu (pruning)



 Zielone przedmioty: na wybór celu potrzeba 3 bity (6 stronników + nie robienie nic - 7 możliwości). Maksymalnie na ręce może być 8 kart. Oznacza to, że na użycie wielu zielonych przedmiotów
	potrzeba 8 * 3 bity = 24 bity.
 Przyzwanie wielu stronników może być zakodowane za pomocą 8 bitów: masz 8 kart w ręce i '1' oznacza którego stronnika przyzwiesz.

 Co do ataków: zakładając, że stronnicy są uporządkowani w pewien sposób atak na jednego stronnika wymaga 6 + 3 = 9 bitów (6 bitów - którzy stronnicy atakują, 3 bity - którego stronnika przeciwnika, 6  możliwości).
	Łącznie daje to 9 bitów + bity na stosowaną strategię uporządkowania < 32 bity. Atak jednego ze stronników przeciwnika wymaga jednego węzła w drzewie.
	W większości przypadków wystarczy jeden atak aby zabić przeciwnika. W najgorszym przypadku kiedy na stole jest 12 stronników zostanie rozpatrzone 36 ataków. Nie jest to zły wynik.
	Zakładając, że potrzeba dwóch ataków do zabicia przeciwnika, mając 12 stronników na polu trzeba rozważyć 6 * (6 po 2) = 6 * 15 = 90 ataków. To jest w praktyce górna granica liczby
	rozpatrywanych ataków, najczęściej ich liczba będzie pomiędzy 10 a 100.

 Póki co ataki rozpatrzę pojedyńczo, jeden stronnik atakując tylko jednego innego stronnika

 Przedmioty które usuwają umiejętności rozpatrywane są jako pierwsze (tylko jeden przedmiot nie usuwa ward'a).
 Czerwone przedmioty rozpatrywane są PRZED [lub po] fazie ataków.

Najwięcej bitów potrzeba na wybór zielonych/czerwonych przedmiotów - 24 bity. Do zakodowania każdej z faz wystarczy jedna liczba 32 bitowa.
	Pozostaje nam 8 dodatkowych bitów na dodatkowe informacje.
*/
constexpr uint32_t PHASE_MASK = 0xFF000000u;
constexpr uint32_t toPhaseMask(uint32_t phase) { return (phase & 0xFFu) << 24; }
constexpr uint32_t GREEN_ITEM_PHASE = toPhaseMask(1u);
constexpr uint32_t GREEN_ITEM_PASS_PHASE = toPhaseMask(2u);
constexpr uint32_t SUMMON_LEFT_PHASE = toPhaseMask(3u);
constexpr uint32_t SUMMON_RIGHT_PHASE = toPhaseMask(4u);
constexpr uint32_t SUMMON_LEFT_PASS_PHASE = toPhaseMask(5u);
constexpr uint32_t SUMMON_RIGHT_PASS_PHASE = toPhaseMask(6u);
constexpr uint32_t SUMMON_LEFT_CHARGE_PHASE = toPhaseMask(7u);
constexpr uint32_t SUMMON_RIGHT_CHARGE_PHASE = toPhaseMask(8u);
constexpr uint32_t SUMMON_LEFT_CHARGE_PASS_PHASE = toPhaseMask(9u);
constexpr uint32_t SUMMON_RIGHT_CHARGE_PASS_PHASE = toPhaseMask(10u);
constexpr uint32_t ATTACK_PHASE = toPhaseMask(11u);
constexpr uint32_t ATTACK_PASS_PHASE = toPhaseMask(12u);
constexpr uint32_t ATTACK_GUARDS_PHASE = toPhaseMask(13u);
constexpr uint32_t ATTACK_GUARDS_PASS_PHASE = toPhaseMask(14u);
constexpr uint32_t RED_ITEM_PHASE = toPhaseMask(15u);
constexpr uint32_t RED_ITEM_PASS_PHASE = toPhaseMask(16u);

constexpr uint32_t SWITCH_PLAYERS_PHASE = toPhaseMask(17u);
constexpr uint32_t EMPTY_ACTION = toPhaseMask(18u);

struct GameTreeAction {
	uint32_t data = 0xFFFFFFFFu; //bits are masked and used for indexing. If the bits are all '1's we do nothing
	bool isMaskSet(uint32_t mask) const { return (data & PHASE_MASK) == mask; }
	void setMask(uint32_t mask) { data = (data & ~PHASE_MASK) | mask; }
	void clearFirst6bits() { data &= ~0b111111u; }

	//GREEN ITEMS
	/*
	3 first bits: which item to use
	next 3 bits: on what target
	*/
	void setIsGreenItemPhase() { setMask(GREEN_ITEM_PHASE); }
	bool isGreenItemPhase() const { return isMaskSet(GREEN_ITEM_PHASE); }
	void setIsGreenItemPassPhase() { setMask(GREEN_ITEM_PASS_PHASE); }
	bool isGreenItemPassPhase() const { return isMaskSet(GREEN_ITEM_PASS_PHASE); }

	//RED ITEMS
	//structure same as green items
	void setIsRedItemPhase() { setMask(RED_ITEM_PHASE); clearFirst6bits(); }
	bool isRedItemPhase() const { return isMaskSet(RED_ITEM_PHASE); }
	void setIsRedItemPassPhase() { setMask(RED_ITEM_PASS_PHASE); }
	bool isRedItemPassPhase() const { return isMaskSet(RED_ITEM_PASS_PHASE); }

	//items helper functions
	int whatItemToUse() const { return data & 0b111u; }
	int onWhatTarget() const { return (data >> 3) & 0b111u; }
	void setItemToUse(int item_number_in_hand) { data |= item_number_in_hand; }
	void setItemTarget(int target_position_on_board) { data |= (target_position_on_board << 3); }

	//ATTACKS
	//information structure: |3 bits: which enemy to attack|3 bits: with which minion attack| <- only first 6 bits are important
	void setIsAttackPhase() { setMask(ATTACK_PHASE); }
	bool isAttackPhase() const { return isMaskSet(ATTACK_PHASE); }
	void setIsAttackPassPhase() { setMask(ATTACK_PASS_PHASE); }
	bool isAttackPassPhase() const { return isMaskSet(ATTACK_PASS_PHASE); }

	//GUARDS ATTACKS
	//same as attacks
	void setIsAttackGuardsPhase() { setMask(ATTACK_GUARDS_PHASE); }
	bool isAttackGuardsPhase() const { return isMaskSet(ATTACK_GUARDS_PHASE); }
	void setIsAttackGuardsPassPhase() { setMask(ATTACK_GUARDS_PASS_PHASE); }
	bool isAttackGuardsPassPhase() const { return isMaskSet(ATTACK_GUARDS_PASS_PHASE); }

	//attacks helper functions
	int whoToAttack() const { return (data >> 3) & 0b111u; }
	int whoAttacks() const { return  data & 0b111u; }


	//SUMMONING
	//structure: 8 bits representing which cards we summon. Each bit coresponds to one of the cards in hand
	void setIsSummonLeftPhase() { setMask(SUMMON_LEFT_PHASE); }
	void setIsSummonRightPhase() { setMask(SUMMON_RIGHT_PHASE); }
	bool isSummonLeftPhase() const { return isMaskSet(SUMMON_LEFT_PHASE); }
	bool isSummonRightPhase() const { return isMaskSet(SUMMON_RIGHT_PHASE); }
	void setIsSummonLeftPassPhase() { setMask(SUMMON_LEFT_PASS_PHASE); }
	void setIsSummonRightPassPhase() { setMask(SUMMON_RIGHT_PASS_PHASE); }
	bool isSummonLeftPassPhase() const { return isMaskSet(SUMMON_LEFT_PASS_PHASE); }
	bool isSummonRightPassPhase() const { return isMaskSet(SUMMON_RIGHT_PASS_PHASE); }

	//SUMMONING MINIONS WITH CHARGE
	//same as summoning
	void setIsSummonLeftChargePhase() { setMask(SUMMON_LEFT_CHARGE_PHASE); }
	void setIsSummonRightChargePhase() { setMask(SUMMON_RIGHT_CHARGE_PHASE); }
	bool isSummonLeftChargePhase() const { return isMaskSet(SUMMON_LEFT_CHARGE_PHASE); }
	bool isSummonRightChargePhase() const { return isMaskSet(SUMMON_RIGHT_CHARGE_PHASE); }
	void setIsSummonLeftChargePassPhase() { setMask(SUMMON_LEFT_CHARGE_PASS_PHASE); }
	void setIsSummonRightChargePassPhase() { setMask(SUMMON_RIGHT_CHARGE_PASS_PHASE); }
	bool isSummonLeftChargePassPhase() const { return isMaskSet(SUMMON_LEFT_CHARGE_PASS_PHASE); }
	bool isSummonRightChargePassPhase() const { return isMaskSet(SUMMON_RIGHT_CHARGE_PASS_PHASE); }
	bool isSummonPhase() const {
		return isSummonLeftPhase() || isSummonRightPhase();
	}
	bool isSummonChargePhase() const {
		return isSummonLeftChargePhase() || isSummonRightChargePhase();
	}

	//summon helper functions
	bool * whoToSummon() const {
		static bool t[8];
		for (int i = 0; i < 8; i++)
			t[i] = (data >> i) & 0b1u;
		return t;
	}

	//SWITCHING PLAYERS
	void setIsSwitchPlayersPhase() { setMask(SWITCH_PLAYERS_PHASE); }
	bool isSwitchPlayersPhase() const { return isMaskSet(SWITCH_PLAYERS_PHASE); }

	//EMPTY ACTION
	bool isEmpty() const { return isMaskSet(EMPTY_ACTION); }
	void setEmpty() { setMask(EMPTY_ACTION); }

	void reset() { data = 0xFFFFFFFFu; setEmpty(); }

	std::vector<Action> toActions(GameState& gs) const;
};

std::vector<Action> GameTreeAction::toActions(GameState& gs) const {
	//GameState& gs SHOULD BE GAME STATE REPRESENTING PARENT NOTE, NOT THIS NODE!!!
	std::vector<Action> actions;
	auto& hand = gs.getPlayerHand();
	auto& my_board = gs.getPlayerBoard();
	auto& enemy_board = gs.getEnemyBoard();
	auto& target_board = (isGreenItemPhase() ? my_board : enemy_board);
	if (isGreenItemPhase() || isRedItemPhase()) {
#if SHOW_TO_ACTIONS
		if (isGreenItemPhase())
			cerr << "toActions: green item" << endl;
		else if (isRedItemPhase())
			cerr << "toActions: red item" << endl;
#endif
		int what_item = whatItemToUse();
		int target = onWhatTarget();
		actions.emplace_back();
		actions.back().use(hand[what_item].instance_id, target_board[target].instance_id);
	}
	else if (isSummonPhase() || isSummonChargePhase()) {
#if SHOW_TO_ACTIONS
		cerr << "toActions: Summon" << endl;
#endif
		bool * who = whoToSummon();
		Lane lane = (isSummonLeftChargePhase() || isSummonLeftChargePassPhase() || isSummonLeftPhase() || isSummonLeftPassPhase()
			? Lane::LEFT : Lane::RIGHT);
		for (int i = 0; i < 8; i++) {
			if (who[i]) {
				actions.emplace_back();
				actions.back().summon(hand[i].instance_id, lane);
			}
		}
	}
	else if (isAttackPhase() || isAttackGuardsPhase()) {
#if SHOW_TO_ACTIONS
		cerr << "toActions: Attack" << endl;
#endif
		int who = whoAttacks();
		int whom = whoToAttack();
		actions.emplace_back();
		actions.back().attack(my_board[who].instance_id, enemy_board[whom].instance_id);
	}
	return actions;
}

void GameState::applyAction(GameTreeAction& a) {
	/*
	Notice that we remove cards from hand, board etc. That changes their order on which most actions depend.
	But as long as theirs position changes deterministically (ex: removing is just swapping with last item in array and shrinking array by 1)
		everything should be fine
	*/

	bool items_used[8] = { false, false, false, false, false, false, false, false };
	bool minions_summoned[8] = { false, false, false, false, false, false, false, false };
	auto & board = getPlayerBoard();
	auto & enemy_board = getEnemyBoard();
	if (a.isSwitchPlayersPhase()) {
		//attack enemy hero with every minion avaliable
		attackEnemyWithAllCreatures();
		switchSides();
	}
	else if (a.isGreenItemPhase() || a.isRedItemPhase() || a.isGreenItemPassPhase() || a.isRedItemPassPhase()) {
#if SHOW_APPLY_ACTIONS
		if (a.isGreenItemPhase())
			cerr << "apply green item" << endl;
		else if (a.isRedItemPhase())
			cerr << "apply red item" << endl;
#endif
		auto & hand = getPlayerHand();
		int which_item = a.whatItemToUse();
		if (a.isGreenItemPassPhase() || a.isRedItemPassPhase()) {
			hand[which_item].passed_attack_or_use = true;
		}
		else {
			auto& target_board = (a.isGreenItemPhase() ? getPlayerBoard() : getEnemyBoard());
			int target = a.onWhatTarget();
			Card::useItemOnCreature(hand[which_item], target_board[target]);
			items_used[which_item] = true;
			getPlayer().mana -= hand[which_item].cost;
		}
	}
	else if (a.isAttackPhase() || a.isAttackGuardsPhase() || a.isAttackGuardsPassPhase() || a.isAttackPassPhase()) {
#if SHOW_APPLY_ACTIONS
		cerr << "apply attacks as player " << playingAsEnemy() << endl;
#endif
		bool pass = a.isAttackGuardsPassPhase() || a.isAttackPassPhase();
		int who = a.whoAttacks();
		if (pass) {
			board[who].passed_attack_or_use = true;
		}
		else {
			int whom = a.whoToAttack();
			if (!enemy_board[whom].hasWard() && board[who].hasDrain())
				getPlayer().health += board[who].attack;
			if (!board[who].hasWard() && enemy_board[whom].hasDrain())
				getEnemy().health += enemy_board[whom].attack;
			Card::resolveAttack(board[who], enemy_board[whom]);
			Card::resolveBreakthrough(board[who], enemy_board[whom]);
			if (enemy_board[whom].breakthrough_damage > 0)
				getEnemy().health -= enemy_board[whom].breakthrough_damage;
			board[who].can_attack_this_turn = false;
		}
	}
	else if (a.isSummonLeftChargePhase() || a.isSummonRightChargePhase() || a.isSummonLeftPhase() || a.isSummonRightPhase()) {
		//|| a.isSummonLeftChargePassPhase() || a.isSummonRightChargePassPhase() || a.isSummonLeftPassPhase() || a.isSummonRightPassPhase()) {
#if SHOW_APPLY_ACTIONS
		cerr << "apply summon" << endl;
#endif
		auto & hand = getPlayerHand();
		auto data = a.data;
		//bool pass_left = a.isSummonLeftChargePassPhase() || a.isSummonLeftPassPhase();
		//bool pass_right = a.isSummonRightChargePassPhase() || a.isSummonRightPassPhase();
		for (int i = 0; i < hand.size; i++, data >>= 1) {
			if (data & 1u) {
				/*
				if (pass_left) {
					continue;
				}
				if (pass_right) {
					continue;
				}
				*/
				//sanity checks
				if (getPlayerBoard().size == 6) {
					cerr << "Attempting to summon minion on full board" << endl;
					trap();
				}
				if (!hand[i].isCreature()) {
					cerr << "Tried to summon " << hand[i] << " as a creature" << endl;
					trap();
				}

				minions_summoned[i] = true;
				getPlayer().mana -= hand[i].cost;
				if (getPlayer().mana < 0) {
					cerr << "Tried to summon creature with not enough mana" << endl;
					trap();
				}
				hand[i].can_attack_this_turn = hand[i].hasCharge();
				hand[i].lane = (a.isSummonLeftChargePhase() || a.isSummonLeftPhase() ? Lane::LEFT : Lane::RIGHT);
				board.newItem() = hand[i];
			}
		}
	}
	if (!playingAsEnemy()) {
		//delete minions after summoning to not alter their order
		for (int i = 7; i >= 0; i--)
			if (minions_summoned[i] || items_used[i])
				getPlayerHand().deleteItem(i);
	}
	removeDeadMinions();
}

GameState GameState::fromAction(GameTreeAction& action)
{
	auto gs_copy = copy();
	gs_copy.applyAction(action);
	return gs_copy;
}

struct GameTreeNode {
	int first_child_index = -1;
	int children_count = 0;
	GameTreeAction previous_action; //action that performed on parent results in this GameTreeNode
	//float alpha, beta; //todo
	float score = 0;
	bool branch_expanded = false;
	//int depth = 0;

	void expandOneLevel(GameState&& copy_of_game_state);

	void expandGreenItemPhase(GameState&);
	void expandSummonPhase(GameState&, bool charge_only = false, Lane lane = Lane::LEFT);
	void expandAttackPhase(GameState&);
	void expandRedItemPhase(GameState&);
	void _expandItemPhase(GameState&, bool green_phase /*if not, then red phase*/);

	bool expanded() const { return first_child_index != -1; }
	bool leaf() const { return first_child_index == -1 && branch_expanded; }

	void clear() { first_child_index = -1; previous_action.reset(); branch_expanded = false; children_count = 0; score = 0; }
	void createChildNode(const GameTreeAction& action);
};

constexpr int MAX_NODES = 1000000; //1M nodes
struct {
	GameTreeNode* NODES{ new GameTreeNode[MAX_NODES] };
	int head = 0;
	int newNode() {
		if (head >= MAX_NODES) {
			cerr << "Out of nodes" << endl;
			trap();
		}
		NODES[head].clear();
		return head++;
	}
	void clear() { head = 0; }
	int size() { return head; }
	GameTreeNode& getNode(int idx) { return NODES[idx]; }
} NODE_CONTAINER;

void GameTreeNode::createChildNode(const GameTreeAction& action)
{
	int node_idx = NODE_CONTAINER.newNode();
	if (first_child_index == -1)
		first_child_index = node_idx;
	children_count++;
	NODE_CONTAINER.NODES[node_idx].previous_action = action;
}

void GameTreeNode::expandGreenItemPhase(GameState& gs) {
#if SHOW_EXPANDING_PHASES
	cerr << "expandGreenItemPhase" << endl;
#endif
	_expandItemPhase(gs, true);
#if SHOW_EXPANDING_PHASES
	cerr << "end expandGreenItemPhase" << endl;
#endif
}

void GameTreeNode::expandRedItemPhase(GameState& gs) {
	_expandItemPhase(gs, false);
}

void GameTreeNode::_expandItemPhase(GameState& gs, bool green_phase) {
	auto& hand = gs.getPlayerHand();
	const int mana = gs.getPlayer().mana;
	auto& my_board = gs.getPlayerBoard();
	auto& enemy_board = gs.getEnemyBoard();
	if (green_phase && my_board.size == 0 || !green_phase && enemy_board.size == 0) {
		return; //cant use green or red items without targets
	}
	auto& target_board = (green_phase ? my_board : enemy_board);

	Vector<8, std::pair<int, int>> items_in_hand; //(cost, position in hand)
	for (int i = 0; i < hand.size; i++)
		if (hand[i].canBePlayed() && (green_phase && hand[i].isGreenItem() || !green_phase && hand[i].isRedItem()) && mana >= hand[i].cost)
			items_in_hand.newItem() = { hand[i].cost, i };

	sort(items_in_hand.data, items_in_hand.data + items_in_hand.size);

	for (int i = 0; i < items_in_hand.size; i++) {
		//create pass action that omits this item
		GameTreeAction no_target_action;
		if (green_phase)
			no_target_action.setIsGreenItemPassPhase();
		else
			no_target_action.setIsRedItemPassPhase();
		no_target_action.data &= ~0b111111u;
		no_target_action.data |= items_in_hand[i].second;
		createChildNode(no_target_action);

		//consider using this item on every minion on board
		for (int j = 0; j < target_board.size; j++) {
			GameTreeAction action;
			if (green_phase)
				action.setIsGreenItemPhase();
			else
				action.setIsRedItemPhase();
			action.data &= ~0b111111u;
			action.data |= items_in_hand[i].second; //what item to use
			action.data |= (j << 3); //on what target
			createChildNode(action);
		}
	}
}

void GameTreeNode::expandSummonPhase(GameState& gs, bool charge_only, Lane lane) {
#if SHOW_EXPANDING_PHASES
	cerr << "expandSummonPhase" << endl;
	cerr << "boardSize " << gs.getPlayerBoard().size << endl;
#endif
	auto& hand = gs.getPlayerHand();
	const int mana = gs.getPlayer().mana;
	auto & board = gs.getPlayerBoard();

	int player_board_size = 0;
	for (int i = 0; i < board.size; i++)
		if (board[i].lane == lane)
			player_board_size++;

	if (player_board_size < 3) {
		Vector<8, std::pair<int, int>> minions_in_hand; //(cost, position in hand)
		for (int i = 0; i < hand.size; i++) {
			if (hand[i].isCreature() && (charge_only && hand[i].hasCharge() || !charge_only && !hand[i].hasCharge())) {
				// cerr << hand[i] << " is a creature" << endl;
				minions_in_hand.newItem() = { hand[i].cost, i };
			}
		}
		sort(minions_in_hand.data, minions_in_hand.data + minions_in_hand.size, [](auto a, auto b) {return a.first > b.first; });
		bool summoned_something = false;
		for (int i = 0; i < minions_in_hand.size; i++) {
			int remaining_mana = mana;
			int remaining_space = 3 - player_board_size;
			GameTreeAction summon_action;
			if (charge_only) {
				if (lane == Lane::LEFT)
					summon_action.setIsSummonLeftChargePhase();
				else
					summon_action.setIsSummonRightChargePhase();
			}
			else {
				if (lane == Lane::LEFT)
					summon_action.setIsSummonLeftPhase();
				else
					summon_action.setIsSummonRightPhase();
			}
			summon_action.data &= ~0b11111111u;
			for (int j = i; j < minions_in_hand.size; j++) {
				auto & minion = hand[minions_in_hand[j].second];
				if (minion.cost > remaining_mana)
					continue;
				if (remaining_space == 0)
					continue;
				summoned_something = true;
				remaining_mana -= minion.cost;
				remaining_space--;
				summon_action.data |= (1u << minions_in_hand[j].second);
			}
			if (summon_action.data & 0b11111111u) {
				createChildNode(summon_action);
			}
		}
		if (summoned_something) {
			GameTreeAction pass_summon;
			if (charge_only)
				if (lane == Lane::LEFT)
					pass_summon.setIsSummonLeftChargePassPhase();
				else
					pass_summon.setIsSummonRightChargePassPhase();
			else
				if (lane == Lane::LEFT)
					pass_summon.setIsSummonLeftPassPhase();
				else
					pass_summon.setIsSummonRightPassPhase();
			createChildNode(pass_summon);
		}
	}

#if SHOW_EXPANDING_PHASES
	cerr << "end expandSummonPhase" << endl;
	cerr << "boardSize " << gs.getPlayerBoard().size << endl;
#endif
}

void GameTreeNode::expandAttackPhase(GameState& gs) {
#if SHOW_EXPANDING_PHASES
	cerr << "expandAttackPhase" << endl;
	cerr << "playerBoard size " << gs.getPlayerBoard().size << endl;
#endif
	// cerr << "Second time attack: " << attacking_second_time << endl;
	auto& my_board = gs.getPlayerBoard();
	auto& enemy_board = gs.getEnemyBoard();
	if (my_board.size == 0 || enemy_board.size == 0) {
		// cerr << "No attackers" << endl;
		return; //no attackers or attacked. Player is always attacked by all avaliable minions
	}

	bool enemy_guard_left = gs.enemyHasGuard(Lane::LEFT);
	bool enemy_guard_right = gs.enemyHasGuard(Lane::RIGHT);

	Vector<6, pair<int, int>> my_minions; //(attack, position on board)
	for (int i = 0; i < my_board.size; i++)
		if (my_board[i].canAttackThisTurn())
			my_minions.newItem() = { my_board[i].attack, i };
	sort(my_minions.data, my_minions.data + my_minions.size); //sort attacking minions from lowest to highest attack


	// cerr << "Enemy board size " << enemy_board.size << endl;
	// cerr << "My minions: " << n_my_minions << '/' << my_board.size << endl;
	bool attacked_something = false;
	if (my_minions.size > 0) {
		auto & my_minion = my_board[my_minions[0].second];
		for (int j = 0; j < enemy_board.size; j++) {
			if (enemy_board[j].lane == Lane::LEFT && enemy_guard_left && !enemy_board[j].hasGuard())
				continue;
			if (enemy_board[j].lane == Lane::RIGHT && enemy_guard_right && !enemy_board[j].hasGuard())
				continue;
			if (enemy_board[j].lane != my_minion.lane)
				continue;
			GameTreeAction attack;
			if (my_minion.lane == Lane::LEFT && enemy_guard_left || my_minion.lane == Lane::RIGHT && enemy_guard_right)
				attack.setIsAttackGuardsPhase();
			else
				attack.setIsAttackPhase();
			attack.data &= ~0b111111u;
			attack.data |= (j << 3); // target
			attack.data |= my_minions[0].second;
			createChildNode(attack);
			attacked_something = true;
		}
		if (attacked_something) {
			GameTreeAction attack_noone;
			if (my_minion.lane == Lane::LEFT && enemy_guard_left || my_minion.lane == Lane::RIGHT && enemy_guard_right)
				attack_noone.setIsAttackGuardsPassPhase();
			else
				attack_noone.setIsAttackPassPhase();
			attack_noone.data &= ~0b111111u;
			attack_noone.data |= my_minions[0].second;
			createChildNode(attack_noone);
		}
	}



#if SHOW_EXPANDING_PHASES
	cerr << "end expandAttackPhase" << endl;
	cerr << "boardSize " << gs.getPlayerBoard().size << endl;
#endif
}

void GameTreeNode::expandOneLevel(GameState&& copy_of_game_state)
{
	//for now expand randomly
	if (expanded()) {
		// cerr << "Expanded. Going deeper." << endl;
		bool all_children_fully_checked = true;
		for (int i = 0; i < children_count; i++) {
			int child_idx = first_child_index + i;
			auto& child = NODE_CONTAINER.NODES[child_idx];
			if (child.branch_expanded)
				continue;
			child.expandOneLevel(copy_of_game_state.fromAction(child.previous_action));
			if (!child.branch_expanded)
				all_children_fully_checked = false;
		}
		if (all_children_fully_checked) {
			branch_expanded = true;
			score = NODE_CONTAINER.NODES[first_child_index + 0].score;
			for (int i = 1; i < children_count; i++) {
				if (copy_of_game_state.playingAsEnemy())
					score = min(score, NODE_CONTAINER.NODES[first_child_index + i].score);
				else
					score = max(score, NODE_CONTAINER.NODES[first_child_index + i].score);
			}
		}
	}
	else {
		/*
		Phase order:
		1. summon (only charge)
		2. green item
		3. red item
		4. attack
		5. summon (if there is space to summon after attacks)
		6. green item phase
		*/
		// cerr << "Not expanded." << endl;
		int phase = 1;
		if (!copy_of_game_state.playingAsEnemy()) {

			if (TIME_ELAPSED < 95/*ms*/) {
				//expand node from our perspective
				if (previous_action.isEmpty()
					|| previous_action.isSummonLeftChargePhase()
					|| previous_action.isSummonLeftChargePassPhase()) {

					Lane lane = (previous_action.isEmpty() ? Lane::LEFT : Lane::RIGHT);
					expandSummonPhase(copy_of_game_state, true, lane);

					if (!expanded()) {
						//go to the next phase
						phase = 2;
					}
				}

				if (previous_action.isSummonLeftChargePhase()
					|| previous_action.isSummonRightChargePhase()
					|| previous_action.isSummonLeftChargePassPhase()
					|| previous_action.isSummonRightChargePassPhase()
					|| previous_action.isGreenItemPhase()
					|| previous_action.isGreenItemPassPhase()
					|| phase == 2) {
					expandGreenItemPhase(copy_of_game_state);
					if (!expanded())
						phase = 3;
				}

				if (previous_action.isGreenItemPassPhase()
					|| previous_action.isGreenItemPhase()
					|| previous_action.isRedItemPhase()
					|| previous_action.isRedItemPassPhase()
					|| phase == 3) {
					expandRedItemPhase(copy_of_game_state);
					if (!expanded())
						phase = 4;
				}

				if (previous_action.isRedItemPhase()
					|| previous_action.isRedItemPassPhase()
					|| previous_action.isAttackGuardsPhase()
					|| previous_action.isAttackGuardsPassPhase()
					|| previous_action.isAttackPhase()
					|| previous_action.isAttackPassPhase()
					|| phase == 4) {
					expandAttackPhase(copy_of_game_state);
					if (!expanded())
						phase = 5;
				}

				if (previous_action.isAttackPassPhase()
					|| previous_action.isAttackGuardsPhase()
					|| previous_action.isAttackPassPhase()
					|| previous_action.isAttackGuardsPassPhase()
					|| previous_action.isSummonLeftPhase()
					|| previous_action.isSummonLeftPassPhase()
					|| phase == 5) {
					Lane lane = (previous_action.isSummonLeftPhase() || previous_action.isSummonLeftPassPhase()
						? Lane::RIGHT : Lane::LEFT);
					expandSummonPhase(copy_of_game_state, false, lane);
				}


				if (previous_action.isSummonPhase()) {
					expandGreenItemPhase(copy_of_game_state);
				}

				if (!expanded()) {
					GameTreeAction switch_players;
					switch_players.setIsSwitchPlayersPhase();
					createChildNode(switch_players);
				}
			}
		}
		else {
			if (TIME_ELAPSED < 95 /*ms*/) {
				if (previous_action.isSwitchPlayersPhase()
					|| previous_action.isAttackGuardsPhase()
					|| previous_action.isAttackGuardsPassPhase()
					|| previous_action.isAttackPhase()
					|| previous_action.isAttackPassPhase()) {
					expandAttackPhase(copy_of_game_state);
				}
			}
			if (!expanded()) {
				branch_expanded = true;
				copy_of_game_state.attackEnemyWithAllCreatures();
				copy_of_game_state.switchSides();
				score = copy_of_game_state.evaluate();
			}
		}

	}
}

//pick card according to tier list taken from here. Skip blue items
//https://lev.pm/posts/2018-09-01-legends-of-code-and-magic-postmortem/#draft
//53th legend
constexpr int CARD_TIER_LIST_1[] = { 68, 7, 65, 49, 116, 69, 151, 48, 53, 51, 44, 67, 29, 139, 84, 18, 158, 28, 64, 80, 33, 85,
	32, 147, 103, 37, 54, 52, 50, 99, 23, 87, 66, 81, 148, 88, 150, 121, 82, 95, 115, 133, 152,
	19, 109, 157, 105, 3, 75, 96, 114, 9, 106, 144, 129, 17, 111, 128, 12, 11, 145, 15, 21, 8,
	134, 155, 141, 70, 90, 135, 104, 41, 112, 61, 5, 97, 26, 34, 73, 6, 36, 86, 77, 83, 13, 89,
	79, 93, 149, 59, 159, 74, 94, 38, 98, 126, 39, 30, 137, 100, 62, 122, 22, 72, 118, 1, 47, 71,
	4, 91, 27, 56, 119, 101, 45, 16, 146, 58, 120, 142, 127, 25, 108, 132, 40, 14, 76, 125, 102,
	131, 123, 2, 35, 130, 107, 43, 63, 31, 138, 124, 154, 78, 46, 24, 10, 136, 113, 60, 57, 92,
	117, 42, 55, 153, 20, 156, 143, 110, 160, 140, -1
};

//IN BOTH CASES THERE WERE SOME TIMEOUTS WHILE THERE WERE A LOT OF CREATURES ON THE BOARD

//ClosetAI's list
// ~80th legend
constexpr int CARD_TIER_LIST_2[] = {
116, 68, 151, 51, 65, 80, 7, 53, 29, 37, 67, 32, 139, 69, 49, 33, 66, 147, 18, 152, 28, 48, 82, 88, 23, 84, 52, 44, 87, 148,
99, 121, 64, 85, 103, 141, 158, 50, 95, 115, 133, 19, 109, 54, 157, 81, 150, 21, 34, 36, 135, 134, 70, 3, 61, 111, 75, 17,
144, 129, 145, 106, 9, 105, 15, 114, 128, 155, 96, 11, 8, 86, 104, 97, 41, 12, 26, 149, 90, 6, 13, 126, 93, 98, 83, 71,
79, 72, 73, 77, 59, 100, 137, 5, 89, 142, 112, 25, 62, 125, 122, 74, 120, 159, 22, 91, 39, 94, 127, 30, 16, 146, 1, 45,
38, 56, 47, 4, 58, 118, 119, 40, 27, 35, 101, 123, 132, 2, 136, 131, 20, 76, 14, 43, 102, 108, 46, 60, 130, 117, 140, 42,
124, 24, 63, 10, 154, 78, 31, 57, 138, 107, 113, 55, 143, 92, 156, 110, 160, 153, -1
};

struct Actor {

	Actor(GameState& gs, GameTreeNode& root) : game_state(gs), game_tree_root(root) {}

	GameState& game_state;
	GameTreeNode& game_tree_root;

	bool in_draft = true;

	int draftPickCard(vector<Card>& choices) {
		const int * BEST_CARDS = CARD_TIER_LIST_1;
		int choices_idx[3] = { 0, 1, 2 };
		std::sort(choices_idx, choices_idx + 3, [&](int a, int b) {
			int a_pos = -1, b_pos = -1;
			for (int i = 0; BEST_CARDS[i] != -1; i++) {
				if (BEST_CARDS[i] == choices[a].number)
					a_pos = i;
				if (BEST_CARDS[i] == choices[b].number)
					b_pos = i;
			}
			if (a_pos == -1 || b_pos == -1) {
				cerr << "Something is wrong in draft" << endl;
				trap();
			}
			if (choices[a].isBlueItem()) {
				if (!choices[b].isBlueItem())
					return false;
			}
			else if (choices[b].isBlueItem())
				return true;
			return a_pos < b_pos;
		});
		return choices_idx[0];
	}

	void think() {
		if (!in_draft) {
			START_TIMER;
			auto start = chrono::high_resolution_clock::now();
			cerr << "Thinking. Player mana: " << game_state.getPlayer().mana << endl;
			//for(int i = 0; i < 5/*number of possible phases*/; i++)
			while (!game_tree_root.branch_expanded)
				game_tree_root.expandOneLevel(game_state.copy());
			cerr << "All nodes checked" << endl;
			cerr << "Best score: " << game_tree_root.score << endl;
			cerr << "Time thinking: " << chrono::duration_cast<chrono::milliseconds>(chrono::high_resolution_clock::now() - start).count() << "ms" << endl;
		}
		cerr << "Nodes used: " << NODE_CONTAINER.size() << endl;
	}

	std::vector<Action> performBestActions() {
		std::vector<Action> actions;

		cerr << "Performing actions. " << endl;
		int depth = 0;
		while (game_tree_root.expanded()) {
			depth++;
			//pick child with the largest depth
			int best_child_idx = game_tree_root.first_child_index;
			for (int i = game_tree_root.first_child_index + 1; i < game_tree_root.first_child_index + game_tree_root.children_count; i++)
				if (NODE_CONTAINER.NODES[i].score > NODE_CONTAINER.NODES[best_child_idx].score)
					best_child_idx = i;
			auto& child = NODE_CONTAINER.NODES[best_child_idx];
			if (child.previous_action.isSwitchPlayersPhase())
				break;
			auto a = child.previous_action.toActions(game_state);

			actions.insert(actions.end(), a.begin(), a.end());
			game_tree_root = child;
			game_state.applyAction(game_tree_root.previous_action);
		}

		if (actions.empty()) {
			actions.emplace_back();
			actions.back().pass();
		}
		game_tree_root.previous_action.setEmpty();

		for (int i = 0; i < game_state.getPlayerBoard().size; i++) {
			auto& creature = game_state.getPlayerBoard()[i];
			if (creature.canAttackEnemyHeroThisTurn())
			{
				cerr << creature << " is free to attack. Trying to attack enemy even if there is a guard" << endl;
				if (!game_state.enemyHasGuard(creature.lane)) {
					actions.emplace_back();
					actions.back().attack(creature.instance_id, -1);
				}
			}
		}
		cerr << "Depth: " << depth << endl;
		return actions;
	}
};

ostream& operator << (ostream& os, const std::vector<Action>& actions) {
	for (int i = 0; i < actions.size(); i++) {
		os << actions[i];
		if (i + 1 < actions.size())
			os << "; ";
	}
	return os;
}

int main()
{
	srand(42);
	// game loop
	GameState game_state;
	GameTreeNode root;
	Actor player_actor(game_state, root);
	while (1) {
		game_state.clear();
		root.clear();
		for (int i = 0; i < 2; i++) {
			int playerHealth;
			int playerMana;
			int playerDeck;
			int playerRune; // the additional number of drawn cards - this turn draw for the player, next turn draw (without broken runes) for the opponent
			int playerDraw;
			cin >> playerHealth >> playerMana >> playerDeck >> playerRune >> playerDraw; cin.ignore();
			player_actor.in_draft = playerMana == 0;
			game_state._players[i].health = playerHealth;
			game_state._players[i].mana = playerMana;
			game_state._players[i].deck = playerDeck;
			game_state._players[i].rune = playerRune;
			game_state._players[i].draw = playerDraw;
		}
		int opponentHand;
		int opponentActions;
		int opponent_draft_pick = -1;
		cin >> opponentHand >> opponentActions; cin.ignore();
		for (int i = 0; i < opponentActions; i++) {
			string cardNumberAndAction;
			getline(cin, cardNumberAndAction);
			if (cardNumberAndAction.size() >= 6 /*"PICK X"*/ && cardNumberAndAction.substr(0, 4) == "PICK")
				opponent_draft_pick = (cardNumberAndAction[5] - '0');
		}
		int cardCount;
		cin >> cardCount; cin.ignore();
		vector<Card> draft_choices;
		for (int i = 0; i < cardCount; i++) {
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
			cin >> cardNumber >> instanceId >> location >> cardType >> cost >> attack >> defense >> abilities >> myHealthChange >> opponentHealthChange >> cardDraw >> lane; cin.ignore();
			Card card;
			card.number = cardNumber;
			card.abilities = parseAbilities(abilities);
			card.instance_id = instanceId;
			card.location = (Location)location;
			card.type = (CardType)cardType;
			card.cost = cost;
			card.attack = attack;
			card.defense = defense;
			card.my_health_change = myHealthChange;
			card.opponent_health_change = opponentHealthChange;
			card.draw = cardDraw;
			card.lane = (Lane)lane;
			card.can_attack_this_turn = card.location != Location::PLAYER_HAND;
			if (player_actor.in_draft) {
				draft_choices.push_back(card);
			}
			else {
				game_state.addCard(card);
			}
		}
		if (player_actor.in_draft) {
			int card_index = player_actor.draftPickCard(draft_choices);
			game_state.addToDeck(draft_choices[card_index], true);
			game_state.addToDeck(draft_choices[opponent_draft_pick], false);
			cout << "PICK " << card_index << endl;
		}


		//player_actor.think();
		auto gs_copy = game_state;
		auto root_copy = root;

		/*
		root_copy.expandSummonPhase(gs_copy); //looks like summoning works for one turn
		if (root_copy.first_child_index != -1) {
			root_copy = NODE_CONTAINER.NODES[root_copy.first_child_index];

		}
		*/
		if (!player_actor.in_draft) {
			player_actor.think();
			cout << player_actor.performBestActions() << endl;
		}

	}
}



/*

Najwięksi stronnicy atakują możliwie największych stronników przeciwnika (generalnie: im mniej ataków (wymian) tym lepiej)
Mali stronnicy powinni atakować albo innych małych stronników, albo jednych z największych (życie po ataku ma być jak najmniejsze)

Zielony przedmiot : daje statystyki i moc / dobiera karty (tylko przyjaźni stronnicy)
Czerwony przedmiot : zadaje obrażenia przeciwnym stronnikom / zabiera im moce. Czasami dobiera karty
Niebieski przedmiot : słabe połączenia czerwonych i zielonych przedmiotów -> na pierwszy rzut oka lepiej nie używać

Ocena stanu gry: cechy_przeciwnika * C_1 + moje_cechy * C_2 (suma ataków, obron; ilość stronników; ile kart w tali; ile kart w ręce; ile kart dobranych w kolejnej turze)

*/

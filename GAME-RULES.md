
# LOCM 1.2 Game Rules

You can also see
- [Short introduction to the game](https://jakubkowalski.tech/Projects/LOCM/CEC19/intro.html)
- [Image version](https://jakubkowalski.tech/Projects/LOCM/CEC19/rules.html)

## The Goal

Draft a deck of cards, battle an opponent with those cards and reduce their Health Points (HP) from 30 to 0.

## Rules

This game is a two-player card game which is played in two phases: the **Draft** phase and the **Battle** phase.
- During the **Draft** phase, both players must create a deck of **30** cards.
- Once the **Draft** phase is over, both decks are shuffled.
- During the **Battle**, the board is divided in two parts: each player plays cards from their hand on their side of the board.
- Each player starts with **30** HP. Some cards can increase this number.
- To reduce the health points of an opponent, the player must make use of cards to deal damage.

## Draft Phase

- For **30** turns, both players are given a choice between 3 different cards. Players select the card they want to add to their deck by using the `PICK` command followed by **0**, **1** or **2**.
- By default, the `PASS` command will pick the first card.
- Both players can select the same card, they will each receive a copy.

## Battle Phase

### Card Draw

- First player starts with **4** cards in hand whereas the second player starts with **5**.
- Each turn, the active player draws one additional card from their deck.
- Some cards can make players draw additional cards at the beginning of the next turn when played.
- Both players possess **runes** which have an impact on card draw. More details in [Advanced Details](#Advanced-Details) section.

### Mana

- Mana is necessary to play cards from the hand.
- The first player starts with **1 max mana**, the second with **2 max mana**.
- Each player can spend as much mana per turn as they have max mana.
- The second player receives his **+1 max mana bonus** until he spends all his mana during a turn.
- Each turn, the active player is granted one additional max mana, unless they already have **12** max mana (**13** for the second player who didn't spend his bonus).


## Card Types 
There are two different types of cards: **Creatures** and **Items**. 

### Creatures
- Placing a creature card from the hand to the board is called _summoning_.
- A player summons **creatures** to their side of the board by paying their cost in _mana_. They are used to attack the opponent and also serve as a defense against the creatures of the opposing player.
- Creatures have a cost in mana, attack points and defense points. Some creatures start with certain abilities.
- By default, creatures can't attack the turn they are summoned. They can attack once per turn only.
- When a creature attacks another one, they both deal _damage_ equals to their attack to the defense of the other creature. When a creature attacks the opponent, it deals _damage_ equals to its attack to the HP of the opponent.
- Creatures are removed from play when their defense reaches **0** or less.
- Creatures can have an effect on the player's health, the opponent's health or the card draw of the player when played.
- Creatures can have different abilities:
  - **Breakthrough**: Creatures with Breakthrough can deal extra _damage_ to the opponent when they attack enemy creatures. If their attack _damage_ is greater than the defending creature's defense, the excess _damage_ is dealt to the opponent.
  - **Charge**: Creatures with Charge can attack the turn they are summoned.
  - **Drain**: Creatures with Drain heal the player of the amount of the _damage_ they deal (when attacking only).
  - **Guard**: Enemy creatures from the same lane must attack creatures with Guard first.
  - **Lethal**: Creatures with Lethal kill the creatures they deal _damage_ to.
  - **Ward**: Creatures with Ward ignore once the next _damage_ they would receive from any source. The "shield" given by the Ward ability is then lost.

### Items

- When played, **items** have an immediate and permanent effect on the board or on the players. They are then removed from play.
- Items have a cost in mana and one or multiple effects out of the following:
- Permanent modifier of a creature's attack and/or defense characteristics. Example: +0/+2 or -1/-1.
- The addition or removal of one or more abilities to one creature.
- Additional card draw the next turn they're played.
- Health gain for the player or health loss for the opponent.
- There are three types of **items**:
  - **Green items** should target the active player's creatures. They have a positive effect on them.
  - **Red items** should target the opponent's creatures. They have a negative effect on them.
  - **Blue items** can be played with the "no creature" target identifier (**-1**) to give the active player a positive effect or cause _damage_ to the opponent, depending on the card. Blue items with negative defense points can also target enemy creatures.


## Gameplay

### Possible Actions
- `SUMMON id lane` to summon the creature `id` from your hand to the lane `lane` (0 - left, 1 - right).
- `ATTACK id1 id2` to attack creature `id2` with creature id1 that has to be on the same lane.
- `ATTACK id -1` to attack the opponent directly with creature `id`.
- `USE id1 id2` to use item `id1` on creature `id2`.
- `USE id -1` to use item `id`.
- `PASS` to do nothing this turn.

A player can do any number of valid actions during one turn. Actions must be separated by a semi-colon `;`.

### Game End
The game is over once any player reaches **0** or less HP.


## Victory Conditions
- Reduce your opponent Health Points (HP) from **30** to **0** or less.

## Loss Conditions
- Your HP gets reduced to **0** or less.
- You do not respond in time or output an unrecognized command.


## Advanced Details

### Runes
- Each player has **5** runes corresponding to the **25**, **20**, **15**, **10** and **5** HP thresholds.
- The first time a player's HP go below one of these thresholds, that player loses a rune and will draw an additional card at the beginning of the next turn. A maximum of 5 cards can thus be drawn this way during the entire game.
- When players have no more cards in their decks and must draw a card, they lose a rune and reach the corresponding HP threshold. 
- Example: a player has 23 HP, 4 runes remaining and no more cards in the deck. If that player must draw a card, the player loses a rune (the 20 HP rune) and 3 HP to reach 20.
- If a player has no more runes, no more cards in the deck and must draw a card, that player's HP reaches 0.

### Constraints
- If a player already has the maximum number of **8** cards in hand and must draw, the draw is cancelled.
- If a player already has the maximum number of **3** creatures on a lane and tries summoning a new one on this lane, the summoning action is cancelled.
- If a player tries to attack an untargetable target (wrong instance id or presence of other defensive creatures with Guard) with one of his creatures, the attack action is cancelled.
- Once a player has played over **50** turns, their deck is considered empty.

### Abilities special cases
- Giving an ability to a creature with that same ability has no effect.
- Attacking a creature with Ward with a creature with Lethal does not kill the creature (since no _damage_ is dealt to the creature).
- Attacking a creature with Ward with a creature with Breakthrough never deals excess _damage_ to the opponent (since no _damage_ is dealt to the creature).
- Attacking a creature with Ward with a creature with Drain does no heal the player (since no _damage_ is dealt to the creature).



## Game Input
### Input for one game turn

_**First 2 lines**_: for each player, `playerHealth`, `playerMana`, `playerDeck` and `playerRune`:
- Integer `playerHealth`: the remaining HP of the player.
- Integer `playerMana`: the current maximum mana of the player.
- Integer `playerDeck`: the number of cards in the player's deck. During the Draft phase, the second player has less card in his deck than his opponent.
- Integer `playerRune`: the next remaining rune of a player.
- Integer `playerDraw`: the additional number of drawn cards - this turn draw for the player, next turn draw (without broken runes) for the opponent.

The player's input comes first, the opponent's input comes second.

During the Draft phase, `playerMana` is always **0**.

_**Next line**_:
- Integer `opponentHand`, the total number of cards in the opponent's hand. These cards are hidden until they're played.
- Integer `opponentActions`, the number of actions performed by the opponent during his last turn.

_**Next `opponentActions` lines**_: for each opponent's action, string `cardNumberAndAction` containing the `cardNumber` of the played card, followed by a space, followed by the action associated with this card (see [Possible Actions](#Possible-Actions) section).

_**Next line**_: Integer `cardCount`: during the Battle phase, the total number of cards on the board and in the player's hand. During the Draft phase, always **3**.

_**Next `cardCount` lines**_: for each card, `cardNumber`, `instanceId`, `location`, `cardType`, `cost`, `attack`, `defense`, `abilities`, `myhealthChange`, `opponentHealthChange`, `cardDraw` and `lane`:
- Integer `cardNumber`: the identifier of a card (see [complete list of cards](https://jakubkowalski.tech/Projects/LOCM/cardlist.html)).
- Integer `instanceId`: the identifier representing the instance of the card (there can be multiple instances of the same card in a game).
- Integer `location`, during the Battle phase:
  - **0**: in the player's hand
  - **1**: on the player's side of the board
  - **-1**: on the opponent's side of the board

Always **0** during the Draft phase.

- Integer `cardType`:
  - **0**: Creature
  - **1**: Green item
  - **2**: Red item
  - **3**: Blue item

- Integer `cost`: the mana cost of the card,
- Integer `attack`:
  - Creature: its attack points
  - Item: its attack modifier
- Integer `defense`:
  - Creature: its defense points
  - Item: its defense modifier. Negative values mean this causes damage.
- String `abilities` of size **6**: the abilities of a card. Each letter representing an ability (**B** for Breakthrough, **C** for Charge and **G** for Guard, **D** for Drain, **L** for Lethal and **W** for Ward).
- Integer `myHealthChange`: the health change for the player.
- Integer `opponentHealthChange`: the health change for the opponent.
= Integer `cardDraw`: the additional number of cards drawn next turn for the player.
- Integer `lane`:
  - Creature on board: 0 - left, 1 - right
  - Other: -1


### Output for one game turn of the Draft

- `PICK nb` where `nb` equals **0**, **1** or **2** to choose one of the three proposed cards to add to your deck.
- `PASS` to do nothing (picks the 1st card by default).

### Output for one game turn of the Card Battle
The available actions are:
- `SUMMON id lane` to summon the **creature** of instanceId `id` from the player's hand to the lane `lane` (0 - left, 1 - right).
- `ATTACK idAttacker idTarget` to attack an opposing creature or opposing player of instanceId `idTarget` with a creature on the board of instanceId `idAttacker`.

  `idTarget` can be the "no-creature" identifier **-1**. It is used to attack the opponent directly.
- `USE idCard idTarget` to use an **item** of instanceId `idCard` on a creature of instanceId `idTarget` or without a target with the "no-creature" identifier **-1**.
- `PASS` to do nothing.

Players may use several actions by using a semi-colon `;`. 

Players may append text to each of their actions, it will be displayed in the viewer. 

Example: `SUMMON 3 1;ATTACK 4 5 yolo; ATTACK 8 -1 no fear`.

### Constraints

- 0 ≤ cost ≤ 12
- 0 ≤ creatures on each lane of the board (per player) ≤ 3
- 0 ≤ cards in hand ≤ 8


- Response time for the first draft turn ≤ 1000ms
- Response time for the first battle turn ≤ 1000ms
- Response time per turn ≤ 200ms


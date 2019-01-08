# Strategy Card Game AI Competition

Strategy Card Game AI Competition is organized for [IEEE CEC 2019](http://www.cec2019.org/index.html) conference.

- **[Competition website](https://jakubkowalski.tech/Projects/LOCM/CEC19/index.html)**
- Submission deadline: **19 May 2019, 23:59 GMT**

![/game artwork/](https://jakubkowalski.tech/Projects/LOCM/CEC19/artwork_small.jpg)


Legends of Code and Magic (LOCM) is a small implementation of a Strategy Card Game, designed to perform AI research. 
Its advantage over the real cardgame AI engines is that it is much simpler to handle by the agents, and thus allows testing more sophisticated algorithms and quickly implement theoretical ideas.
  
All cards effects are deterministic, thus the nondeterminism is introduced only by the ordering of cards and unknown opponent's deck. 
The game board consists of two lines (similarly as in TES:Legends), so it favors deeper strategic thinking.
Also, LOCM is based on the fair arena mode, i.e., before every game, both players create their decks secretly from the symmetrical yet limited choices. Because of that, the deckbuilding is dynamic and cannot be simply reduced to using human-created top-meta decks.
  
This competition aims to play the same role for [Hearthstone AI Competition](https://dockhorn.antares.uberspace.de/wordpress/) as [microRTS](https://sites.google.com/site/micrortsaicompetition/home) plays for various StarCraft AI contests.
Encourage advanced research, free of drawbacks of working with the full-fledged game. In this domain, it means i.a. embedding deckbuilding into the game itself (limiting the usage of premade decks), and allowing efficient search beyond the one turn depth.
  
The contest is based on the LOCM 1.2. One-lane, 1.0 version of the game, has been used for [CodinGame contest](https://www.codingame.com/leaderboards/challenge/legends-of-code-and-magic-marathon/global) in August 2018.

![/game screens/](https://jakubkowalski.tech/Projects/LOCM/CEC19/screensrow.png)



## Getting Started

### Online play
You can play LOCM 1.2 online, via the [CodinGame IDE](https://www.codingame.com/contribute/view/162759566f5a132f64b4de78ed637a2f309a) (click "PREVIEW" to run IDE and see game rules).

  Source code can be written directly in IDE or you can use [CG Sync](https://www.codingame.com/forum/t/codingame-sync-beta/614) to synchronize IDE code with your local file

### Offline referee
To run the game engine locally you can use the [referee jar](referee-nim/LoCM.jar). The most important options are:
- `-p1 <player1 command line>` where you put command to run your local first player bot
- `-p2 <player2 command line>` where you put command to run your local second player bot
- `-s` _(optional)_ to run server with visualization (at `http://localhost:8888/test.html`)

Thus, example usage is: 

```java -jar .\LoCM.jar -p1 "python3 PlayerExample.py3"  -p2 "python3 PlayerExample.py3" -s```

Running the jar without any options will show the extended readme.

Example player algorithms can be found [here](referee-nim/Research/PlayerAlgorithms). Source code of the referee is [here](referee-java/).

### Offline runner

To run multiple instances of the game you can use the nim-based runner documented [here](referee-nim/).



## Game Rules

- [Short introduction to the game]()
- [Markdown version](GAME-RULES.md)
- [Image version](jakubkowalski.tech/Projects/LOCM/CEC19/rules.html)
- [List of cards](https://jakubkowalski.tech/Projects/LOCM/cardlist.html)






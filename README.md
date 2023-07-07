# Strategy Card Game AI Competition

## **The competition is no longer organized**

<br>

**Article about the SCGAI competition history:**

**[Summarizing Strategy Card Game AI Competition](https://arxiv.org/pdf/2305.11814.pdf)**

Jakub Kowalski, Radosław Miernik; IEEE Conference on Games, 2023 [[cite]](https://jakubkowalski.tech/Publications/Kowalski2023SummarizingStrategy.bib)

<br>

**We are organizing a new cardgame-related contest: [Tales of Tribute AI Competition](https://github.com/ScriptsOfTribute)**
<br><br>

![/game artwork/](https://jakubkowalski.tech/Projects/LOCM/CEC19/artwork_small.jpg)




## Getting Started

Partially deprecated - work in progress.

### Online play
You can play LOCM 1.5 online, via the [CodinGame IDE](https://www.codingame.com/contribute/view/11103db118e4111aaadd2a9eb64f2a21d1f75) (click "PREVIEW" to run IDE and see game rules).

  Source code can be written directly in IDE or you can use [CG Sync](https://www.codingame.com/forum/t/codingame-sync-beta/614) to synchronize IDE code with your local file

### Offline referee
To run the game engine locally you can use the [referee1.5 jar](referee1.5-java/LoCM1.5.jar). The most important options are:
- `-p1 <player1 command line>` where you put command to run your local first player bot
- `-p2 <player2 command line>` where you put command to run your local second player bot
- `-s` _(optional)_ to run server with visualization (at `http://localhost:8888/test.html`)

Thus, example usage is: 

```java -jar .\LoCM1.5.jar -p1 "python3 PlayerExample.py3"  -p2 "python3 PlayerExample.py3" -s```

Running the jar without any options will show the extended readme.

Example player algorithms can be found [here](referee-nim/Research/PlayerAlgorithms). Source code of the referee is [here](referee-java/).

### Offline runner

To run multiple instances of the game you can use the nim-based runner documented [here](referee-nim/).






Added 1.5 jar to referee1.5-java, moved 1.2 jar from nim directory to java

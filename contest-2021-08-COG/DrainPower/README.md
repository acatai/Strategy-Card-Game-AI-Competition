# LocmContest

## Legend of Code And Magic 1.2 contest submit

An agent to play Legend of Code And Magic 1.2 ( https://www.codingame.com/ide/demo/68194451cf54dd36cc8c817f355e5a44a06062 )

Consists of few modules extracted from 1.0 version - it's mostly driven by simulation of possible game states and scoring function which indicates how good a certain state is.
It's quite aggresive and tries to defeat opponent creatures if the trade is worthwhile. Drain and guard seem to be very powerful and useful.
It has opponent lethal detection module as well as player lethal detection - it tries to prevent player's lethal whenever possible.
In future I would really like to use deck tracking and opponent card predictions in order to enhance bot's actions - but this feature is not available as of right now.

There are currently two strategies: default and aggresive one, the only difference between those are weights in game state scoring so both are quite similar in nature.

# Running code on linux

In order to run the code on linux:

```
sudo apt update
sudo apt install mono-complete
mcs -out: gabbek_locm_bot.exe results.cs
mono gabbek_locm_bot.exe
```

The bot can be run with two different strategies:

1) `gabbek_locm_bot.exe` - runs with default, probably better strategy
2) `gabbek_locm_bot.exe aggresive` - runs with aggresive strategy

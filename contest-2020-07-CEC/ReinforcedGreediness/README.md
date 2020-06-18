# reinforced-greediness

>*"Dermatoplastic shepard scratches its reinforced greediness by formulating without shock."* — random text on the web

This is a bot for Legends of Code and Magic submitted to the [IEEE CEC 2020's Strategy Card Game AI Competition](https://jakubkowalski.tech/Projects/LOCM/CEC20). Made by Ronaldo Vieira, Luiz Chaimowicz and Anderson Tavares from Universidade Federal de Minas Gerais and Universidade Federal do Rio Grande do Sul.

## Dependencies
Our bot requires Python 3.6+ and the numpy, scipy and sortedcontainers libraries. They can by installed by:
```
pip install numpy scipy sortedcontainers
```

## Usage
```
python agent.py
```

## Draft strategy
We use neural networks to choose cards. They are trained by reinforcement learning in a competitive self-play setting, 
and a separate network is used when playing as first player and second player. This is part of Ronaldo's master's thesis.

## Playing strategy
We find the best combination of actions with a best-first search that considers only the current turn. A simplified 
version of the forward model available in the [gym-locm](https://github.com/ronaldosvieira/gym-locm) project is used. 
Our state evaluation function is formed by a linear combination of hand-made features, with coefficients found via 
Bayesian optimization.

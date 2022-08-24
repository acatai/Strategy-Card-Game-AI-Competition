# Inspirai LoCM

## Dependencies
Python 3.7.4
```shell
pip install -r requirements.txt
```

## Usage
```shell
python agent.py
```

## Description
Our agent is built with two main components: a score function for the constructed phase and a neural network for the battle phase.
The structure of our score function is adapted from `Coac` and its hyperparameters are optimized using Bayesian Optimization.
The neural network is trained by self-play from scratch using PPO. To ease training, we use a modified game simulator from `ReinforcedGreediness` to update the in-turn game state and mask invalid actions.

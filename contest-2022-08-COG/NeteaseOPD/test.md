# For testing purpose

`main.py` is our current version AI, and `evaluate.py` is a baseline agent for testing. On our machine, the win rate of `main.py` compared to `evaluate.py` is about 94%, and the error rate of `main.py` is about 0.0%. If the test results differ significantly, then there is something wrong.

We run the test by following https://github.com/acatai/Strategy-Card-Game-AI-Competition/blob/master/contest-2021-08-COG/run.sh, except we set "cardGenSeed=$SEED1 seed=$SEED2 shufflePlayer0Seed=$SEED2 shufflePlayer1Seed=$SEED2" for LOCM 1.5. Based on the python environment described in `README.md`, the Java referee player command line for `main.py` and `evaluate.py` are:

```shell
/home/python3.7.7/bin/python3.7 NeteaseOPD/main.py
/home/python3.7.7/bin/python3.7 NeteaseOPD/evaluate.py
```

# ByteRL LOCM 1.2, version C
An agent that plays LoCM 1.2.

## Description
Our submission is indebted to [gym-locm project](https://github.com/ronaldosvieira/gym-locm), 
from which much code is borrowed.

In this submission,
both the Draft-Phase policy and the Battle-Phase policy are learned end-to-end via Fictitious Self-Play and Deep Reinforcement Learning.
The training is done with our proprietary RL framework,
which is not included in this submitted code and is planned to open-source in near future.
The submitted code only runs in testing-time for competition/evaluation, 
where the trained NN model has been provided 
(See `agent.py` for neural net architecture and `Agent.weights` for weights&biases).


## Install and Run
Following the COG 2021 instruction, we provide two possible ways, `Bare Machine` and `Virtual Env`, 
to install and run the full agent.
`Bare Machine` way is preferred.
However, in case the `Bare Machine` way conflicts with other submitted agent in Python version and/or package version,
please alternatively use the `Virtual Env` way.

### Bare Machine
The code is tested with Python 3.7 and `numpy==1.21.5`. Install the dependencies by:
```bash
pip3 install numpy==1.21.5
```
Then run the agent:
```bash
python3 locm1d2_submit.py
```
To test it with java referee, run the command:
```bash
java -jar /full/path/to/LoCM.jar \
    -p1 "python3 /full/path/to/byterl_locm1d2_c/locm1d2_submit.py" \
    -p2 "python3 /full/path/to/byterl_locm1d2_c/locm1d2_submit.py" \
    -s
```

### Virtual Env
First install `miniconda` (e.g., [from here](https://docs.conda.io/en/latest/miniconda.html)), 
and create a virtual env named `brl_locm_submit` with Python 3.7:
```bash
conda create -n brl_locm_submit python=3.7
```
Then activate the virtual env and install the dependencies within it:
```bash
conda activate brl_locm_submit
pip3 install numpy==1.21.5
```
To run the agent, use the full Python 3 path from the virtual env `brl_locm_submit` where the installed dependencies are ready:
```bash
/your/miniconda/path/envs/brl_locm_submit/bin/python3 locm1d2_submit.py
```
Note:
* When running the full agent command, you don't need (and should not) activate the virtual env; you need only provide the correct full python3 path from the virtual env.
* `/your/miniconda/path` is where the miniconda is installed in your machine, and all virtual envs should be found in the `/your/miniconda/path/envs` directory.

To test it with java referee, run the command:
```bash
java -jar /full/path/to/LoCM.jar \
    -p1 "/your/miniconda/path/envs/brl_locm_submit/bin/python3 /full/path/to/byterl_locm1d2_c/locm1d2_submit.py" \
    -p2 "/your/miniconda/path/envs/brl_locm_submit/bin/python3 /full/path/to/byterl_locm1d2_c/locm1d2_submit.py" \
    -s
```

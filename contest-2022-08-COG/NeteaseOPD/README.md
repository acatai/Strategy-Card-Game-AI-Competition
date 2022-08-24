# NeteaseOPD

Submission of the [Strategy Card Game AI Competition IEEE COG 2022](https://legendsofcodeandmagic.com/COG22/).

Authors: Jianming Gao, Yunkun Li, Yali Shangguan and Zhaohao Liang from Netease Game OPD.

## Description

NeteaseOPD is a reinforcement learning agent.
We use PPO and self-play to train policies to act in deck construction phase and battle phase. In order to simulate game states, we modify [gym-locm](#gym-locm), a [gym](https://github.com/openai/gym) environment for LOCM 1.2, to environment for LOCM 1.5. We use [RLlib](https://github.com/ray-project/ray) for training and use [ONNX Runtime](#onnxruntime) for inference.
In addition to the RL policies, we search for a combination of actions that can defeat opponent in one turn each battle phase turn.

## How to Run

NeteaseOPD is a python agent. To run it:

1. Extract our `.zip` file. The directory structure is as follows:

    ```text
    NeteaseOPD
    ├── README.md
    ├── config.py
    ├── gym_locm
    │   ├── agents.py
    │   ├── base_env.py
    │   ├── battle_env.py
    │   ├── card.py
    │   ├── custom_rl_agents.py
    │   ├── draft_env.py
    │   ├── engine.py
    │   ├── exceptions.py
    │   └── util.py
    ├── main.py
    ├── models
    │   ├── battle_model.onnx
    │   └── draft_model.onnx
    └── serving_utils.py
    ```

2. compile python from scratch with '--enable-optimizations' flags to accelerate our algorithm

    ```shell
    # install dependency
    apt-get install -y gcc make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev

    # download python3.7.7 tgz and untar
    PYTHON_TEMP="/home/python_temp"
    PYTHON_LOCATION="/home/python3.7.7"
    mkdir ${PYTHON_TEMP} && cd ${PYTHON_TEMP} && wget https://www.python.org/ftp/python/3.7.7/Python-3.7.7.tgz && tar -xzvf Python-3.7.7.tgz

    # configure with optimizations
    cd ${PYTHON_TEMP}/Python-3.7.7 && ./configure --enable-optimizations --prefix=${PYTHON_LOCATION}
    
    # make and make install (this will cost about 30 minutes)
    make -j 8 && make install && make clean
   
    # upgrade pip
    ${PYTHON_LOCATION}/bin/pip3 install --upgrade pip
   
    # install requirements
    ${PYTHON_LOCATION}/bin/pip3 install gym==0.19.0 numpy==1.18.5 onnxruntime==1.8.0 cython==0.29.23 llvmlite==0.37.0 numba==0.54.0 onnx==1.9.0 six==1.13.0
   
    # python3.7.7 bin in ${PYTHON_LOCATION}/bin/python3.7
    ```

3. The Java referee player command line:

    ```shell
    ${PYTHON_LOCATION}/bin/python3.7 NeteaseOPD/main.py
    ```

## References

1. <span id="gym-locm">Vieira, R., Rocha Tavares, A., & Chaimowicz, L. (2020). OpenAI Gym Environments for Legends of Code and Magic (Version 1.2.0) [Computer software]. https://github.com/ronaldosvieira/gym-locm</span>

2. <span id="onnxruntime">, O. R. D. (2018). ONNX Runtime [Computer software]. https://github.com/microsoft/onnxruntime</span>

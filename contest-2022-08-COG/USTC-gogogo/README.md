# Name of authors
Lu YuDong, student of University of Science and Technology of China(USTC)
Zhao Jian, student of USTC

# Bot Name
We submit two bots made by different methods

## First: 
    Parameter_control

Corresponding file:

    Param.py

## Second: 
    Zero_control

Corresponding file:

    Zero.py

    model.py
    
    model.ckpt

# How to run the bot
## First: 
needs:

    python==3.8 

to start in bash, run:

    python3 Param.py

## Second: 
needs:

    tensorflow==2.9.0 

    python==3.8

to start in bash, run:

    python3 Zero.py

# Description
Both bots model the intermediate process of each round, with the bot considering only the optimal single decision for the current situation each time.

For the Parameter_control:

    We use hyperparameters to control the selection and playing phases

For the Zero_control:

    We use hyperparameters to control the card selection phase. At the same time, the playing phase is controlled with the model obtained by reinforcement learning
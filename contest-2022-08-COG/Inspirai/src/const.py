##### main
agent_name = None
self_model = None
fself_model = None

model = None
obs = None
state = None
reward = None
done = None
value = None
attention = None


##### pipeline
step = None
replay = None
summary = None
last_obs = None
post_obs = None
last_action = None
trajectory_len = None
agent2id = None
agent2model = None
agent2action = None
last_potentials = None

##### features
players = None
cards = None
lanes = None
common = None
end = None
temperature = None

##### actions
card = None
card_prob = None
card_mask = None
card_valid = None
target = None
target_prob = None
target_mask = None
target_valid = None

##### env


globals().update({
    k: k for k in globals()
})

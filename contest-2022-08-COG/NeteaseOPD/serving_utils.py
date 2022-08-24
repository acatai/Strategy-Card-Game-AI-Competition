import numpy as np

# from ray.rllib.models.preprocessors import get_preprocessor
# 为了防超时不import ray

import gym
from typing import List
from collections import OrderedDict


OBS_VALIDATION_INTERVAL = 100
MODEL_DEFAULTS = {
    # Experimental flag.
    # If True, try to use a native (tf.keras.Model or torch.Module) default
    # model instead of our built-in ModelV2 defaults.
    # If False (default), use "classic" ModelV2 default models.
    # Note that this currently only works for:
    # 1) framework != torch AND
    # 2) fully connected and CNN default networks as well as
    # auto-wrapped LSTM- and attention nets.
    "_use_default_native_models": False,

    # === Built-in options ===
    # FullyConnectedNetwork (tf and torch): rllib.models.tf|torch.fcnet.py
    # These are used if no custom model is specified and the input space is 1D.
    # Number of hidden layers to be used.
    "fcnet_hiddens": [256, 256],
    # Activation function descriptor.
    # Supported values are: "tanh", "relu", "swish" (or "silu"),
    # "linear" (or None).
    "fcnet_activation": "tanh",

    # VisionNetwork (tf and torch): rllib.models.tf|torch.visionnet.py
    # These are used if no custom model is specified and the input space is 2D.
    # Filter config: List of [out_channels, kernel, stride] for each filter.
    # Example:
    # Use None for making RLlib try to find a default filter setup given the
    # observation space.
    "conv_filters": None,
    # Activation function descriptor.
    # Supported values are: "tanh", "relu", "swish" (or "silu"),
    # "linear" (or None).
    "conv_activation": "relu",

    # Some default models support a final FC stack of n Dense layers with given
    # activation:
    # - Complex observation spaces: Image components are fed through
    #   VisionNets, flat Boxes are left as-is, Discrete are one-hot'd, then
    #   everything is concated and pushed through this final FC stack.
    # - VisionNets (CNNs), e.g. after the CNN stack, there may be
    #   additional Dense layers.
    # - FullyConnectedNetworks will have this additional FCStack as well
    # (that's why it's empty by default).
    "post_fcnet_hiddens": [],
    "post_fcnet_activation": "relu",

    # For DiagGaussian action distributions, make the second half of the model
    # outputs floating bias variables instead of state-dependent. This only
    # has an effect is using the default fully connected net.
    "free_log_std": False,
    # Whether to skip the final linear layer used to resize the hidden layer
    # outputs to size `num_outputs`. If True, then the last hidden layer
    # should already match num_outputs.
    "no_final_linear": False,
    # Whether layers should be shared for the value function.
    "vf_share_layers": True,

    # == LSTM ==
    # Whether to wrap the model with an LSTM.
    "use_lstm": False,
    # Max seq len for training the LSTM, defaults to 20.
    "max_seq_len": 20,
    # Size of the LSTM cell.
    "lstm_cell_size": 256,
    # Whether to feed a_{t-1} to LSTM (one-hot encoded if discrete).
    "lstm_use_prev_action": False,
    # Whether to feed r_{t-1} to LSTM.
    "lstm_use_prev_reward": False,
    # Whether the LSTM is time-major (TxBx..) or batch-major (BxTx..).
    "_time_major": False,

    # == Attention Nets (experimental: torch-version is untested) ==
    # Whether to use a GTrXL ("Gru transformer XL"; attention net) as the
    # wrapper Model around the default Model.
    "use_attention": False,
    # The number of transformer units within GTrXL.
    # A transformer unit in GTrXL consists of a) MultiHeadAttention module and
    # b) a position-wise MLP.
    "attention_num_transformer_units": 1,
    # The input and output size of each transformer unit.
    "attention_dim": 64,
    # The number of attention heads within the MultiHeadAttention units.
    "attention_num_heads": 1,
    # The dim of a single head (within the MultiHeadAttention units).
    "attention_head_dim": 32,
    # The memory sizes for inference and training.
    "attention_memory_inference": 50,
    "attention_memory_training": 50,
    # The output dim of the position-wise MLP.
    "attention_position_wise_mlp_dim": 32,
    # The initial bias values for the 2 GRU gates within a transformer unit.
    "attention_init_gru_gate_bias": 2.0,
    # Whether to feed a_{t-n:t-1} to GTrXL (one-hot encoded if discrete).
    "attention_use_n_prev_actions": 0,
    # Whether to feed r_{t-n:t-1} to GTrXL.
    "attention_use_n_prev_rewards": 0,

    # == Atari ==
    # Which framestacking size to use for Atari envs.
    # "auto": Use a value of 4, but only if the env is an Atari env.
    # > 1: Use the trajectory view API in the default VisionNets to request the
    #      last n observations (single, grayscaled 84x84 image frames) as
    #      inputs. The time axis in the so provided observation tensors
    #      will come right after the batch axis (channels first format),
    #      e.g. BxTx84x84, where T=num_framestacks.
    # 0 or 1: No framestacking used.
    # Use the deprecated `framestack=True`, to disable the above behavor and to
    # enable legacy stacking behavior (w/o trajectory view API) instead.
    "num_framestacks": "auto",
    # Final resized frame dimension
    "dim": 84,
    # (deprecated) Converts ATARI frame to 1 Channel Grayscale image
    "grayscale": False,
    # (deprecated) Changes frame to range from [-1, 1] if true
    "zero_mean": True,

    # === Options for custom models ===
    # Name of a custom model to use
    "custom_model": None,
    # Extra options to pass to the custom classes. These will be available to
    # the Model's constructor in the model_config field. Also, they will be
    # attempted to be passed as **kwargs to ModelV2 models. For an example,
    # see rllib/models/[tf|torch]/attention_net.py.
    "custom_model_config": {},
    # Name of a custom action distribution to use.
    "custom_action_dist": None,
    # Custom preprocessors are deprecated. Please use a wrapper class around
    # your environment instead to preprocess observations.
    "custom_preprocessor": None,

    # Deprecated keys:
    # Use `lstm_use_prev_action` or `lstm_use_prev_reward` instead.
    # "lstm_use_prev_action_reward": DEPRECATED_VALUE,
    # Use `num_framestacks` (int) instead.
    "framestack": True,
}

def legacy_patch_shapes(space: gym.Space) -> List[int]:
    """Assigns shapes to spaces that don't have shapes.

    This is only needed for older gym versions that don't set shapes properly
    for Tuple and Discrete spaces.
    """

    if not hasattr(space, "shape"):
        if isinstance(space, gym.spaces.Discrete):
            space.shape = ()
        elif isinstance(space, gym.spaces.Tuple):
            shapes = []
            for s in space.spaces:
                shape = legacy_patch_shapes(s)
                shapes.append(shape)
            space.shape = tuple(shapes)

    return space.shape

class Preprocessor:
    """Defines an abstract observation preprocessor function.

    Attributes:
        shape (List[int]): Shape of the preprocessed output.
    """

    def __init__(self, obs_space: gym.Space, options: dict = None):
        legacy_patch_shapes(obs_space)
        self._obs_space = obs_space
        if not options:
            # from ray.rllib.models.catalog import MODEL_DEFAULTS
            self._options = MODEL_DEFAULTS.copy()
        else:
            self._options = options
        self.shape = self._init_shape(obs_space, self._options)
        self._size = int(np.product(self.shape))
        self._i = 0

    def _init_shape(self, obs_space: gym.Space, options: dict) -> List[int]:
        """Returns the shape after preprocessing."""
        raise NotImplementedError

    def transform(self, observation) -> np.ndarray:
        """Returns the preprocessed observation."""
        raise NotImplementedError

    def write(self, observation, array: np.ndarray,
              offset: int) -> None:
        """Alternative to transform for more efficient flattening."""
        array[offset:offset + self._size] = self.transform(observation)

    def check_shape(self, observation) -> None:
        """Checks the shape of the given observation."""
        if self._i % OBS_VALIDATION_INTERVAL == 0:
            if type(observation) is list and isinstance(
                    self._obs_space, gym.spaces.Box):
                observation = np.array(observation)
            try:
                if not self._obs_space.contains(observation):
                    raise ValueError(
                        "Observation ({}) outside given space ({})!",
                        observation, self._obs_space)
            except AttributeError:
                raise ValueError(
                    "Observation for a Box/MultiBinary/MultiDiscrete space "
                    "should be an np.array, not a Python list.", observation)
        self._i += 1

    @property
    def size(self) -> int:
        return self._size

    # @property
    # def observation_space(self) -> gym.Space:
    #     obs_space = gym.spaces.Box(-1., 1., self.shape, dtype=np.float32)
    #     # Stash the unwrapped space so that we can unwrap dict and tuple spaces
    #     # automatically in modelv2.py
    #     classes = (DictFlatteningPreprocessor, OneHotPreprocessor,
    #                RepeatedValuesPreprocessor, TupleFlatteningPreprocessor)
    #     if isinstance(self, classes):
    #         obs_space.original_space = self._obs_space
    #     return obs_space

class DictFlatteningPreprocessor(Preprocessor):
    """Preprocesses each dict value, then flattens it all into a vector.

    RLlib models will unpack the flattened output before _build_layers_v2().
    """

    def _init_shape(self, obs_space: gym.Space, options: dict) -> List[int]:
        assert isinstance(self._obs_space, gym.spaces.Dict)
        size = 0
        self.preprocessors = []
        for space in self._obs_space.spaces.values():
            preprocessor = get_preprocessor(space)(space, self._options)
            self.preprocessors.append(preprocessor)
            size += preprocessor.size
        return (size, )

    def transform(self, observation) -> np.ndarray:
        self.check_shape(observation)
        array = np.zeros(self.shape, dtype=np.float32)
        self.write(observation, array, 0)
        return array

    def write(self, observation, array: np.ndarray,
              offset: int) -> None:
        if not isinstance(observation, OrderedDict):
            observation = OrderedDict(sorted(observation.items()))
        assert len(observation) == len(self.preprocessors), \
            (len(observation), len(self.preprocessors))
        for o, p in zip(observation.values(), self.preprocessors):
            p.write(o, array, offset)
            offset += p.size


class OneHotPreprocessor(Preprocessor):
    """One-hot preprocessor for Discrete and MultiDiscrete spaces.

    Examples:
        >>> self.transform(Discrete(3).sample())
        ... np.array([0.0, 1.0, 0.0])
        >>> self.transform(MultiDiscrete([2, 3]).sample())
        ... np.array([0.0, 1.0, 0.0, 0.0, 1.0])
    """

    def _init_shape(self, obs_space: gym.Space, options: dict) -> List[int]:
        if isinstance(obs_space, gym.spaces.Discrete):
            return (self._obs_space.n, )
        else:
            return (np.sum(self._obs_space.nvec), )

    def transform(self, observation) -> np.ndarray:
        self.check_shape(observation)
        arr = np.zeros(self._init_shape(self._obs_space, {}), dtype=np.float32)
        if isinstance(self._obs_space, gym.spaces.Discrete):
            arr[observation] = 1
        else:
            for i, o in enumerate(observation):
                arr[np.sum(self._obs_space.nvec[:i]) + o] = 1
        return arr

    def write(self, observation, array: np.ndarray,
              offset: int) -> None:
        array[offset:offset + self.size] = self.transform(observation)

class NoPreprocessor(Preprocessor):
    def _init_shape(self, obs_space: gym.Space, options: dict) -> List[int]:
        return self._obs_space.shape

    def transform(self, observation) -> np.ndarray:
        self.check_shape(observation)
        return observation

    def write(self, observation, array: np.ndarray,
              offset: int) -> None:
        array[offset:offset + self._size] = np.array(
            observation, copy=False).ravel()

    @property
    def observation_space(self) -> gym.Space:
        return self._obs_space


def get_preprocessor(space: gym.Space) -> type:
    """Returns an appropriate preprocessor class for the given space."""

    legacy_patch_shapes(space)
    obs_shape = space.shape

    if isinstance(space, (gym.spaces.Discrete, gym.spaces.MultiDiscrete)):
        preprocessor = OneHotPreprocessor
    # elif obs_shape == ATARI_OBS_SHAPE:
    #     preprocessor = GenericPixelPreprocessor
    # elif obs_shape == ATARI_RAM_OBS_SHAPE:
    #     preprocessor = AtariRamPreprocessor
    elif isinstance(space, gym.spaces.Tuple):
        raise NotImplementedError()
        preprocessor = TupleFlatteningPreprocessor
    elif isinstance(space, gym.spaces.Dict):
        preprocessor = DictFlatteningPreprocessor
    # elif isinstance(space, Repeated):
    #     preprocessor = RepeatedValuesPreprocessor
    else:
        preprocessor = NoPreprocessor

    return preprocessor


class RLlibSavedModelServingUtils:
    """ """

    def __init__(self, observation_space) -> None:
        """
        observation_space(gym.Space)
        input_type(str):
            "": 每个特征分开处理，对应 input_dict["obs"]
            "flatten": 所有特征压平、拼接成一维，对应 input_dict["obs_flat"]
        """
        self.observation_space = observation_space

    def state_preprocess(self, state):
        """
        游戏状态转化为ray模型的输入形式
        """
        raise NotImplementedError

    def batch_to_tensor_inputs(self, samples):
        """
        samples(list)
        """
        raise NotImplementedError


class OnnxInputs:
    def __init__(self, policy_id="main") -> None:
        self.observations = "{}/obs:0".format(policy_id)
        self.prev_action = "{}/prev_actions:0".format(policy_id)
        self.prev_reward = "{}/prev_rewards:0".format(policy_id)

class OnnxOutputs:
    def __init__(self, policy_id="main") -> None:
        self.action_logp = "{}/cond_2/Merge:0".format(policy_id)
        self.action_dist_inputs = "{}/add:0".format(policy_id)
        self.vf_preds = "{}/Reshape_8:0".format(policy_id)
        self.action_prob = "{}/Exp:0".format(policy_id)
        self.actions_0 = "{}/cond_1/Merge:0".format(policy_id)

class RLlibObsFlatSavedModelONNXUtils(RLlibSavedModelServingUtils):
    """
    """

    def __init__(self, observation_space, policy_id="main") -> None:
        super().__init__(observation_space)

        self.fc_model_pp = get_preprocessor(observation_space)(observation_space)
        self.onnx_inputs = OnnxInputs(policy_id=policy_id)

    def state_preprocess(self, state):
        """
        游戏状态转化为ray内置FC模型的输入，对应 inputs['observations']
        """
        observation = self.fc_model_pp.transform(state)  # ndarray shape (-1, )
        return observation

    def batch_to_tensor_inputs(self, samples):
        """
        samples(list): observations
        """
        observations = samples
        assert isinstance(
            observations, list
        ), "observations must be list of observation"
        batch_size = len(observations)

        inputs = {
            self.onnx_inputs.observations: [],
            self.onnx_inputs.prev_action: [],
            self.onnx_inputs.prev_reward: [],
        }

        for observation in observations:

            temp = (
                observation.tolist()
                if isinstance(observation, np.ndarray)
                else observation
            )

            inputs[self.onnx_inputs.observations].append(temp)
            inputs[self.onnx_inputs.prev_action].append(0)
            inputs[self.onnx_inputs.prev_reward].append(0.0)

        return inputs

        
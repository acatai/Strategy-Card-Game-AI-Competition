from typing import Any

import numpy as np
import tensorflow.compat.v1 as tf
from tensorflow.compat.v1.keras.backend import get_session


def combined_shape(length, shape=None):
    if shape is None:
        return (length,)
    return (length, shape) if np.isscalar(shape) else (length, *shape)


def placeholder(dtype=tf.float32, shape=None):
    tf.disable_eager_execution()
    return tf.placeholder(dtype=dtype, shape=combined_shape(None, shape))

    

def mlp(x, hidden_sizes=(32,), activation=tf.tanh, output_activation=None):
    for h in hidden_sizes[:-1]:
        x = tf.layers.dense(x, units=h, activation=activation)
    return tf.layers.dense(x, units=hidden_sizes[-1], activation=output_activation)


class CategoricalPd:
    def __init__(self, logits):
        self.logits = logits

    def mode(self):
        return tf.argmax(self.logits, axis=-1)

    def logp(self, x):
        return -self.neglogp(x)

    def neglogp(self, x):
        # return tf.nn.sparse_softmax_cross_entropy_with_logits(logits=self.logits, labels=x)
        # Note: we can't use sparse_softmax_cross_entropy_with_logits because
        #       the implementation does not allow second-order derivatives...
        if x.dtype in {tf.uint8, tf.int32, tf.int64}:
            # one-hot encoding
            x_shape_list = x.shape.as_list()
            logits_shape_list = self.logits.get_shape().as_list()[:-1]
            for xs, ls in zip(x_shape_list, logits_shape_list):
                if xs is not None and ls is not None:
                    assert xs == ls, 'shape mismatch: {} in x vs {} in logits'.format(xs, ls)

            x = tf.one_hot(x, self.logits.get_shape().as_list()[-1])
        else:
            # already encoded
            assert x.shape.as_list() == self.logits.shape.as_list()

        return tf.nn.softmax_cross_entropy_with_logits_v2(logits=self.logits, labels=x)

    def kl(self, other):
        a0 = self.logits - tf.reduce_max(self.logits, axis=-1, keepdims=True)
        a1 = other.logits - tf.reduce_max(other.logits, axis=-1, keepdims=True)
        ea0 = tf.exp(a0)
        ea1 = tf.exp(a1)
        z0 = tf.reduce_sum(ea0, axis=-1, keepdims=True)
        z1 = tf.reduce_sum(ea1, axis=-1, keepdims=True)
        p0 = ea0 / z0
        return tf.reduce_sum(p0 * (a0 - tf.log(z0) - a1 + tf.log(z1)), axis=-1)

    def entropy(self):
        a0 = self.logits - tf.reduce_max(self.logits, axis=-1, keepdims=True)
        ea0 = tf.exp(a0)
        z0 = tf.reduce_sum(ea0, axis=-1, keepdims=True)
        p0 = ea0 / z0
        return tf.reduce_sum(p0 * (tf.log(z0) - a0), axis=-1)

    def sample(self):
        u = tf.random_uniform(tf.shape(self.logits), dtype=self.logits.dtype)
        return tf.argmax(self.logits - tf.log(-tf.log(u)), axis=-1)


class SCModel():
    def __init__(self, observation_space, action_space, config=None, model_id='0'):
        with tf.variable_scope(model_id):
            # self.info_ph = placeholder(shape=observation_space, dtype='float')
            # self.handcard_ph = placeholder(shape=observation_space, dtype='float')
            # self.my_boardcard_ph = placeholder(shape=observation_space, dtype='float')
            # self.opp_boardcard_ph = placeholder(shape=observation_space, dtype='float')
            self.x_ph = placeholder(shape=observation_space, dtype=tf.float32)
            self.a_ph = placeholder(dtype=tf.int32)
            self.legal_action = tf.placeholder(dtype= tf.float32, shape=(None, action_space)) 
        self.logits = None
        self.vf = None

        # Initialize Tensorflow session
        self.sess = get_session()
        
        self.scope = model_id
        self.observation_space = observation_space
        self.action_space = action_space
        self.model_id = model_id
        self.config = config

        # Set configurations
        if config is not None:
            self.load_config(config)

        # Build up model
        self.build()

        # Build assignment ops
        self._weight_ph = None
        self._to_assign = None
        self._nodes = None
        self._build_assign()

        # Build saver
        self.saver = tf.train.Saver(tf.trainable_variables())

        pd = CategoricalPd(self.logits)
        self.action = pd.sample()
        self.neglogp = pd.neglogp(self.action)
        self.neglogp_a = pd.neglogp(self.a_ph)
        self.entropy = pd.entropy()
        self.sess.run(tf.global_variables_initializer())
        
    def forward(self, states, legal_action):
        return self.sess.run([self.action, self.vf, self.neglogp], feed_dict={self.x_ph: states, self.legal_action: legal_action})

    def build(self) -> None:
        with tf.variable_scope(self.scope):
            with tf.variable_scope('pi'):
                logits_without_mask = mlp(self.x_ph, [512, 512, 512, 512, 512, self.action_space], tf.tanh)
                # self.logits = logits_without_mask * self.legal_action + (1 - self.legal_action) * (-1e8)
                # self.logits = logits - tf.reduce_logsumexp(logits, axis=0, keepdims=True)
                self.logits = logits_without_mask + 1000. *tf.to_float(self.legal_action-1)

            with tf.variable_scope('v'):
                self.vf = tf.squeeze(mlp(self.x_ph, [512, 512, 512, 512, 512, 1], tf.tanh), axis=1)

    def set_weights(self, weights) -> None:
        feed_dict = {self._weight_ph[var.name]: weight
                     for (var, weight) in zip(tf.trainable_variables(scope=self.scope), weights)}

        self.sess.run(self._nodes, feed_dict=feed_dict)

    def get_weights(self) -> Any:
        return self.sess.run(tf.trainable_variables(self.scope))

    def _build_assign(self):
        self._weight_ph, self._to_assign = dict(), dict()
        variables = tf.trainable_variables(self.scope)
        for var in variables:
            self._weight_ph[var.name] = tf.placeholder(var.value().dtype, var.get_shape().as_list())
            self._to_assign[var.name] = var.assign(self._weight_ph[var.name])
        self._nodes = list(self._to_assign.values())

if __name__ == '__main__': 
    modeltest = SCModel(512, 146)
    tests = np.random.uniform(size=(1, 512))
    print(tests)
    testa = np.zeros(146, dtype=int)
    testa[5] = 1
    # testa[15] = 1
    # testa[25] = 1
    testa[35] = 1
    for _ in range(100):
        print(modeltest.forward(tests, [testa]))
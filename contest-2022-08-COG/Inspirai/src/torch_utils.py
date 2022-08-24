import torch
import numpy as np
import torch.nn.functional as F


class Lambda(torch.nn.Module):
    def __init__(self, func):
        super().__init__()
        self.func = func

    def forward(self, x):
        return self.func(x)


def to_tensor(obj, cuda=True):
    if isinstance(obj, list) or isinstance(obj, tuple):
        return type(obj)(to_tensor(o, cuda=cuda) for o in obj)
    elif isinstance(obj, dict):
        return {k: to_tensor(v, cuda=cuda) for k, v in obj.items()}
    elif isinstance(obj, np.ndarray):
        return to_tensor(torch.as_tensor(obj), cuda=cuda)
    else:
        assert isinstance(obj, torch.Tensor) or isinstance(obj, torch.nn.Module)
        return obj.cuda() if torch.cuda.is_available() and cuda else obj


def mask_prob(prob, mask):
    prob = (prob + 1e-10) * mask
    prob = prob + prob.eq(0).all(-1, keepdim=True)
    return prob / prob.sum(-1, keepdim=True)


def reshape_prob(prob, temperature):
    logit = (prob + 1e-10).log()
    logit = logit / temperature
    return torch.softmax(logit, -1)


def unsqueeze(obs):
    if isinstance(obs, dict):
        return {k: unsqueeze(v) for k, v in obs.items()}
    return obs[np.newaxis, ...]


def squeeze(action):
    if isinstance(action, dict):
        return {k: squeeze(v) for k, v in action.items()}
    return np.squeeze(action, axis=0)


########### dynamic lr ###########
class LRModifier:
    def __init__(self, optimizer: torch.optim.Optimizer):
        self.optimizer = optimizer
        self.lr = self.optimizer.param_groups[0]['lr']

    def modify(self, lr):
        if lr != self.lr:
            print(f'change lr from {self.lr} to {lr}')
            self.optimizer.param_groups[0]['lr'] = lr
            self.lr = lr


########### transformer output weights ###########
class MultiheadAttentionImp(torch.nn.MultiheadAttention):
    def forward(self, query, key, value, key_padding_mask=None, need_weights=True, attn_mask=None):
        attn_output, self.attn_output_weights = super().forward(query, key, value, key_padding_mask, need_weights, attn_mask)
        return attn_output, self.attn_output_weights


class TransformerEncoderLayerImp(torch.nn.TransformerEncoderLayer):
    def __init__(self, d_model, nhead, dim_feedforward=2048, dropout=0.1, activation=F.relu, layer_norm_eps=1e-5, batch_first=False, norm_first=False, device=None, dtype=None) -> None:
        super().__init__(d_model, nhead, dim_feedforward, dropout, activation, layer_norm_eps, batch_first, norm_first, device, dtype)
        factory_kwargs = {'device': device, 'dtype': dtype}
        self.self_attn = MultiheadAttentionImp(d_model, nhead, dropout=dropout, batch_first=batch_first, **factory_kwargs)

    # self-attention block
    def _sa_block(self, x, attn_mask, key_padding_mask):
        x = self.self_attn(x, x, x, attn_mask=attn_mask, key_padding_mask=key_padding_mask, need_weights=True)[0]
        return self.dropout1(x)

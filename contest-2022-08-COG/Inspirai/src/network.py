import torch
from torch.distributions import Categorical

from src import const, torch_utils
from src.features import encoders, feature_size


class Network(torch.nn.Module):
    def __init__(self):
        super().__init__()

        # encoders
        self.encoders = torch.nn.ModuleDict(encoders)

        # transformer
        self.transformer = torch.nn.TransformerEncoder(
            torch.nn.TransformerEncoderLayer(feature_size, nhead=4, dim_feedforward=feature_size, batch_first=True, dropout=0),
            num_layers=3
        )

        # value
        self.value_head = torch.nn.Sequential(
            torch.nn.Linear(feature_size, feature_size),
            torch.nn.ReLU(),
            torch.nn.Linear(feature_size, 1),
            torch.nn.Flatten(-2)
        )

        # actions
        self.card_attn = torch.nn.MultiheadAttention(feature_size, num_heads=1, batch_first=True)
        self.target_attn = torch.nn.MultiheadAttention(feature_size, num_heads=1, batch_first=True)

    def forward(self, obs, outputs_b=None):
        outputs = {}

        # encode
        features = {
            feature_name: encoder(obs[feature_name])
            for feature_name, encoder in self.encoders.items()
        }

        # aggregate
        feature_seq = torch.cat(list(features.values()), dim=1)
        padding_seq = torch.cat([
            obs[feature_name].eq(0).all(-1) if len(obs[feature_name].shape) == 3   # seq feature
            else obs[feature_name].new_zeros((obs[feature_name].size(0), 1)).bool()  # image feature
            for feature_name in features
        ], dim=1)
        padding_seq = padding_seq & ~padding_seq.all(1, keepdim=True)  # NOTE: flow adds all-zero samples in batch !
        feature_seq = self.transformer(feature_seq, src_key_padding_mask=padding_seq)   # [B, S, F]
        feature_final = feature_seq[:, 0]  # [B, F]
        # feature_mean = (feature_seq * (~padding_seq).unsqueeze(-1)).sum(1) / (~padding_seq).sum(-1, keepdim=True)    # [B, F]

        # value
        value = self.value_head(feature_final)
        outputs[const.value] = value

        # actions: sample card
        card_mask = obs[const.card_mask]
        card_prob = self.card_attn(query=feature_final.unsqueeze(1), key=feature_seq, value=feature_seq, key_padding_mask=padding_seq)[1][:, 0]  # [B, S]
        card_prob = torch_utils.mask_prob(card_prob, card_mask)  # [B, S]
        card_prob = torch_utils.reshape_prob(card_prob, obs[const.temperature][..., None].clip(1e-10))  # [B, S]
        card = outputs_b[const.card] if outputs_b else Categorical(card_prob).sample()  # [B]

        # actions: sample target
        B = feature_seq.size(0)
        card_feature = feature_seq[range(B), card]  # [B, F]
        target_mask = obs[const.target_mask][range(B), card]
        target_prob = self.target_attn(query=card_feature.unsqueeze(1), key=feature_seq, value=feature_seq, key_padding_mask=padding_seq)[1][:, 0]  # [B, S]
        target_prob = torch_utils.mask_prob(target_prob, target_mask)  # [B, S]
        target_prob = torch_utils.reshape_prob(target_prob, obs[const.temperature][..., None].clip(1e-10))  # [B, S]
        target = outputs_b[const.target] if outputs_b else Categorical(target_prob).sample()  # [B]

        outputs[const.card] = card
        outputs[const.target] = target
        outputs[const.card_prob] = card_prob
        outputs[const.target_prob] = target_prob

        return outputs

from abc import ABC, abstractmethod
from typing import Type

from gym_locm.engine import *


class Agent(ABC):
    @abstractmethod
    def seed(self, seed):
        pass

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def act(self, state):
        pass


class PassBattleAgent(Agent):
    def seed(self, seed):
        pass

    def reset(self):
        pass

    def act(self, state):
        return Action(ActionType.PASS)


PassDraftAgent = PassBattleAgent


draft_agents = {
    "pass": PassDraftAgent,
}

battle_agents = {
    "pass": PassBattleAgent,
}


def parse_draft_agent(agent_name: str) -> Type:
    return draft_agents[agent_name.lower().replace(" ", "-")]


def parse_battle_agent(agent_name: str) -> Type:
    return battle_agents[agent_name.lower().replace(" ", "-")]

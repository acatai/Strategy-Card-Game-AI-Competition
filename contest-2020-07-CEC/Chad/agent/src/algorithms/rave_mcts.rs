use std::collections::HashMap;

use derive_new::new;
use petgraph::prelude::*;
use rand::prelude::*;

use super::GameState;

#[derive(new)]
struct Node<State> {
    state: State,
    #[new(default)]
    score: f32,
    #[new(default)]
    visit: f32,
    #[new(default)]
    expanded: bool,
    #[new(default)]
    children: usize,
}

#[derive(Default, Copy, Clone)]
struct AMAFValue {
    pub score: f32,
    pub visit: f32,
}

pub struct RaveMCTS<Action, State> {
    pub root: NodeIndex,
    graph: DiGraph<Node<State>, Action>,
    exploration_constant: f32,
    amaf: HashMap<Action, AMAFValue>,
    amaf_smoothing: f32,
}

impl<Action, State> RaveMCTS<Action, State>
where
    State: GameState<Action = Action>,
    Action: Clone + std::hash::Hash + Eq,
{
    const FAST_SEARCH: bool = false;

    pub fn new(start_state: State, amaf_smoothing: f32, exploration_constant: Option<f32>) -> Self {
        let mut graph = DiGraph::new();
        let root = graph.add_node(Node::new(start_state));

        Self {
            graph,
            root,
            exploration_constant: exploration_constant.unwrap_or_else(|| (2.0f32).sqrt()),
            amaf: HashMap::default(),
            amaf_smoothing,
        }
    }

    fn get_best_child(&self, root: NodeIndex) -> Option<NodeIndex> {
        let get_score = |node: NodeIndex| self.graph[node].score / self.graph[node].visit;

        self.graph
            .neighbors_directed(root, Outgoing)
            .filter(|&a| self.graph[a].visit != 0.0)
            .max_by(|&a, &b| get_score(a).partial_cmp(&get_score(b)).unwrap())
    }

    fn expand(&mut self, node: NodeIndex) {
        let children = {
            let n = &mut self.graph[node];
            n.expanded = true;

            n.state.children()
        };

        let mut cnt = 0;

        for child in children {
            let (action, state) = child;
            let new_node = self.graph.add_node(Node::new(state));
            self.graph.add_edge(node, new_node, action);

            cnt += 1;
        }

        self.graph[node].children = cnt;
    }

    fn propagate(&mut self, node: NodeIndex, score: f32) {
        self.graph[node].score += score;
        self.graph[node].visit += 1.0;

        if let Some(edge) = self.graph.first_edge(node, Incoming) {
            let entry = self.amaf.entry(self.graph[edge].clone()).or_default();

            entry.score += score;
            entry.visit += 1.0;
        }

        if let Some(parent) = self.graph.neighbors_directed(node, Incoming).next() {
            self.propagate(parent, score);
        }
    }

    fn score(&self, node: NodeIndex) -> f32 {
        let (score, visits, parent_visits) = {
            let n = &self.graph[node];
            let p_n = &self.graph[self
                .graph
                .neighbors_directed(node, Incoming)
                .next()
                .unwrap()]; // NOTE(MarWit): This unwrap is safe as parent of node should always exist
            (n.score, n.visit, p_n.visit)
        };

        let amaf_value = self.get_amaf_value(node);
        let beta = (self.amaf_smoothing - visits).max(0.0) / self.amaf_smoothing;

        let mcts_score = score / visits;
        let amaf_score = amaf_value.score / amaf_value.visit;
        let total_score = beta * amaf_score + (1.0 - beta) * mcts_score;

        total_score + self.exploration_constant * (parent_visits.ln() / visits).sqrt()
    }

    fn get_amaf_value(&self, node: NodeIndex) -> AMAFValue {
        let edge = self.graph.first_edge(node, Incoming).unwrap();
        self.amaf
            .get(&self.graph[edge])
            .copied()
            .unwrap_or_else(AMAFValue::default)
    }

    fn select(&mut self, node: NodeIndex) -> NodeIndex {
        if !self.graph[node].expanded {
            self.expand(node);

            if self.graph[node].children == 0 {
                node
            } else {
                let mut rng = rand::thread_rng();
                self.graph
                    .neighbors_directed(node, Outgoing)
                    .choose(&mut rng)
                    .unwrap() // NOTE(MarWit): This unwrap is safe (given node
                              // have >0 children)
            }
        } else if self.graph[node].children == 0 {
            node
        } else {
            let children = self
                .graph
                .neighbors_directed(node, Outgoing)
                .collect::<Vec<_>>();

            let mut rng = rand::thread_rng();
            if let Some(new_node) = children
                .iter()
                .filter(|&n| self.graph[*n].visit == 0.0)
                .choose(&mut rng)
                .cloned()
            {
                return if Self::FAST_SEARCH {
                    self.select(new_node)
                } else {
                    new_node
                };
            }

            let new_parent = children
                .into_iter()
                .max_by(|&a, &b| self.score(a).partial_cmp(&self.score(b)).unwrap())
                .unwrap(); // NOTE(MarWit): This unwrap is safe as we know that
                           // children.len() > 0

            self.select(new_parent)
        }
    }

    pub fn eval(&mut self, node: NodeIndex) {
        let next_node = self.select(node);

        let node_data = &mut self.graph[next_node];
        let score = node_data.state.eval();

        self.propagate(next_node, score);
    }

    #[allow(dead_code)]
    pub fn get_best_action(&self) -> Action {
        let best_node = self.get_best_child(self.root).unwrap();
        let best_action_edge = self.graph.first_edge(best_node, Incoming).unwrap();
        // NOTE(MarWit): This is safe as every node have exactly one parent
        // (graph is tree)

        self.graph[best_action_edge].clone()
    }

    pub fn get_best_action_chain(&self) -> Vec<Action> {
        let mut current_node = self.root;
        let mut actions = vec![];

        while let Some(best_node) = self.get_best_child(current_node) {
            let best_action_edge = self.graph.first_edge(best_node, Incoming).unwrap();
            // NOTE(MarWit): This is safe as every node have exactly one parent
            // (graph is tree)
            actions.push(self.graph[best_action_edge].clone());
            current_node = best_node;
        }

        actions
    }
}

"""
Simulation of social network dynamics with aging connections,
modeling relationship formation and community evolution over time.
"""

from dynamic_walker.graph.dynamic_graph import DynamicGraph
from dynamic_walker.graph.biased_walker import BiasedRandomWalker
from dynamic_walker.visualization.animator import GraphAnimator

# Social network with community structure and relationship aging
social_params = {
    "strategy": "aging",
    "initial_nodes": 40,
    "max_degree": 15,
    "min_degree": 1,
    "target_components": 4,
    "min_component_size": 2,
    "edge_aging_factor": 0.85,
    "node_aging_factor": 0.95,
    "decay_factor": 0.9
}

social_graph = DynamicGraph(**social_params)

# Social agent navigating through activity and connections
social_walker_params = {
    "graph": social_graph,
    "bias_type": "activity",
    "teleport_probability": 0.2,
    "stay_probability": 0.05,
    "exploration_factor": 0.8,
    "adaptive_bias": True,
    "decay_factor": 0.85,
    "max_teleport_distance": 2,
    "min_weight": 0.05,
    "teleport_strategy": "uniform"
}

social_walker = BiasedRandomWalker(**social_walker_params)

# Social network evolution characteristics
social_evolution = {
    "node_add_prob": 0.04,
    "node_remove_prob": 0.003,
    "edge_add_prob": 0.3,
    "edge_remove_prob": 0.15,
    "triadic_prob": 0.6,
}

# Visualization with 800 steps at 50ms intervals
animator = GraphAnimator(social_graph, social_walker,steps=800,interval=50,**social_evolution)
animator.animate()

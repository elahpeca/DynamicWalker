"""
Simulation of stochastic network dynamics with random connectivity,
modeling emergent patterns in complex systems.
"""

from dynamic_walker.graph.dynamic_graph import DynamicGraph
from dynamic_walker.graph.biased_walker import BiasedRandomWalker
from dynamic_walker.visualization.animator import GraphAnimator

# Stochastic network with random connections and aging
stochastic_params = {
    "strategy": "random",
    "initial_nodes": 30,
    "max_degree": 8,
    "min_degree": 1,
    "target_components": 1,
    "min_component_size": 1,
    "edge_aging_factor": 0.92,
    "node_aging_factor": 0.99,
}

stochastic_net = DynamicGraph(**stochastic_params)

# Network navigator with weight-based movement
navigator_params = {
    "graph": stochastic_net,
    "bias_type": "weight",
    "teleport_probability": 0.1,
    "stay_probability": 0.1,
    "exploration_factor": 1.0,
    "adaptive_bias": False,
    "decay_factor": 0.9,
    "max_teleport_distance": 1,
    "min_weight": 0.1,
    "teleport_strategy": "component"
}

navigator = BiasedRandomWalker(**navigator_params)

# Stochastic network evolution parameters
evolution_params = {
    "node_add_prob": 0.02,
    "node_remove_prob": 0.005,
    "edge_add_prob": 0.4,
    "edge_remove_prob": 0.2,
    "triadic_prob": 0.3,
    "reconnection_prob": 0.15,
    "content_update_prob": 0.25
}

# Visualization with 800 steps at 50ms intervals
animator = GraphAnimator(stochastic_net, navigator, steps=800, interval=50, **evolution_params)
animator.animate()
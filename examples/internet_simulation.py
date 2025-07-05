"""
Simulation of internet-like network evolution with preferential attachment,
modeling web crawler behavior and network dynamics over time.
"""

from dynamic_walker.graph.dynamic_graph import DynamicGraph
from dynamic_walker.graph.biased_walker import BiasedRandomWalker
from dynamic_walker.visualization.animator import GraphAnimator

# Scale-free network with preferential attachment and aging components
internet_params = {
    "strategy": "preferential",
    "initial_nodes": 30,
    "max_degree": 10,
    "min_degree": 1,
    "target_components": 3,
    "min_component_size": 2,
    "edge_aging_factor": 0.95,
    "node_aging_factor": 0.98,
    "preferential_exponent": 1.1
}

internet_graph = DynamicGraph(**internet_params)

# Web crawler with exploration/exploitation balance and cross-component jumps
crawler_params = {
    "graph": internet_graph,
    "bias_type": "degree",
    "teleport_probability": 0.1,
    "stay_probability": 0.05,
    "exploration_factor": 1.1,
    "adaptive_bias": True,
    "decay_factor": 0.9,
    "max_teleport_distance": 2,
    "min_weight": 0.02,
    "teleport_strategy": "distant"
}

walker = BiasedRandomWalker(**crawler_params)

# Network evolution probabilities modeling real-world internet dynamics
evolution_params = {
    "node_add_prob": 0.02,
    "node_remove_prob": 0.003,
    "edge_add_prob": 0.2,
    "edge_remove_prob": 0.08,
    "triadic_prob": 0.4,
    "reconnection_prob": 0.15,
    "content_update_prob": 0.3
}

# Visualization with 800 steps at 50ms intervals
animator = GraphAnimator(internet_graph, walker, steps=800, interval=50, **evolution_params)
animator.animate()
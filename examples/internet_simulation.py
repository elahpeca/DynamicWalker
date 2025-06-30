from dynamic_walker.graph.dynamic_graph import DynamicGraph
from dynamic_walker.graph.biased_walker import BiasedRandomWalker
from dynamic_walker.visualization.animator import animate_simulation

# Internet-like graph simulation parameters
dynamic_graph = DynamicGraph(initial_nodes=10)
walker = BiasedRandomWalker(
    graph=dynamic_graph,
    bias_type="degree",  # Prefer high-degree nodes (popular pages)
    start_node=0,  # Starting point
    teleport_probability=0.15,  # PageRank-style random jumps
    stay_probability=0.05,  # Chance to stay on page
    exploration_factor=1.2,  # Moderate exploration boost
    adaptive_bias=True,  # Avoid recently visited pages
    decay_factor=0.95,  # Visit memory decay rate
    max_teleport_distance=0  # Can jump anywhere
)

# Start visualization
animate_simulation(
    dynamic_graph, 
    walker,
    steps=200,
    interval=300,
    node_add_prob=0.1,  # Rare site additions
    edge_add_prob=0.6,   # Frequent link creation
    node_remove_prob=0.05,  # Rare site removal
    edge_remove_prob=0.25   # Occasional link removal
)
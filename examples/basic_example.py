from dynamic_walker.graph.dynamic_graph import DynamicGraph
from dynamic_walker.graph.biased_walker import BiasedRandomWalker
from dynamic_walker.visualization.animator import animate_simulation

dynamic_graph = DynamicGraph(initial_nodes=5)

walker = BiasedRandomWalker(
    graph=dynamic_graph,
    bias_type="weight",
    teleport_probability=0.1,
    exploration_factor=1.5
)

animate_simulation(
    dynamic_graph, 
    walker,
    steps=100,
    interval=500,
    node_add_prob=0.3,
    edge_add_prob=0.4,
    node_remove_prob=0.05,
    edge_remove_prob=0.1
)
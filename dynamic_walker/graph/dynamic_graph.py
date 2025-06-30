import networkx as nx
import random

class DynamicGraph:
    """
    Simulates evolving graph structure with probabilistic modifications.
    
    Supports:
    - Node additions/removals
    - Edge additions/removals
    - Weighted edges
    - Timestep tracking
    """
    
    def __init__(self, initial_nodes=5):
        """Initialize with starting nodes"""
        self.G = nx.Graph()
        if initial_nodes > 0:
            self.G.add_nodes_from(range(initial_nodes))
        self.time_step = 0
        self.node_counter = initial_nodes
        self.removed_nodes = set()

    def update(self, node_add_prob=0.3, edge_add_prob=0.4, 
               node_remove_prob=0.05, edge_remove_prob=0.1):
        """
        Evolve graph structure based on probabilities.
        """
        self.time_step += 1

        # Node addition
        if random.random() < node_add_prob:
            new_node = self.node_counter
            self.G.add_node(new_node)
            self.node_counter += 1

        # Edge addition: each node may spawn new connections
        for node in list(self.G.nodes()):
            if random.random() < edge_add_prob:
                # Find connectable targets
                possible_targets = [
                    n for n in self.G.nodes() 
                    if n != node and not self.G.has_edge(node, n)
                ]
                if possible_targets:
                    target = random.choice(possible_targets)
                    weight = random.randint(1, 10)  # Assign random weight
                    self.G.add_edge(node, target, weight=weight)

        # Node removal (avoid destroying graph)
        if self.G.number_of_nodes() > 2 and random.random() < node_remove_prob:
            node_to_remove = random.choice(list(self.G.nodes()))
            self.G.remove_node(node_to_remove)
            self.removed_nodes.add(node_to_remove)

        # Edge removal
        if self.G.number_of_edges() > 0 and random.random() < edge_remove_prob:
            edge_to_remove = random.choice(list(self.G.edges()))
            self.G.remove_edge(*edge_to_remove)
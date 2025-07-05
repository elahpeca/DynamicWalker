import random
from collections import deque
import networkx as nx

class BiasedRandomWalker:
    """Implements a biased random walker with teleportation capabilities for graph exploration."""
    
    def __init__(self, graph, 
                 bias_type="weight",
                 max_history=100,
                 start_node=None,
                 stay_probability=0.0,
                 teleport_probability=0.1,
                 exploration_factor=1.0,
                 decay_factor=0.99,
                 adaptive_bias=True,
                 min_weight=0.1,
                 max_teleport_distance=0,
                 teleport_strategy="uniform"):
        """
        Initialize the random walker with specified parameters.
        """
        self.graph = graph
        self.bias_type = bias_type
        self.max_history = max_history
        self.path = deque(maxlen=max_history)
        self.visit_count = {}
        self.stay_probability = stay_probability
        self.teleport_probability = teleport_probability
        self.exploration_factor = exploration_factor
        self.decay_factor = decay_factor
        self.adaptive_bias = adaptive_bias
        self.min_weight = min_weight
        self.max_teleport_distance = max_teleport_distance
        self.teleport_strategy = teleport_strategy
        
        self.current_node = self._init_start_node(start_node)

    def _init_start_node(self, start_node):
        """Initialize starting node with preference for high-degree nodes."""
        G = self.graph.G
        if start_node is not None and start_node in G:
            node = start_node
        elif G.nodes:
            # Prefer high-degree nodes for better initial connectivity
            degrees = nx.degree(G)
            max_degree = max(d for _, d in degrees)
            candidates = [n for n, d in degrees if d == max_degree]
            node = random.choice(candidates) if candidates else random.choice(list(G.nodes))
        else:
            node = None
            
        if node is not None:
            self.path.append(node)
            self.visit_count[node] = 1
        return node

    def reset(self, start_node=None):
        """Reset the walker's state and optionally set new start node."""
        self.path.clear()
        self.visit_count.clear()
        self.current_node = self._init_start_node(start_node)

    def _get_teleport_candidates(self):
        """Get candidate nodes for teleportation based on current strategy."""
        G = self.graph.G
        current_node = self.current_node
        
        if not G.nodes:
            return []
        
        if current_node not in G:
            return list(G.nodes)
        
        # Component-aware strategies
        if self.teleport_strategy == "component":
            component = nx.node_connected_component(G, current_node)
            return list(component)
        
        if self.teleport_strategy == "distant":
            current_component = nx.node_connected_component(G, current_node)
            return [n for n in G.nodes if n not in current_component]
        
        # Distance-limited teleportation
        if self.max_teleport_distance <= 0:
            return list(G.nodes)
        
        try:
            distances = nx.single_source_shortest_path_length(
                G, current_node, cutoff=self.max_teleport_distance
            )
            return list(distances.keys())
        except nx.NodeNotFound:
            return list(G.nodes)

    def _get_node_weight(self, node):
        """Calculate weight for a node considering bias type and visit history."""
        weight = 1.0
        
        if self.bias_type == "weight":
            edges = self.graph.G.edges(node, data='weight', default=1.0)
            if edges:
                weight = sum(w for _, _, w in edges) / len(edges)
        elif self.bias_type == "degree":
            weight = self.graph.G.degree(node)
        elif self.bias_type == "activity":
            weight = self.graph.G.nodes[node].get('activity', 1.0)
        elif self.bias_type == "custom" and hasattr(self, 'custom_bias'):
            weight = self.custom_bias(node)
        
        # Apply adaptive bias based on visit counts
        if self.adaptive_bias:
            visit_count = self.visit_count.get(node, 0)
            weight *= (self.decay_factor ** visit_count)
        
        return max(self.min_weight, weight)

    def step(self):
        """Perform one step of the random walk with teleportation."""
        G = self.graph.G
        
        if not G.nodes:
            self.current_node = None
            return
        
        # Handle case where current node was removed
        if self.current_node not in G:
            self.current_node = random.choice(list(G.nodes)) if G.nodes else None
            if self.current_node:
                self.path.append(self.current_node)
                self.visit_count[self.current_node] = self.visit_count.get(self.current_node, 0) + 1
            return

        # Teleportation logic
        if random.random() < self.teleport_probability:
            candidates = self._get_teleport_candidates()
            if candidates:
                weights = [self._get_node_weight(node) for node in candidates]
                total_weight = sum(weights)
                
                if total_weight > 0:
                    next_node = random.choices(candidates, weights=weights)[0]
                else:
                    next_node = random.choice(candidates)
                
                self.current_node = next_node
                self.path.append(next_node)
                self.visit_count[next_node] = self.visit_count.get(next_node, 0) + 1
            return

        # Stay probability
        if random.random() < self.stay_probability:
            self.visit_count[self.current_node] += 1
            return

        # Standard random walk step
        neighbors = list(G.neighbors(self.current_node))
        if not neighbors:
            # Force teleport if no neighbors available
            self.teleport_probability = 1.0
            self.step()
            self.teleport_probability = 0.1  # Reset to default
            return

        # Calculate weights with exploration factor
        weights = []
        for neighbor in neighbors:
            weight = self._get_node_weight(neighbor)
            weights.append(weight ** self.exploration_factor)

        # Select next node based on weights
        total_weight = sum(weights)
        if total_weight <= 0:
            next_node = random.choice(neighbors)
        else:
            next_node = random.choices(neighbors, weights=weights)[0]
        
        # Update walker state
        self.current_node = next_node
        self.path.append(next_node)
        self.visit_count[next_node] = self.visit_count.get(next_node, 0) + 1

    def get_visit_distribution(self):
        """Calculate normalized visit frequencies for all visited nodes."""
        total_visits = sum(self.visit_count.values())
        if total_visits == 0:
            return {}
        return {node: count / total_visits for node, count in self.visit_count.items()}
    
    def set_custom_bias(self, bias_function):
        """Set a custom bias function for node selection."""
        self.custom_bias = bias_function
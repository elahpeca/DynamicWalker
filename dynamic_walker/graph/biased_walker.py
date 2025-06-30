import random
from collections import deque
import networkx as nx

class BiasedRandomWalker:
    """
    Simulates a random walker with configurable biases on dynamic graphs.
    
    Features:
    - Multiple bias strategies (weight, degree, custom)
    - Teleportation (PageRank-like jumps)
    - Adaptive exploration/exploitation
    - Visit history tracking
    - Handles dynamic graph changes
    """
    
    def __init__(self, graph, 
        bias_type="weight",
        max_history=100,
        start_node=None,
        stay_probability=0.0,
        teleport_probability=0.0,
        exploration_factor=1.0,
        decay_factor=0.99,
        adaptive_bias=False,
        min_weight=0.1,
        max_teleport_distance=0):
        """
        Initialize walker with navigation parameters.
        """
        self.graph = graph
        self.bias_type = bias_type
        self.custom_bias = None
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
        
        # Initialize starting position
        if start_node is not None and start_node in graph.G.nodes():
            self.current_node = start_node
        else:
            self.current_node = random.choice(list(graph.G.nodes())) if graph.G.nodes() else None
        
        if self.current_node is not None:
            self.path.append(self.current_node)
            self.visit_count[self.current_node] = 1

    def set_custom_bias(self, bias_function):
        """Set custom bias function."""
        self.custom_bias = bias_function

    def reset(self, start_node=None):
        """Reset walker to initial state."""
        self.path.clear()
        self.visit_count = {}
        
        if start_node is not None and start_node in self.graph.G.nodes():
            self.current_node = start_node
        else:
            self.current_node = random.choice(list(self.graph.G.nodes())) if self.graph.G.nodes() else None
        
        if self.current_node is not None:
            self.path.append(self.current_node)
            self.visit_count[self.current_node] = 1

    def _get_teleport_candidates(self):
        """Get nodes within max-teleport distance using BFS."""
        if self.max_teleport_distance <= 0:
            return list(self.graph.G.nodes())
        
        try:
            # Calculate shortest paths within distance limit
            distances = nx.single_source_shortest_path_length(
                self.graph.G, self.current_node, cutoff=self.max_teleport_distance
            )
            return list(distances.keys())
        except:
            return list(self.graph.G.nodes())

    def _get_adaptive_weight(self, node, neighbor):
        """
        Calculate edge weight with exploration adjustments:
        1. Get base weight (edge weight, degree, or custom)
        2. Apply visit-count decay to encourage exploration
        3. Enforce minimum weight threshold
        """
        base_weight = 1.0
        
        if self.bias_type == "weight":
            base_weight = self.graph.G.edges.get((node, neighbor), {}).get("weight", 1.0)
        elif self.bias_type == "degree":
            base_weight = self.graph.G.degree(neighbor)
        elif self.bias_type == "custom" and self.custom_bias:
            base_weight = self.custom_bias(node, neighbor)
        
        # Reduce weight for frequently visited nodes (explorational decay)
        if self.adaptive_bias:
            visit_count = self.visit_count.get(neighbor, 0)
            decay = self.decay_factor ** visit_count
            return max(self.min_weight, base_weight * decay)
        
        return max(self.min_weight, base_weight)

    def step(self):
        """Execute one navigation step with priority: teleport > stay > neighbor walk."""
        # Handle empty graph case
        if not self.graph.G.nodes():
            self.current_node = None
            return
            
        # Recover if current node was removed
        if self.current_node not in self.graph.G.nodes():
            available_nodes = list(self.graph.G.nodes())
            if available_nodes:
                self.current_node = random.choice(available_nodes)
                self.path.append(self.current_node)
                self.visit_count[self.current_node] = self.visit_count.get(self.current_node, 0) + 1
            else:
                self.current_node = None
            return

        # Teleportation logic (PageRank-style jump)
        if random.random() < self.teleport_probability:
            candidates = self._get_teleport_candidates()
            if candidates:
                # Exclude current position from candidates
                if self.current_node in candidates:
                    candidates.remove(self.current_node)
                
                if candidates:
                    next_node = random.choice(candidates)
                    self.current_node = next_node
                    self.path.append(next_node)
                    self.visit_count[next_node] = self.visit_count.get(next_node, 0) + 1
            return

        # Stay-in-place probability
        if random.random() < self.stay_probability:
            self.visit_count[self.current_node] = self.visit_count.get(self.current_node, 0) + 1
            return

        # Standard neighbor walk with bias
        neighbors = list(self.graph.G.neighbors(self.current_node))
        if not neighbors:
            return

        # Calculate weights with exploration factor
        weights = []
        for neighbor in neighbors:
            weight = self._get_adaptive_weight(self.current_node, neighbor)
            
            # Apply exploration exponent (1=neutral, >1=explore less-traveled paths)
            if self.exploration_factor != 1.0:
                weight = weight ** self.exploration_factor
                
            weights.append(weight)

        # Normalize and select next node
        total_weight = sum(weights)
        if total_weight <= 0:
            next_node = random.choice(neighbors)  # Fallback to uniform selection
        else:
            probabilities = [w / total_weight for w in weights]
            next_node = random.choices(neighbors, weights=probabilities)[0]
        
        # Update state
        self.current_node = next_node
        self.path.append(next_node)
        self.visit_count[next_node] = self.visit_count.get(next_node, 0) + 1

    def get_visit_distribution(self):
        """Compute normalized visit frequencies across all nodes."""
        total_visits = sum(self.visit_count.values())
        if total_visits == 0:
            return {}
        return {node: count / total_visits for node, count in self.visit_count.items()}
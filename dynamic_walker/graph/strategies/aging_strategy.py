from .base_strategy import BaseStrategy
import random
import networkx as nx

class AgingStrategy(BaseStrategy):
    """Implements aging-based attachment strategy for dynamic graphs."""
    
    def __init__(self, graph, config):
        """Initialize strategy with decay factor from config."""
        super().__init__(graph, config)
        self.decay_factor = config.get('decay_factor', 0.95)
    
    def pre_attach(self, new_node):
        """Set birth step for new node before attachment."""
        self.graph.G.nodes[new_node]['birth_step'] = self.time_step
    
    def attach(self, new_node):
        """Attach new node considering node age and activity."""
        G = self.graph.G
        if G.number_of_nodes() <= 1:
            return
            
        weights = {}
        
        for node, data in G.nodes(data=True):
            if node == new_node:
                continue
                
            age = self.time_step - data.get('birth_step', 0)
            age_factor = self.decay_factor ** age
            activity = data.get('activity', 0.5)
            weights[node] = age_factor * (0.6 + 0.4 * activity)
        
        if not weights:
            return
            
        num_edges = min(3, max(1, int(G.number_of_nodes() / 10)))
        selected = set()
        
        for _ in range(num_edges * 3):
            if len(selected) >= num_edges:
                break
                
            target = random.choices(
                list(weights.keys()),
                weights=list(weights.values()),
                k=1
            )[0]
            
            if self._add_edge(new_node, target):
                selected.add(target)
                weights[target] *= 0.3
    
    def add_triadic_edges(self):
        """Add triadic closures based on edge age and activity."""
        G = self.graph.G
        if G.number_of_edges() == 0:
            return
            
        edge_weights = []
        
        for u, v in G.edges():
            age = self.time_step - min(
                G.nodes[u].get('birth_step', self.time_step),
                G.nodes[v].get('birth_step', self.time_step)
            )
            weight = self.decay_factor ** age
            activity = (G.nodes[u].get('activity', 0.5) + G.nodes[v].get('activity', 0.5)) / 2  
            edge_weights.append(((u, v), weight * activity))
        
        if not edge_weights:
            return
            
        edge_weights.sort(key=lambda x: x[1], reverse=True)
        u, v = edge_weights[0][0]
        
        # Find potential triadic closure candidates
        potential_targets = [
            (v, neighbor) for neighbor in nx.neighbors(G, u)
            if neighbor != v and not G.has_edge(v, neighbor)
        ] + [
            (u, neighbor) for neighbor in nx.neighbors(G, v)
            if neighbor != u and not G.has_edge(u, neighbor)
        ]
        
        for source, target in potential_targets[:2]:
            self._add_edge(source, target)
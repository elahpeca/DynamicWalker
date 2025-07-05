from .base_strategy import BaseStrategy
import random
import networkx as nx

class RandomStrategy(BaseStrategy):
    """Implements random attachment strategy for graph growth."""
    
    def attach(self, new_node):
        """Attach new node to random existing nodes."""
        G = self.graph.G
        if G.number_of_nodes() <= 1:
            return
        
        candidates = [n for n in G.nodes if n != new_node and 
                     G.degree(n) < self.config.get('max_degree', 15)]
        
        if not candidates:
            return
            
        # Connect to random nodes (scaled with graph size)
        num_edges = min(3, max(1, int(G.number_of_nodes() / 15)))
        for target in random.sample(candidates, min(num_edges, len(candidates))):
            self._add_edge(new_node, target)
    
    def add_triadic_edges(self):
        """Add random triadic closures to increase clustering."""
        G = self.graph.G
        if G.number_of_edges() == 0:
            return
            
        # Select random edge and potential triangle completions
        u, v = random.choice(list(G.edges()))
        potential_targets = [
            (v, n) for n in nx.neighbors(G, u) 
            if n != v and not G.has_edge(v, n)
        ] + [
            (u, n) for n in nx.neighbors(G, v)
            if n != u and not G.has_edge(u, n)
        ]
        
        # Add 1-2 random triangle edges
        for source, target in random.sample(potential_targets, min(2, len(potential_targets))):
            self._add_edge(source, target)
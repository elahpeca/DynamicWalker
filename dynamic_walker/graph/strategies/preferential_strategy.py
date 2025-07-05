from .base_strategy import BaseStrategy
import random
import networkx as nx

class PreferentialStrategy(BaseStrategy):
    """Implements preferential attachment strategy for graph growth."""
    
    def __init__(self, graph, config):
        """Initialize with preferential exponent parameter."""
        super().__init__(graph, config)
        self.exponent = config.get('preferential_exponent', 1.0)
    
    def attach(self, new_node):
        """Attach new node using preferential attachment rules."""
        G = self.graph.G
        if G.number_of_nodes() < 2:
            return
        
        new_comp = next(nx.connected_components(G), set()) if G.nodes else set()
        candidates = []
        
        for node in G.nodes:
            if node == new_node:
                continue
                
            if G.degree(node) >= self.config.get('max_degree', 15):
                continue
                
            weight = G.degree(node) ** self.exponent
            same_component = node in new_comp
            bonus = 1.0 if same_component else 1.5
            candidates.append((node, weight * bonus))
        
        if not candidates:
            return
            
        # Normalize weights for probability distribution
        total_weight = sum(w for _, w in candidates)
        probabilities = [w / total_weight for _, w in candidates]
        num_edges = min(3, max(1, int(G.number_of_nodes() / 10)))
        selected = set()
        
        for _ in range(num_edges * 2):
            if len(selected) >= num_edges:
                break
                
            idx = random.choices(range(len(candidates)), weights=probabilities)[0]
            target, weight = candidates[idx]
            
            if self._add_edge(new_node, target):
                selected.add(target)
                probabilities[idx] = 0
                total_weight = sum(probabilities)
                if total_weight > 0:
                    probabilities = [p / total_weight for p in probabilities]
    
    def add_triadic_edges(self):
        """Add triadic closures with preference for cross-component edges."""
        G = self.graph.G
        if G.number_of_edges() == 0:
            return
            
        cross_edges = []
        same_edges = []
        components = list(nx.connected_components(G))
        
        for u, v in G.edges():
            comp_u = next((c for c in components if u in c), set())
            comp_v = next((c for c in components if v in c), set())
            
            if comp_u == comp_v:
                same_edges.append((u, v))
            else:
                cross_edges.append((u, v))
        
        # Prefer cross-component edges for better connectivity
        selected_edge = random.choice(cross_edges) if cross_edges else random.choice(same_edges) if same_edges else None
        if not selected_edge:
            return
            
        u, v = selected_edge
        potential_targets = [
            (v, neighbor) for neighbor in nx.neighbors(G, u)
            if neighbor != v and not G.has_edge(v, neighbor)
        ] + [
            (u, neighbor) for neighbor in nx.neighbors(G, v)
            if neighbor != u and not G.has_edge(u, neighbor)
        ]
        
        if potential_targets:
            for source, target in random.sample(potential_targets, min(2, len(potential_targets))):
                self._add_edge(source, target)
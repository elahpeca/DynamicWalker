import networkx as nx
import random
import heapq
from .strategies.strategy_factory import StrategyFactory

class DynamicGraph:
    """A dynamic graph that evolves over time with configurable growth strategies."""
    
    def __init__(self, strategy="preferential", **config):
        """Initialize the graph with given strategy and configuration."""
        self.G = nx.Graph()
        self.time_step = 0
        self.node_counter = 0
        self.config = config
        self.strategy_name = strategy
        self.components_dirty = True
        self._components = None
        self._activity_heap = []
        self._node_activity = {}
        
        self.strategy = StrategyFactory.create(strategy, self, config)
        
        self.target_components = config.get('target_components', 1)
        self.min_component_size = config.get('min_component_size', 3)
        
        nx.set_node_attributes(self.G, 0.0, 'activity')
        nx.set_node_attributes(self.G, 0, 'birth_step')
        nx.set_edge_attributes(self.G, 0.0, 'weight')
        
        if config.get('initial_nodes', 0) > 0:
            self._initialize_graph()
    
    def _initialize_graph(self):
        """Initialize the graph with initial nodes based on configuration."""
        num_nodes = self.config['initial_nodes']
        if self.target_components > 1:
            self._create_multicomponent_graph(num_nodes)
        else:
            self._create_single_component_graph(num_nodes)
        self.node_counter = num_nodes
    
    def _create_single_component_graph(self, num_nodes):
        """Create a single connected component graph."""
        self.G = nx.connected_watts_strogatz_graph(num_nodes, k=4, p=0.6, tries=100)
        nx.set_edge_attributes(self.G, 1.0, 'weight')
        
        for node in self.G.nodes:
            self._init_node(node)
            self.strategy.pre_attach(node)
    
    def _create_multicomponent_graph(self, num_nodes):
        """Create graph with multiple components."""
        component_sizes = self._balanced_component_sizes(num_nodes)
        self.G = nx.empty_graph(0)
        
        for i, size in enumerate(component_sizes):
            comp_graph = nx.connected_watts_strogatz_graph(size, k=3, p=0.6, tries=100)
            nx.set_edge_attributes(comp_graph, 1.0, 'weight')
            
            comp_graph = nx.relabel_nodes(comp_graph, {n: n + self.node_counter for n in comp_graph.nodes})
            self.G = nx.union(self.G, comp_graph)
            
            for node in comp_graph.nodes:
                self._init_node(node)
                self.strategy.pre_attach(node)
            
            self.node_counter += size
    
    def _balanced_component_sizes(self, total_nodes):
        """Calculate balanced component sizes distribution."""
        target = self.target_components
        min_size = self.min_component_size
        base_size = max(min_size, total_nodes // target)
        remainder = total_nodes % target
        
        sizes = [base_size + 1] * remainder + [base_size] * (target - remainder)
        return [s for s in sizes if s >= min_size]

    def _init_node(self, node):
        """Initialize node with activity tracking."""
        activity = 1.0
        self.G.nodes[node]['activity'] = activity
        self.G.nodes[node]['birth_step'] = self.time_step
        self._node_activity[node] = activity
        heapq.heappush(self._activity_heap, (activity, node))
    
    def _add_edge(self, u, v, weight=1.0):
        """Add edge between nodes with weight."""
        if u == v or self.G.has_edge(u, v):
            return False
        
        self.G.add_edge(u, v, weight=weight)
        self.components_dirty = True
        return True
    
    def _remove_edge(self, u, v):
        """Remove edge between nodes."""
        if self.G.has_edge(u, v):
            self.G.remove_edge(u, v)
            self.components_dirty = True
            return True
        return False
    
    def update_activity(self):
        """Update node and edge activities with aging factors."""
        self.time_step += 1
        
        node_aging = self.config.get('node_aging_factor', 0.99)
        edge_aging = self.config.get('edge_aging_factor', 0.97)
        
        node_activities = {node: max(0.1, data['activity'] * node_aging)
                          for node, data in self.G.nodes(data=True)}
        nx.set_node_attributes(self.G, node_activities, 'activity')
        
        self._node_activity.update(node_activities)
        
        edge_weights = {(u, v): data['weight'] * edge_aging
                       for u, v, data in self.G.edges(data=True)}
        nx.set_edge_attributes(self.G, edge_weights, 'weight')
    
    def get_least_active_node(self):
        """Get least active node using activity heap."""
        while self._activity_heap:
            activity, node = heapq.heappop(self._activity_heap)
            current_activity = self._node_activity.get(node, -1)
            if current_activity == activity and node in self.G:
                heapq.heappush(self._activity_heap, (activity, node))
                return node
        return None
    
    def enforce_degree_limits(self):
        """Ensure all nodes stay within configured degree limits."""
        min_degree = self.config.get('min_degree', 2)
        max_degree = self.config.get('max_degree', 15)
        degrees = dict(self.G.degree())
        
        nodes_to_boost = [n for n, d in degrees.items() if d < min_degree]
        for node in nodes_to_boost:
            self._boost_connectivity(node, min_degree)
        
        nodes_to_reduce = [n for n, d in degrees.items() if d > max_degree]
        for node in nodes_to_reduce:
            self._reduce_connectivity(node, max_degree)
    
    def _boost_connectivity(self, node, min_degree):
        """Increase connectivity for under-connected node."""
        needed = min_degree - self.G.degree(node)
        if needed <= 0:
            return
        
        components = self._get_components()
        node_comp = next((comp for comp in components if node in comp), set())
        
        comp_dict = {}
        for comp in components:
            for n in comp:
                comp_dict[n] = comp
        
        neighbors = set(self.G.neighbors(node))
        non_neighbors = set(self.G.nodes) - neighbors - {node}
        
        candidates = []
        for other in non_neighbors:
            if self.G.degree(other) >= self.config.get('max_degree', 15):
                continue
                
            priority = 1.5 if comp_dict.get(other, set()) != node_comp else 1.0
            score = priority * self.G.nodes[other]['activity']
            candidates.append((other, score))
        
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            for other, _ in candidates[:min(needed, len(candidates))]:
                if self._add_edge(node, other):
                    needed -= 1
                    if needed <= 0:
                        break
    
    def _reduce_connectivity(self, node, max_degree):
        """Reduce connectivity for over-connected node."""
        excess = self.G.degree(node) - max_degree
        if excess <= 0:
            return
        
        candidates = []
        for neighbor in self.G.neighbors(node):
            weight = self.G.edges[node, neighbor]['weight']
            activity = self.G.nodes[neighbor]['activity']
            score = 0.4 * (1 - weight) + 0.6 * (1 - activity)
            candidates.append((neighbor, score))
        
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            for neighbor, _ in candidates[:excess]:
                self._remove_edge(node, neighbor)
    
    def _get_components(self):
        """Get connected components with caching."""
        if self.components_dirty or self._components is None:
            self._components = list(nx.connected_components(self.G))
            self.components_dirty = False
        return self._components
    
    def enforce_component_rules(self):
        """Ensure graph components follow configuration rules."""
        components = self._get_components()
        num_components = len(components)
        
        if num_components == self.target_components:
            self._enforce_min_component_size(components)
            return
        
        if num_components > self.target_components:
            self._merge_components(components)
        else:
            self._split_components(components)
        
        self._enforce_min_component_size(self._get_components())
    
    def _merge_components(self, components):
        """Merge components to reach target count."""
        sorted_comps = sorted(components, key=len)
        keep_count = self.target_components
        merge_components = sorted_comps[:-keep_count]
        keep_components = set().union(*sorted_comps[-keep_count:])
        
        for comp in merge_components:
            if not comp:
                continue
                
            node_from = random.choice(list(comp))
            node_to = random.choice(list(keep_components))
            self._add_edge(node_from, node_to)
    
    def _split_components(self, components):
        """Split components to reach target count."""
        needed = self.target_components - len(components)
        sorted_comps = sorted(components, key=len, reverse=True)
        
        for comp in sorted_comps:
            if needed <= 0:
                break
                
            if len(comp) < 2 * self.min_component_size:
                continue
                
            bridge_edge = self._find_best_bridge(comp)
            if bridge_edge:
                self._remove_edge(*bridge_edge)
                needed -= 1
    
    def _find_best_bridge(self, component):
        """Find optimal bridge edge to split component."""
        subgraph = self.G.subgraph(component)
        if len(component) > 100:
            betweenness = nx.betweenness_centrality(subgraph, k=min(50, len(component)))
        else:
            betweenness = nx.betweenness_centrality(subgraph)
        
        edge_centrality = {}
        for u, v in subgraph.edges():
            edge_centrality[(u, v)] = (betweenness[u] + betweenness[v]) / 2
        
        if not edge_centrality:
            return None
        
        return max(edge_centrality, key=edge_centrality.get)
    
    def _enforce_min_component_size(self, components):
        """Ensure all components meet minimum size requirement."""
        small_comps = [comp for comp in components if len(comp) < self.min_component_size]
        if not small_comps:
            return
            
        largest_comp = max(components, key=len)
        
        for comp in small_comps:
            if comp == largest_comp:
                continue
                
            node_from = random.choice(list(comp))
            node_to = random.choice(list(largest_comp))
            self._add_edge(node_from, node_to)
    
    def update(self, params):
        """Main update method for graph evolution."""
        self.time_step += 1
        self.update_activity()
        
        if random.random() < params.get('node_add_prob', 0.02):
            self._add_node()
        
        if self.G.number_of_nodes() > 3 and random.random() < params.get('node_remove_prob', 0.005):
            self._remove_inactive_node()
        
        if self.G.number_of_edges() > 0:
            if random.random() < params.get('triadic_prob', 0.3):
                self.strategy.add_triadic_edges()
            
            if random.random() < params.get('edge_remove_prob', 0.1):
                self._remove_aged_edges()
        
        self.enforce_degree_limits()
        self.enforce_component_rules()
        self.strategy.post_update()
    
    def _add_node(self):
        """Add new node to the graph."""
        new_node = self.node_counter
        self.G.add_node(new_node)
        self._init_node(new_node)
        self.strategy.pre_attach(new_node)
        self.strategy.attach(new_node)
        self.components_dirty = True
        self.node_counter += 1
    
    def _remove_inactive_node(self):
        """Remove least active node from the graph."""
        node = self.get_least_active_node()
        if node is not None:
            self.G.remove_node(node)
            self.components_dirty = True
            self._node_activity.pop(node, None)
    
    def _remove_aged_edges(self):
        """Remove edges with weight below threshold."""
        threshold = self.config.get('min_edge_weight', 0.1)
        edges_to_remove = [
            (u, v) for u, v, data in self.G.edges(data=True)
            if data['weight'] < threshold
        ]
        
        if edges_to_remove:
            self.G.remove_edges_from(edges_to_remove)
            self.components_dirty = True
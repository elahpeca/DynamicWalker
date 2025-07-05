import abc

class BaseStrategy(abc.ABC):
    """Abstract base class for graph growth strategies."""
    
    def __init__(self, graph, config):
        """Initialize strategy with graph and configuration."""
        self.graph = graph
        self.config = config
        self.time_step = 0
    
    def pre_attach(self, new_node):
        """Optional pre-attachment hook for new nodes."""
        pass
    
    @abc.abstractmethod
    def attach(self, new_node):
        """Abstract method for attaching new nodes to the graph."""
        pass
    
    @abc.abstractmethod
    def add_triadic_edges(self):
        """Abstract method for adding triadic closure edges."""
        pass
    
    def post_update(self):
        """Update time step after graph modifications."""
        self.time_step += 1
    
    def _get_eligible_nodes(self, exclude_node=None):
        """Get nodes that haven't reached maximum degree."""
        max_degree = self.config.get('max_degree', 15)
        return [n for n in self.graph.G.nodes 
               if n != exclude_node and self.graph.G.degree(n) < max_degree]
    
    def _add_edge(self, u, v, weight=1.0):
        """Wrapper for graph's edge addition method."""
        return self.graph._add_edge(u, v, weight)
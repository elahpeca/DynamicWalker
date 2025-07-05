import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import random
from matplotlib.animation import FuncAnimation
from matplotlib.colors import LinearSegmentedColormap
import matplotlib as mpl


class GraphAnimator:
    """Visualizes dynamic graph evolution with random walker animation."""
    
    def __init__(self, dynamic_graph, walker, steps=500, interval=200, **params):
        """
        Initialize the animator with graph and walker.
        """
        self.dynamic_graph = dynamic_graph
        self.walker = walker
        self.steps = steps
        self.interval = interval
        self.params = params
        
        # Initialize figure and visual settings
        self.fig, self.ax = plt.subplots(figsize=(12, 8), facecolor='#f0f0f0')
        self.fig.tight_layout(rect=[0.05, 0.05, 0.95, 0.95])
        
        self.strategy_name = dynamic_graph.strategy_name.capitalize()
        self.title_text = self.fig.text(
            0.5, 0.97, 
            f"Random Walk on Dynamic Graph: {self.strategy_name} strategy", 
            fontsize=16,
            color='#333333',
            horizontalalignment='center'
        )
        
        # Color schemes
        self.edge_cmap = LinearSegmentedColormap.from_list("custom_blue", ["#2c7bb6", "#abd9e9"])
        self.node_cmap = LinearSegmentedColormap.from_list("custom_purple", ["#762a83", "#c2a5cf"])
        
        self._initialize_positions()
        
        # Styling
        plt.style.use('seaborn-v0_8-pastel')
        self.ax.set_facecolor('#fafafa')
    
    def _initialize_positions(self):
        """Initialize node positions using spring layout."""
        G = self.dynamic_graph.G
        self.prev_pos = nx.spring_layout(G, seed=42)
        self.current_pos = self.prev_pos.copy()
    
    def _update_positions(self, G, frame):
        """Update node positions with smooth interpolation."""
        # Calculate new positions using current as base
        new_pos = nx.spring_layout(
            G,
            pos=self.current_pos.copy(),
            seed=42,
            iterations=15 if frame == 0 else 8
        )
        
        # Interpolate positions
        interpolated_pos = {}
        alpha = min(1.0, 0.1 + frame * 0.05)
        
        for node in G.nodes():
            if node in self.prev_pos and node in new_pos:
                # Smooth transition for existing nodes
                interpolated_pos[node] = (
                    alpha * new_pos[node][0] + (1 - alpha) * self.prev_pos[node][0],
                    alpha * new_pos[node][1] + (1 - alpha) * self.prev_pos[node][1]
                )
            else:
                # Use direct position for new nodes
                interpolated_pos[node] = new_pos[node]
        
        self.prev_pos = self.current_pos.copy()
        self.current_pos = new_pos.copy()
        
        return interpolated_pos

    def _calculate_node_sizes(self, G):
        """Calculate node sizes based on their degree."""
        degrees = np.array([d for _, d in G.degree()])
        min_size, max_size = 50, 300
        
        if degrees.max() == degrees.min():
            return np.full(len(degrees), (min_size + max_size) / 2)
        
        return min_size + (max_size - min_size) * (degrees - degrees.min()) / (degrees.max() - degrees.min())

    def _draw_graph(self, G, pos):
        """Draw the graph with current parameters."""
        # Ensure all nodes have positions
        for node in G.nodes():
            if node not in pos:
                pos[node] = (random.random(), random.random())
        
        node_sizes = self._calculate_node_sizes(G)
        degrees = np.array([d for _, d in G.degree()])
        
        # Draw nodes
        nx.draw_networkx_nodes(
            G, pos, ax=self.ax, 
            node_size=node_sizes,
            node_color=degrees,
            cmap=self.node_cmap,
            alpha=0.85,
            edgecolors='#555555',
            linewidths=0.8
        )
        
        # Draw edges
        nx.draw_networkx_edges(
            G, pos, ax=self.ax, 
            edge_color='#888888',
            style="solid",
            width=0.8,
            alpha=0.3,
        )
        
        # Highlight current node
        current_node = self.walker.current_node
        if current_node in G.nodes:
            self._highlight_node(current_node, pos)

    def _highlight_node(self, node, pos):
        """Highlight the specified node with special styling."""
        nx.draw_networkx_nodes(
            self.dynamic_graph.G, pos, 
            nodelist=[node],
            node_size=300,
            node_color='#e7298a',
            edgecolors='#ff00ff',
            linewidths=2.0,
            ax=self.ax
        )
        
        # Add glow effect
        self.ax.scatter(
            [pos[node][0]],
            [pos[node][1]],
            s=1000,
            alpha=0.15,
            color='#e7298a',
            zorder=-1
        )

    def _render_info_panel(self, frame):
        """Render information panel with current stats including graph density."""
        G = self.dynamic_graph.G
        n = G.number_of_nodes()
        m = G.number_of_edges()
        
        # Calculate density (handle cases when n < 2)
        density = (2 * m) / (n * (n - 1)) if n > 1 else 0.0
        
        info = (
            f"Step: {frame}/{self.steps}\n"
            f"Nodes: {n}\n"
            f"Edges: {m}\n"
            f"Density: {density:.4f}\n"
            f"Components: {nx.number_connected_components(G)}\n"
            f"Current node: {self.walker.current_node}"
        )
        
        self.ax.text(
            0.98, 0.02, info,
            transform=self.ax.transAxes,
            fontsize=11,
            fontfamily='monospace',
            verticalalignment='bottom',
            horizontalalignment='right',
            bbox=dict(
                boxstyle='round,pad=0.5',
                facecolor='white',
                edgecolor='#dddddd',
                alpha=0.8
            )
        )
        
    def _update_frame(self, frame):
        """Update function for animation frames."""
        self.ax.clear()
        self.ax.set_facecolor('#fafafa')
        
        # Update system state
        if frame > 0:
            self.dynamic_graph.update(self.params)
            self.walker.step()
        
        G = self.dynamic_graph.G
        pos = self._update_positions(G, frame)
        
        # Draw elements
        self._draw_graph(G, pos)
        self._render_info_panel(frame)
        
        self.ax.set_axis_off()

    def animate(self):
        """Start the animation process."""
        self.animation = FuncAnimation(
            self.fig,
            self._update_frame,
            frames=self.steps + 1,
            interval=self.interval,
            repeat=False,
            blit=False
        )
        plt.show()
        return self.animation
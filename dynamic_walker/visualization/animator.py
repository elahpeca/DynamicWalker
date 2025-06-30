import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import networkx as nx
import numpy as np

def animate_simulation(graph, walker, steps=50, interval=500, **kwargs):
    """
    Creates animated visualization of dynamic graph and walker.
    
    Features:
    - Real-time topology evolution
    - Agent position tracking
    - Adaptive layout updates
    - Statistics dashboard
    - Edge weight labeling
    - Smooth transitions
    """
    fig, ax = plt.subplots(figsize=(13, 9))
    colors = {
        'node': '#A0E7E5',
        'agent': '#FF6B6B',
        'path': '#4ECDC4',
        'edge': '#777777',
        'weight': '#333333',
        'bg': '#F8F9FA',
        'degree': '#888888',
        'text': '#333333'
    }
    
    # Initialize positions using spring layout
    pos = nx.spring_layout(graph.G, seed=42, k=1.5) if graph.G.nodes() else {}
    
    # Legend elements
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors['agent'], 
                  markersize=10, label='Agent Position'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors['node'], 
                  markersize=10, label='Graph Nodes')
    ]
    
    # Statistics tracking
    stats = {
        'nodes_added': 0,
        'nodes_removed': 0,
        'edges_added': 0,
        'edges_removed': 0
    }
    
    def update(i):
        nonlocal pos, stats
        ax.clear()
        
        try:
            # Track changes for statistics
            prev_nodes = set(graph.G.nodes())
            prev_edges = set(graph.G.edges())
            
            # Update graph and walker state
            graph.update(**kwargs)
            walker.step()
            
            # Calculate changes
            new_nodes = set(graph.G.nodes()) - prev_nodes
            removed_nodes = prev_nodes - set(graph.G.nodes())
            new_edges = set(graph.G.edges()) - prev_edges
            removed_edges = prev_edges - set(graph.G.edges())
            
            # Update statistics counters
            stats['nodes_added'] += len(new_nodes)
            stats['nodes_removed'] += len(removed_nodes)
            stats['edges_added'] += len(new_edges)
            stats['edges_removed'] += len(removed_edges)
            
            # Handle empty graph case
            if not graph.G.nodes():
                ax.text(0.5, 0.5, "Empty Graph\nWaiting for new nodes...", 
                       ha='center', va='center', fontsize=14)
                return
            
            # Calculate adaptive sizes based on node count
            node_count = len(graph.G.nodes())
            base_size = 800
            min_size = 300
            max_size = 1200
            scaled_size = max(min_size, min(max_size, base_size / (1 + node_count/10)))
            sizes = {
                'node': scaled_size,
                'agent': scaled_size * 1.5,  # Agent is larger than nodes
                'font': max(8, 12 - node_count/20)  # Font shrinks as graph grows
            }
            
            # Layout update logic
            if new_nodes or removed_nodes:
                # Position new nodes near center
                for node in new_nodes:
                    if node not in pos:
                        pos[node] = np.random.normal(0, 0.2, 2)
                
                # Smooth layout transition
                prev_pos = pos.copy()
                new_pos = nx.spring_layout(
                    graph.G, 
                    pos=prev_pos,  # Start from current positions
                    seed=42,
                    k=1.5 * (1 + node_count/20),  # Adjust spacing
                    iterations=30  # More iterations for stability
                )
                
                # Blend old and new positions
                for node in graph.G.nodes():
                    if node in prev_pos:
                        pos[node] = prev_pos[node]*0.7 + new_pos[node]*0.3
                    else:
                        pos[node] = new_pos[node]
            else:
                # Minor position jitter for visual freshness
                for node in graph.G.nodes():
                    if node in pos:
                        pos[node] = pos[node]*0.9 + np.random.normal(0, 0.01, 2)*0.1
            
            # Draw edges
            nx.draw_networkx_edges(
                graph.G, pos,
                width=1.5,
                edge_color=colors['edge'],
                alpha=0.7,
                ax=ax
            )
            
            # Edge labels for weight-based biases
            if walker.bias_type in ['weight', 'custom']:
                edge_labels = {}
                for (u, v) in graph.G.edges():
                    if walker.bias_type == 'weight':
                        edge_labels[(u, v)] = graph.G.edges[u, v].get('weight', '?')
                    elif walker.custom_bias:
                        try:
                            # Format custom bias values
                            edge_labels[(u, v)] = f"{walker.custom_bias(u, v):.2f}"
                        except:
                            pass
                
                nx.draw_networkx_edge_labels(
                    graph.G, pos,
                    edge_labels=edge_labels,
                    font_size=max(8, sizes['font']-2),
                    font_color=colors['weight'],
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.2'),
                    ax=ax
                )
            
            # Draw all nodes
            nx.draw_networkx_nodes(
                graph.G, pos,
                node_size=sizes['node'],
                node_color=colors['node'],
                edgecolors='#333333',
                linewidths=1.0,
                ax=ax
            )
            
            # Highlight agent position
            if walker.current_node is not None and walker.current_node in graph.G.nodes():
                nx.draw_networkx_nodes(
                    graph.G, pos,
                    nodelist=[walker.current_node],
                    node_size=sizes['agent'],
                    node_color=colors['agent'],
                    edgecolors='#333333',
                    linewidths=1.5,
                    ax=ax
                )
            
            # Node labels
            nx.draw_networkx_labels(
                graph.G, pos,
                font_size=sizes['font'],
                font_color=colors['text'],
                font_weight='bold',
                ax=ax
            )
            
            # Title with current step and mode
            ax.set_title(f'Dynamic Graph • Step {graph.time_step} • Mode: {walker.bias_type}', 
                        fontsize=14, pad=20, color=colors['text'], fontweight='bold')
            
            # Statistics dashboard
            stats_text = (
                f"Nodes: {node_count} | Edges: {len(graph.G.edges())}\n"
                f"Agent: {walker.current_node if walker.current_node is not None else 'N/A'}\n"
                f"Added: ▲{stats['nodes_added']} nd | ▲{stats['edges_added']} edg\n"
                f"Removed: ▼{stats['nodes_removed']} nd | ▼{stats['edges_removed']} edg"
            )
            
            ax.text(
                0.5, 0.02,
                stats_text,
                transform=ax.transAxes,
                ha='center',
                fontsize=10,
                bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.4')
            )
            
            # Legend
            ax.legend(handles=legend_elements, loc='upper right', frameon=True, 
                     framealpha=0.9, facecolor=colors['bg'])
            
            ax.set_axis_off()
            # Dynamic margins based on graph size
            ax.margins(0.15 + 0.05 * (node_count/20))
            
        except Exception as e:
            print(f'Error at step {i}: {e}')
    
    # Create animation
    ani = FuncAnimation(
        fig, update,
        frames=steps,
        interval=interval,
        repeat=False
    )
    plt.tight_layout()
    plt.show()
    return ani
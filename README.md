# DynamicWalker

## Adaptive navigation in evolving networks

**Core Features:**

1. **Dynamic Graph Generation**
   - Multiple growth strategies:
     - Random connections
     - Preferential attachment
     - Aging-based connections
   - Parameter control:
     - Node degree limits
     - Component management
     - Aging rates

2. **Biased Random Walk Navigation**
   - Activity-based traversal 
   - Degree-weighted movement 
   - Cross-component teleportation 
   - Configurable exploration/exploitation balance
   - Adaptive walker memory and decay

3. **Visualization**
   - Real-time animation of walker movements
   - Agent path tracking with history
   - Degree-based node coloring and scaling
   - Current walker position highlighting

**Dependencies:**
- Python 3.8+
- NetworkX 2.6+
- Matplotlib 3.5+

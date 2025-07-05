from .random_strategy import RandomStrategy
from .preferential_strategy import PreferentialStrategy
from .aging_strategy import AgingStrategy

class StrategyFactory:
    """Factory class for creating graph growth strategy instances."""
    
    # Registry of available strategies
    STRATEGIES = {
        "random": RandomStrategy,
        "preferential": PreferentialStrategy,
        "aging": AgingStrategy
    }
    
    @staticmethod
    def create(strategy_name, graph, config):
        """
        Create and return a strategy instance.
        """
        strategy_class = StrategyFactory.STRATEGIES.get(strategy_name.lower())
        if not strategy_class:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        return strategy_class(graph, config)
from typing import Dict, Any, Callable
from .node_context import NodeContext

class WorkflowEngine:
    def __init__(self):
        self.node_handlers: Dict[str, Callable] = {}
        self.edge_handlers: Dict[str, Callable] = {}
        
    def register_node_handler(self, node_type: str, handler: Callable):
        self.node_handlers[node_type] = handler
        
    def register_edge_handler(self, from_node: str, to_node: str, handler: Callable):
        edge_key = f"{from_node}->{to_node}"
        self.edge_handlers[edge_key] = handler
        
    def handle_node(self, context: NodeContext):
        if context.node_type in self.node_handlers:
            return self.node_handlers[context.node_type](context)
        return context.output_data
        
    def handle_edge(self, from_node: str, to_node: str, data: Any):
        edge_key = f"{from_node}->{to_node}"
        if edge_key in self.edge_handlers:
            return self.edge_handlers[edge_key](data)
        return data

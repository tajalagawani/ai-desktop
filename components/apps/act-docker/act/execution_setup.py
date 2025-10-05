# execution_setup.py
from .execution_manager import ExecutionManager
from .handlers import chat_handler, chat_to_slack_handler

def setup_execution_manager(actfile_path: str) -> ExecutionManager:
    manager = ExecutionManager(actfile_path)
    
    # Register handlers
    manager.workflow_engine.register_node_handler("ChatModels", chat_handler)
    manager.workflow_engine.register_edge_handler(
        "chatmodels_test", 
        "slack_test",
        "aggregatenode",
       
    )
    
    return manager
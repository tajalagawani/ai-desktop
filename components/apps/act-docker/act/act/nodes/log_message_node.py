from .base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType, NodeValidationError; import logging, json; logger = logging.getLogger(__name__); class LogMessageNode(BaseNode):
        _VALID_LOG_LEVELS = ["debug", "info", "warning", "error", "critical"]
        def get_schema(self): return NodeSchema(node_type='LogMessage', version='1.0', description='', parameters=[NodeParameter(name='message', type=NodeParameterType.STRING, description=''), NodeParameter(name='level', type=NodeParameterType.STRING, description='', default='info', enum=self._VALID_LOG_LEVELS)], outputs={'logged_level': NodeParameterType.STRING})
        async def execute(self, node_data: dict) -> dict:
            params = node_data.get('params', {}); message = params.get('message', 'No message'); level = str(params.get('level', 'info')).lower(); node_name = node_data.get('__node_name', 'LogMessageNode')
            if level not in self._VALID_LOG_LEVELS: level = 'info'
            log_func = getattr(logger, level, logger.info); log_output = f"[{node_name}] {message}"; log_func(log_output)
            return {"status": "success", "message": f"Message logged at level '{level}'.", "result": {"logged_level": level, "logged_message": message}}
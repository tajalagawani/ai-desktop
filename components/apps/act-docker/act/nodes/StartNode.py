"""
Start Node - Initiates workflow execution with configurable parameters.
Used as an entry point for workflows, allowing initial data setup and scheduling.
"""

import logging
import json
import os
import sys
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import time
import threading
import queue
import re

try:
    from base_node import (
        BaseNode, NodeSchema, NodeParameter, NodeParameterType,
        NodeValidationError
    )
except ImportError:
    try:
        from base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError
        )
    except ImportError:
        from base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError
        )

# Configure logging
logger = logging.getLogger(__name__)

class StartNodeOperation:
    """Operations available on the Start Node."""
    INITIALIZE = "initialize"
    PROVIDE_CONTEXT = "provide_context"
    SET_VARIABLES = "set_variables"
    LOAD_CONFIG = "load_config"
    SCHEDULE = "schedule"
    CHECK_SCHEDULE = "check_schedule"
    CANCEL_SCHEDULE = "cancel_schedule"

class ScheduleType:
    """Schedule types supported by the Start Node."""
    ONCE = "once"
    INTERVAL = "interval"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CRON = "cron"

class StartNode(BaseNode):
    """
    Node for starting workflows and initializing execution context.
    Serves as the entry point for workflow execution.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.execution_manager = None
        self.scheduled_tasks = {}
        self.schedule_lock = threading.Lock()
        self.scheduler_thread = None
        self.scheduler_queue = queue.Queue()
        self.scheduler_running = False
        
    def set_execution_manager(self, execution_manager):
        """Set the execution manager for this node."""
        self.execution_manager = execution_manager
        
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the Start node."""
        return NodeSchema(
            node_type="start",
            version="1.0.0",
            description="Initiates workflow execution with configurable parameters",
            parameters=[
                # Basic parameters
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Operation to perform with the Start node",
                    required=False,
                    enum=[
                        StartNodeOperation.INITIALIZE,
                        StartNodeOperation.PROVIDE_CONTEXT,
                        StartNodeOperation.SET_VARIABLES,
                        StartNodeOperation.LOAD_CONFIG,
                        StartNodeOperation.SCHEDULE,
                        StartNodeOperation.CHECK_SCHEDULE,
                        StartNodeOperation.CANCEL_SCHEDULE
                    ],
                    default=StartNodeOperation.INITIALIZE
                ),
                NodeParameter(
                    name="workflow_name",
                    type=NodeParameterType.STRING,
                    description="Name of the workflow being executed",
                    required=False
                ),
                NodeParameter(
                    name="description",
                    type=NodeParameterType.STRING,
                    description="Description of the workflow purpose",
                    required=False
                ),
                NodeParameter(
                    name="variables",
                    type=NodeParameterType.OBJECT,
                    description="Initial variables for the workflow",
                    required=False
                ),
                NodeParameter(
                    name="config_path",
                    type=NodeParameterType.STRING,
                    description="Path to configuration file",
                    required=False
                ),
                NodeParameter(
                    name="environment",
                    type=NodeParameterType.STRING,
                    description="Execution environment (dev, test, prod)",
                    required=False,
                    default="dev"
                ),
                NodeParameter(
                    name="debug",
                    type=NodeParameterType.BOOLEAN,
                    description="Enable debug mode",
                    required=False,
                    default=False
                ),
                
                # Scheduling parameters
                NodeParameter(
                    name="schedule_id",
                    type=NodeParameterType.STRING,
                    description="Unique identifier for the schedule",
                    required=False
                ),
                NodeParameter(
                    name="schedule_type",
                    type=NodeParameterType.STRING,
                    description="Type of schedule",
                    required=False,
                    enum=[
                        ScheduleType.ONCE,
                        ScheduleType.INTERVAL,
                        ScheduleType.DAILY,
                        ScheduleType.WEEKLY,
                        ScheduleType.MONTHLY,
                        ScheduleType.CRON
                    ]
                ),
                NodeParameter(
                    name="datetime",
                    type=NodeParameterType.STRING,
                    description="Date and time for one-time schedule (ISO format)",
                    required=False
                ),
                NodeParameter(
                    name="interval_seconds",
                    type=NodeParameterType.NUMBER,
                    description="Interval in seconds for interval schedules",
                    required=False
                ),
                NodeParameter(
                    name="time_of_day",
                    type=NodeParameterType.STRING,
                    description="Time of day for daily schedules (HH:MM format)",
                    required=False
                ),
                NodeParameter(
                    name="day_of_week",
                    type=NodeParameterType.NUMBER,
                    description="Day of week for weekly schedules (0=Monday, 6=Sunday)",
                    required=False
                ),
                NodeParameter(
                    name="day_of_month",
                    type=NodeParameterType.NUMBER,
                    description="Day of month for monthly schedules",
                    required=False
                ),
                NodeParameter(
                    name="cron_expression",
                    type=NodeParameterType.STRING,
                    description="Cron expression for cron schedules",
                    required=False
                ),
                NodeParameter(
                    name="max_executions",
                    type=NodeParameterType.NUMBER,
                    description="Maximum number of executions (0=unlimited)",
                    required=False,
                    default=0
                ),
                NodeParameter(
                    name="callback",
                    type=NodeParameterType.OBJECT,
                    description="Callback to execute when scheduled time is reached",
                    required=False
                )
            ],

            outputs={
                "status": NodeParameterType.STRING,
                "message": NodeParameterType.STRING,
                "data": NodeParameterType.OBJECT,
                "timestamp": NodeParameterType.STRING,
                "workflow_name": NodeParameterType.STRING,
                "environment": NodeParameterType.STRING,
                "schedule_id": NodeParameterType.STRING
            },
            
            # Add metadata
            tags=["workflow", "initialization", "entry-point", "scheduling"],
            author="System"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation based on operation type."""
        params = node_data.get("params", {})
        operation = params.get("operation", StartNodeOperation.INITIALIZE)
        
        # Validate based on operation
        if operation == StartNodeOperation.INITIALIZE:
            if not params.get("workflow_name"):
                # Not strictly required but give a warning
                logger.warning("No workflow_name provided for initialization")
                
        elif operation == StartNodeOperation.SET_VARIABLES:
            if not params.get("variables"):
                raise NodeValidationError("Variables are required for SET_VARIABLES operation")
                
        elif operation == StartNodeOperation.LOAD_CONFIG:
            config_path = params.get("config_path")
            if not config_path:
                raise NodeValidationError("Config path is required for LOAD_CONFIG operation")
            
            if not os.path.exists(config_path):
                raise NodeValidationError(f"Config file not found: {config_path}")
                
        elif operation == StartNodeOperation.SCHEDULE:
            schedule_id = params.get("schedule_id")
            schedule_type = params.get("schedule_type")
            
            if not schedule_id:
                raise NodeValidationError("Schedule ID is required for SCHEDULE operation")
            
            if not schedule_type:
                raise NodeValidationError("Schedule type is required for SCHEDULE operation")
            
            # Validate parameters based on schedule type
            if schedule_type == ScheduleType.ONCE:
                if not params.get("datetime"):
                    raise NodeValidationError("Datetime is required for one-time schedules")
                    
            elif schedule_type == ScheduleType.INTERVAL:
                if not params.get("interval_seconds"):
                    raise NodeValidationError("Interval seconds is required for interval schedules")
                    
            elif schedule_type == ScheduleType.DAILY:
                if not params.get("time_of_day"):
                    raise NodeValidationError("Time of day is required for daily schedules")
                    
            elif schedule_type == ScheduleType.WEEKLY:
                if not params.get("day_of_week") and not isinstance(params.get("day_of_week"), int):
                    raise NodeValidationError("Day of week is required for weekly schedules")
                if not params.get("time_of_day"):
                    raise NodeValidationError("Time of day is required for weekly schedules")
                    
            elif schedule_type == ScheduleType.MONTHLY:
                if not params.get("day_of_month") and not isinstance(params.get("day_of_month"), int):
                    raise NodeValidationError("Day of month is required for monthly schedules")
                if not params.get("time_of_day"):
                    raise NodeValidationError("Time of day is required for monthly schedules")
                    
            elif schedule_type == ScheduleType.CRON:
                if not params.get("cron_expression"):
                    raise NodeValidationError("Cron expression is required for cron schedules")
                    
        elif operation == StartNodeOperation.CANCEL_SCHEDULE:
            if not params.get("schedule_id"):
                raise NodeValidationError("Schedule ID is required to cancel a schedule")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Start node."""
        try:
            # Extract parameters
            params = node_data.get("params", {})
            operation = params.get("operation", StartNodeOperation.INITIALIZE)
            
            # Set debug mode if specified
            if params.get("debug", False):
                logging.getLogger().setLevel(logging.DEBUG)
                logger.debug("Debug mode enabled")
            
            # Start scheduler thread if needed for scheduling operations
            if operation in [StartNodeOperation.SCHEDULE, StartNodeOperation.CHECK_SCHEDULE, StartNodeOperation.CANCEL_SCHEDULE]:
                self._ensure_scheduler_running()
            
            # Execute the appropriate operation
            if operation == StartNodeOperation.INITIALIZE:
                return self._operation_initialize(params)
            elif operation == StartNodeOperation.PROVIDE_CONTEXT:
                return self._operation_provide_context(params)
            elif operation == StartNodeOperation.SET_VARIABLES:
                return self._operation_set_variables(params)
            elif operation == StartNodeOperation.LOAD_CONFIG:
                return self._operation_load_config(params)
            elif operation == StartNodeOperation.SCHEDULE:
                return self._operation_schedule(params)
            elif operation == StartNodeOperation.CHECK_SCHEDULE:
                return self._operation_check_schedule(params)
            elif operation == StartNodeOperation.CANCEL_SCHEDULE:
                return self._operation_cancel_schedule(params)
            else:
                error_message = f"Unknown operation: {operation}"
                logger.error(error_message)
                return {
                    "status": "error",
                    "message": error_message,
                    "data": None,
                    "timestamp": datetime.now().isoformat(),
                    "workflow_name": params.get("workflow_name", "unknown"),
                    "environment": params.get("environment", "dev")
                }
                
        except Exception as e:
            error_message = f"Error in Start node: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "message": error_message,
                "data": None,
                "timestamp": datetime.now().isoformat(),
                "workflow_name": params.get("workflow_name", "unknown"),
                "environment": params.get("environment", "dev")
            }
    
    # -------------------------
    # Operation Methods
    # -------------------------
    
    def _operation_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initialize the workflow with basic configuration.
        
        Args:
            params: Initialization parameters
            
        Returns:
            Initialization results
        """
        workflow_name = params.get("workflow_name", "Unnamed Workflow")
        description = params.get("description", "")
        environment = params.get("environment", "dev")
        
        logger.info(f"Initializing workflow: {workflow_name}")
        logger.info(f"Environment: {environment}")
        
        if description:
            logger.info(f"Description: {description}")
        
        # Prepare initial data
        initial_data = {
            "workflow_info": {
                "name": workflow_name,
                "description": description,
                "environment": environment,
                "start_time": datetime.now().isoformat()
            },
            "variables": params.get("variables", {}),
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "cwd": os.getcwd()
            }
        }
        
        return {
            "status": "success",
            "message": f"Successfully initialized workflow: {workflow_name}",
            "data": initial_data,
            "timestamp": datetime.now().isoformat(),
            "workflow_name": workflow_name,
            "environment": environment
        }
    
    def _operation_provide_context(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide execution context information.
        
        Args:
            params: Context parameters
            
        Returns:
            Context information
        """
        workflow_name = params.get("workflow_name", "Unnamed Workflow")
        environment = params.get("environment", "dev")
        
        # Collect environment variables (being careful not to expose sensitive ones)
        safe_env_vars = {}
        sensitive_keys = ["KEY", "SECRET", "PASSWORD", "TOKEN", "CREDENTIAL"]
        
        for key, value in os.environ.items():
            # Skip sensitive environment variables
            if any(sensitive_word in key.upper() for sensitive_word in sensitive_keys):
                safe_env_vars[key] = "[REDACTED]"
            else:
                safe_env_vars[key] = value
        
        # Get system context info
        context_data = {
            "environment": environment,
            "system": {
                "python_version": sys.version,
                "platform": sys.platform,
                "cwd": os.getcwd(),
                "argv": sys.argv
            },
            "environment_vars": safe_env_vars,
            "workflow_name": workflow_name,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add execution manager info if available
        if self.execution_manager:
            context_data["execution_info"] = {
                "actfile_path": str(getattr(self.execution_manager, "actfile_path", "")),
                "sandbox_timeout": getattr(self.execution_manager, "sandbox_timeout", 0),
                "node_count": len(getattr(self.execution_manager, "workflow_data", {}).get("nodes", {}))
            }
        
        # Add scheduled tasks info
        with self.schedule_lock:
            context_data["scheduled_tasks"] = {
                "count": len(self.scheduled_tasks),
                "tasks": [task_id for task_id in self.scheduled_tasks.keys()]
            }
        
        return {
            "status": "success",
            "message": "Successfully gathered execution context",
            "data": context_data,
            "timestamp": datetime.now().isoformat(),
            "workflow_name": workflow_name,
            "environment": environment
        }
    
    def _operation_set_variables(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set variables for the workflow.
        
        Args:
            params: Variable parameters
            
        Returns:
            Variables setting results
        """
        workflow_name = params.get("workflow_name", "Unnamed Workflow")
        environment = params.get("environment", "dev")
        variables = params.get("variables", {})
        
        if not variables:
            return {
                "status": "warning",
                "message": "No variables provided",
                "data": {"variables": {}},
                "timestamp": datetime.now().isoformat(),
                "workflow_name": workflow_name,
                "environment": environment
            }
        
        logger.info(f"Setting {len(variables)} variables for workflow: {workflow_name}")
        
        # Process variables with environment expansion if needed
        processed_variables = {}
        for key, value in variables.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                processed_variables[key] = os.environ.get(env_var, value)
            else:
                processed_variables[key] = value
        
        return {
            "status": "success",
            "message": f"Successfully set {len(processed_variables)} variables",
            "data": {"variables": processed_variables},
            "timestamp": datetime.now().isoformat(),
            "workflow_name": workflow_name,
            "environment": environment
        }
    
    def _operation_load_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Args:
            params: Config parameters
            
        Returns:
            Configuration loading results
        """
        workflow_name = params.get("workflow_name", "Unnamed Workflow")
        environment = params.get("environment", "dev")
        config_path = params.get("config_path")
        
        if not config_path:
            return {
                "status": "error",
                "message": "No config path provided",
                "data": None,
                "timestamp": datetime.now().isoformat(),
                "workflow_name": workflow_name,
                "environment": environment
            }
        
        try:
            # Support different file formats
            if config_path.endswith('.json'):
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
            elif config_path.endswith(('.yaml', '.yml')):
                try:
                    import yaml
                    with open(config_path, 'r') as f:
                        config_data = yaml.safe_load(f)
                except ImportError:
                    return {
                        "status": "error",
                        "message": "YAML support requires PyYAML package",
                        "data": None,
                        "timestamp": datetime.now().isoformat(),
                        "workflow_name": workflow_name,
                        "environment": environment
                    }
            else:
                return {
                    "status": "error",
                    "message": f"Unsupported configuration file format: {config_path}",
                    "data": None,
                    "timestamp": datetime.now().isoformat(),
                    "workflow_name": workflow_name,
                    "environment": environment
                }
                
            # Apply environment-specific configuration if available
            if isinstance(config_data, dict) and "environments" in config_data and environment in config_data["environments"]:
                env_config = config_data["environments"][environment]
                # Merge with base config
                base_config = {k: v for k, v in config_data.items() if k != "environments"}
                merged_config = {**base_config, **env_config}
                config_data = merged_config
            
            logger.info(f"Successfully loaded configuration from {config_path}")
            
            return {
                "status": "success",
                "message": f"Successfully loaded configuration from {config_path}",
                "data": {"config": config_data},
                "timestamp": datetime.now().isoformat(),
                "workflow_name": workflow_name,
                "environment": environment
            }
            
        except FileNotFoundError:
            error_message = f"Configuration file not found: {config_path}"
            logger.error(error_message)
            return {
                "status": "error",
                "message": error_message,
                "data": None,
                "timestamp": datetime.now().isoformat(),
                "workflow_name": workflow_name,
                "environment": environment
            }
        except json.JSONDecodeError as e:
            error_message = f"Invalid JSON in configuration file: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "message": error_message,
                "data": None,
                "timestamp": datetime.now().isoformat(),
                "workflow_name": workflow_name,
                "environment": environment
            }
        except Exception as e:
            error_message = f"Error loading configuration: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "message": error_message,
                "data": None,
                "timestamp": datetime.now().isoformat(),
                "workflow_name": workflow_name,
                "environment": environment
            }
    
    def _operation_schedule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule a workflow execution.
        
        Args:
            params: Schedule parameters
            
        Returns:
            Scheduling results
        """
        workflow_name = params.get("workflow_name", "Unnamed Workflow")
        environment = params.get("environment", "dev")
        schedule_id = params.get("schedule_id")
        schedule_type = params.get("schedule_type")
        max_executions = params.get("max_executions", 0)
        
        # Make sure scheduler is running
        self._ensure_scheduler_running()
        
        # Calculate next execution time based on schedule type
        next_execution = None
        interval_seconds = None
        schedule_info = {
            "id": schedule_id,
            "type": schedule_type,
            "workflow_name": workflow_name,
            "environment": environment,
            "params": params,
            "created_at": datetime.now().isoformat(),
            "execution_count": 0,
            "max_executions": max_executions,
            "status": "scheduled",
            "last_execution": None,
            "callback": params.get("callback")
        }
        
        # Calculate next execution time based on schedule type
        try:
            if schedule_type == ScheduleType.ONCE:
                # One-time schedule
                datetime_str = params.get("datetime")
                next_execution = datetime.fromisoformat(datetime_str)
                
            elif schedule_type == ScheduleType.INTERVAL:
                # Interval schedule
                interval_seconds = params.get("interval_seconds")
                next_execution = datetime.now() + timedelta(seconds=interval_seconds)
                schedule_info["interval_seconds"] = interval_seconds
                
            elif schedule_type == ScheduleType.DAILY:
                # Daily schedule
                time_of_day = params.get("time_of_day")
                hours, minutes = map(int, time_of_day.split(':'))
                next_execution = self._get_next_daily_execution(hours, minutes)
                schedule_info["time_of_day"] = time_of_day
                
            elif schedule_type == ScheduleType.WEEKLY:
                # Weekly schedule
                day_of_week = params.get("day_of_week")
                time_of_day = params.get("time_of_day")
                hours, minutes = map(int, time_of_day.split(':'))
                next_execution = self._get_next_weekly_execution(day_of_week, hours, minutes)
                schedule_info["day_of_week"] = day_of_week
                schedule_info["time_of_day"] = time_of_day
                
            elif schedule_type == ScheduleType.MONTHLY:
                # Monthly schedule
                day_of_month = params.get("day_of_month")
                time_of_day = params.get("time_of_day")
                hours, minutes = map(int, time_of_day.split(':'))
                next_execution = self._get_next_monthly_execution(day_of_month, hours, minutes)
                schedule_info["day_of_month"] = day_of_month
                schedule_info["time_of_day"] = time_of_day
                
            elif schedule_type == ScheduleType.CRON:
                # Cron schedule
                cron_expression = params.get("cron_expression")
                next_execution = self._get_next_cron_execution(cron_expression)
                schedule_info["cron_expression"] = cron_expression
            
            if next_execution is None:
                return {
                    "status": "error",
                    "message": f"Could not calculate next execution time for schedule type: {schedule_type}",
                    "data": None,
                    "timestamp": datetime.now().isoformat(),
                    "workflow_name": workflow_name,
                    "environment": environment,
                    "schedule_id": schedule_id
                }
                
            schedule_info["next_execution"] = next_execution.isoformat()
            
            # Store schedule info
            with self.schedule_lock:
                self.scheduled_tasks[schedule_id] = schedule_info
            
            # Enqueue the schedule
            self.scheduler_queue.put({
                "schedule_id": schedule_id,
                "execution_time": next_execution,
                "schedule_info": schedule_info
            })
            
            logger.info(f"Successfully scheduled task '{schedule_id}' for {next_execution.isoformat()}")
            
            return {
                "status": "success",
                "message": f"Successfully scheduled task '{schedule_id}' for {next_execution.isoformat()}",
                "data": {
                    "schedule": schedule_info
                },
                "timestamp": datetime.now().isoformat(),
                "workflow_name": workflow_name,
                "environment": environment,
                "schedule_id": schedule_id
            }
            
        except Exception as e:
            error_message = f"Error scheduling task: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "message": error_message,
                "data": None,
                "timestamp": datetime.now().isoformat(),
                "workflow_name": workflow_name,
                "environment": environment,
                "schedule_id": schedule_id
            }
    
    def _operation_check_schedule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check status of scheduled executions.
        
        Args:
            params: Check parameters
            
        Returns:
            Schedule status information
        """
        workflow_name = params.get("workflow_name", "Unnamed Workflow")
        environment = params.get("environment", "dev")
        schedule_id = params.get("schedule_id")
        
        with self.schedule_lock:
            if schedule_id:
                # Check specific schedule
                if schedule_id in self.scheduled_tasks:
                    schedule_info = self.scheduled_tasks[schedule_id]
                    return {
                        "status": "success",
                        "message": f"Found schedule '{schedule_id}'",
                        "data": {"schedule": schedule_info},
                        "timestamp": datetime.now().isoformat(),
                        "workflow_name": workflow_name,
                        "environment": environment,
                        "schedule_id": schedule_id
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Schedule '{schedule_id}' not found",
                        "data": None,
                        "timestamp": datetime.now().isoformat(),
                        "workflow_name": workflow_name,
                        "environment": environment,
                        "schedule_id": schedule_id
                    }
            else:
                # Return all schedules
                schedules = list(self.scheduled_tasks.values())
                return {
                    "status": "success",
                    "message": f"Found {len(schedules)} scheduled tasks",
                    "data": {"schedules": schedules},
                    "timestamp": datetime.now().isoformat(),
                    "workflow_name": workflow_name,
                    "environment": environment
                }
    
    def _operation_cancel_schedule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cancel a scheduled execution.
        
        Args:
            params: Cancel parameters
            
        Returns:
            Cancellation results
        """
        workflow_name = params.get("workflow_name", "Unnamed Workflow")
        environment = params.get("environment", "dev")
        schedule_id = params.get("schedule_id")
        
        with self.schedule_lock:
            if schedule_id in self.scheduled_tasks:
                schedule_info = self.scheduled_tasks[schedule_id]
                schedule_info["status"] = "cancelled"
                del self.scheduled_tasks[schedule_id]
                
                return {
                    "status": "success",
                    "message": f"Successfully cancelled schedule '{schedule_id}'",
                    "data": {"schedule": schedule_info},
                    "timestamp": datetime.now().isoformat(),
                    "workflow_name": workflow_name,
                    "environment": environment,
                    "schedule_id": schedule_id
                }
            else:
                return {
                    "status": "error",
                    "message": f"Schedule '{schedule_id}' not found",
                    "data": None,
                    "timestamp": datetime.now().isoformat(),
                    "workflow_name": workflow_name,
                    "environment": environment,
                    "schedule_id": schedule_id
                }
    
    # -------------------------
    # Scheduling Helper Methods
    # -------------------------
    
    def _ensure_scheduler_running(self):
        """
        Ensure the scheduler thread is running.
        """
        if self.scheduler_thread is None or not self.scheduler_thread.is_alive():
            logger.info("Starting scheduler thread")
            self.scheduler_running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()
    
    def _scheduler_loop(self):
        """
        Main scheduler loop that processes scheduled tasks.
        """
        logger.info("Scheduler thread started")
        
        while self.scheduler_running:
            try:
                # Process any new schedules in the queue
                while not self.scheduler_queue.empty():
                    try:
                        schedule_item = self.scheduler_queue.get_nowait()
                        logger.debug(f"Processed new schedule: {schedule_item['schedule_id']}")
                    except queue.Empty:
                        break
                
                # Check if any scheduled tasks need to be executed
                now = datetime.now()
                tasks_to_execute = []
                tasks_to_reschedule = []
                
                with self.schedule_lock:
                    for schedule_id, schedule_info in list(self.scheduled_tasks.items()):
                        if schedule_info["status"] == "cancelled":
                            continue
                            
                        next_execution_str = schedule_info.get("next_execution")
                        if not next_execution_str:
                            continue
                            
                        next_execution = datetime.fromisoformat(next_execution_str)
                        
                        if now >= next_execution:
                            # Time to execute this task
                            tasks_to_execute.append((schedule_id, schedule_info))
                
                # Execute tasks that are due
                for schedule_id, schedule_info in tasks_to_execute:
                    self._execute_scheduled_task(schedule_id, schedule_info)
                    
                    # Calculate next execution time if needed
                    schedule_type = schedule_info["type"]
                    
                    # For repeating schedules, calculate the next execution time
                    if schedule_type == ScheduleType.INTERVAL:
                        # For interval schedules, add the interval to the current time
                        interval_seconds = schedule_info.get("interval_seconds")
                        next_execution = datetime.now() + timedelta(seconds=interval_seconds)
                        tasks_to_reschedule.append((schedule_id, schedule_info, next_execution))
                        
                    elif schedule_type == ScheduleType.DAILY:
                        # Daily schedule
                        time_of_day = schedule_info.get("time_of_day")
                        hours, minutes = map(int, time_of_day.split(':'))
                        next_execution = self._get_next_daily_execution(hours, minutes)
                        tasks_to_reschedule.append((schedule_id, schedule_info, next_execution))
                        
                    elif schedule_type == ScheduleType.WEEKLY:
                        # Weekly schedule
                        day_of_week = schedule_info.get("day_of_week")
                        time_of_day = schedule_info.get("time_of_day")
                        hours, minutes = map(int, time_of_day.split(':'))
                        next_execution = self._get_next_weekly_execution(day_of_week, hours, minutes)
                        tasks_to_reschedule.append((schedule_id, schedule_info, next_execution))
                        
                    elif schedule_type == ScheduleType.MONTHLY:
                        # Monthly schedule
                        day_of_month = schedule_info.get("day_of_month")
                        time_of_day = schedule_info.get("time_of_day")
                        hours, minutes = map(int, time_of_day.split(':'))
                        next_execution = self._get_next_monthly_execution(day_of_month, hours, minutes)
                        tasks_to_reschedule.append((schedule_id, schedule_info, next_execution))
                        
                    elif schedule_type == ScheduleType.CRON:
                        # Cron schedule
                        cron_expression = schedule_info.get("cron_expression")
                        next_execution = self._get_next_cron_execution(cron_expression)
                        tasks_to_reschedule.append((schedule_id, schedule_info, next_execution))
                
                # Reschedule tasks that need to be rescheduled
                with self.schedule_lock:
                    for schedule_id, schedule_info, next_execution in tasks_to_reschedule:
                        # Check if we've reached the maximum executions
                        max_executions = schedule_info.get("max_executions", 0)
                        execution_count = schedule_info.get("execution_count", 0)
                        
                        if max_executions > 0 and execution_count >= max_executions:
                            # Maximum executions reached, remove from scheduled tasks
                            schedule_info["status"] = "completed"
                            logger.info(f"Schedule '{schedule_id}' completed (reached max executions)")
                        else:
                            # Update the next execution time
                            schedule_info["next_execution"] = next_execution.isoformat()
                            self.scheduled_tasks[schedule_id] = schedule_info
                            logger.debug(f"Rescheduled '{schedule_id}' for {next_execution.isoformat()}")
                
                # Sleep for a short time to avoid busy-waiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                logger.error(f"Traceback: {str(e)}")
                time.sleep(5)  # Sleep longer on error
    
    def _execute_scheduled_task(self, schedule_id: str, schedule_info: Dict[str, Any]):
        """
        Execute a scheduled task.
        
        Args:
            schedule_id: ID of the schedule to execute
            schedule_info: Schedule information
        """
        logger.info(f"Executing scheduled task: {schedule_id}")
        
        try:
            # Update execution count and last execution time
            with self.schedule_lock:
                if schedule_id in self.scheduled_tasks:
                    schedule_info = self.scheduled_tasks[schedule_id]
                    schedule_info["execution_count"] = schedule_info.get("execution_count", 0) + 1
                    schedule_info["last_execution"] = datetime.now().isoformat()
                    schedule_info["status"] = "running"
                    self.scheduled_tasks[schedule_id] = schedule_info
            
            # Execute the callback if available
            callback = schedule_info.get("callback")
            if callback:
                if isinstance(callback, dict) and "node" in callback and "params" in callback:
                    # Execute a node with parameters
                    node_name = callback["node"]
                    params = callback["params"]
                    
                    if self.execution_manager:
                        try:
                            logger.info(f"Executing callback node: {node_name}")
                            result = self.execution_manager.execute_node(node_name, params)
                            
                            # Update the schedule info with the result
                            with self.schedule_lock:
                                if schedule_id in self.scheduled_tasks:
                                    schedule_info = self.scheduled_tasks[schedule_id]
                                    schedule_info["last_result"] = result
                                    schedule_info["status"] = "waiting"
                                    self.scheduled_tasks[schedule_id] = schedule_info
                                    
                            logger.info(f"Callback execution completed: {result.get('status', 'unknown')}")
                        except Exception as e:
                            logger.error(f"Error executing callback node: {str(e)}")
                    else:
                        logger.error("Cannot execute callback: execution_manager not available")
                else:
                    logger.warning(f"Invalid callback format: {callback}")
            else:
                logger.info("No callback specified for scheduled task")
                
                # Update status to waiting
                with self.schedule_lock:
                    if schedule_id in self.scheduled_tasks:
                        schedule_info = self.scheduled_tasks[schedule_id]
                        schedule_info["status"] = "waiting"
                        self.scheduled_tasks[schedule_id] = schedule_info
            
        except Exception as e:
            logger.error(f"Error executing scheduled task '{schedule_id}': {str(e)}")
            
            # Update status to error
            with self.schedule_lock:
                if schedule_id in self.scheduled_tasks:
                    schedule_info = self.scheduled_tasks[schedule_id]
                    schedule_info["status"] = "error"
                    schedule_info["error"] = str(e)
                    self.scheduled_tasks[schedule_id] = schedule_info
    
    def _get_next_daily_execution(self, hours: int, minutes: int) -> datetime:
        """
        Calculate the next execution time for a daily schedule.
        
        Args:
            hours: Hour of the day (0-23)
            minutes: Minute of the hour (0-59)
            
        Returns:
            Next execution time
        """
        now = datetime.now()
        next_execution = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
        
        # If the time has already passed today, schedule for tomorrow
        if next_execution <= now:
            next_execution += timedelta(days=1)
            
        return next_execution
    
    def _get_next_weekly_execution(self, day_of_week: int, hours: int, minutes: int) -> datetime:
        """
        Calculate the next execution time for a weekly schedule.
        
        Args:
            day_of_week: Day of the week (0=Monday, 6=Sunday)
            hours: Hour of the day (0-23)
            minutes: Minute of the hour (0-59)
            
        Returns:
            Next execution time
        """
        now = datetime.now()
        
        # Calculate days until the next specified day of week
        current_day_of_week = now.weekday()  # 0=Monday, 6=Sunday
        days_ahead = day_of_week - current_day_of_week
        
        if days_ahead < 0:  # Target day has already passed this week
            days_ahead += 7
        elif days_ahead == 0:  # Today is the target day
            # Check if the time has already passed
            target_time = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
            if target_time <= now:
                days_ahead = 7  # Schedule for next week
        
        next_execution = now.replace(hour=hours, minute=minutes, second=0, microsecond=0) + timedelta(days=days_ahead)
        return next_execution
    
    def _get_next_monthly_execution(self, day_of_month: int, hours: int, minutes: int) -> datetime:
        """
        Calculate the next execution time for a monthly schedule.
        
        Args:
            day_of_month: Day of the month (1-31)
            hours: Hour of the day (0-23)
            minutes: Minute of the hour (0-59)
            
        Returns:
            Next execution time
        """
        import calendar
        now = datetime.now()
        
        # Try to set the day of month
        year = now.year
        month = now.month
        
        # Get the last day of the current month
        _, last_day = calendar.monthrange(year, month)
        
        # Adjust day_of_month if it exceeds the last day of the month
        effective_day = min(day_of_month, last_day)
        
        # Create the target datetime for this month
        target_date = now.replace(day=effective_day, hour=hours, minute=minutes, second=0, microsecond=0)
        
        # If the target date has already passed this month, move to next month
        if target_date <= now:
            # Move to the next month
            if month == 12:
                year += 1
                month = 1
            else:
                month += 1
                
            # Get the last day of the next month
            _, last_day = calendar.monthrange(year, month)
            
            # Adjust day_of_month if it exceeds the last day of the next month
            effective_day = min(day_of_month, last_day)
            
            # Create the target datetime for the next month
            target_date = now.replace(year=year, month=month, day=effective_day, 
                                     hour=hours, minute=minutes, second=0, microsecond=0)
        
        return target_date
    
    def _get_next_cron_execution(self, cron_expression: str) -> datetime:
        """
        Calculate the next execution time for a cron schedule.
        
        Args:
            cron_expression: Cron expression
            
        Returns:
            Next execution time
        """
        try:
            # Try to use croniter package if available
            from croniter import croniter
            now = datetime.now()
            cron = croniter(cron_expression, now)
            return cron.get_next(datetime)
        except ImportError:
            logger.warning("croniter package not available, using simple cron parser")
            return self._simple_cron_parser(cron_expression)
    
    def _simple_cron_parser(self, cron_expression: str) -> datetime:
        """
        Simple cron expression parser for when croniter is not available.
        Only supports a subset of cron functionality.
        
        Args:
            cron_expression: Cron expression (minute hour day_of_month month day_of_week)
            
        Returns:
            Next execution time
        """
        now = datetime.now()
        parts = cron_expression.split()
        
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression: {cron_expression}, expected 5 fields")
        
        minute, hour, day_of_month, month, day_of_week = parts
        
        # Start with tomorrow at midnight
        next_execution = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        # Handle simple patterns only
        if minute != "*" and not minute.startswith("*/"):
            minutes = self._parse_cron_field(minute, 0, 59)
            next_execution = next_execution.replace(minute=minutes[0])
        
        if hour != "*" and not hour.startswith("*/"):
            hours = self._parse_cron_field(hour, 0, 23)
            next_execution = next_execution.replace(hour=hours[0])
        
        return next_execution
    
    def _parse_cron_field(self, field: str, min_val: int, max_val: int) -> List[int]:
        """
        Parse a cron field into a list of values.
        
        Args:
            field: Cron field
            min_val: Minimum value for the field
            max_val: Maximum value for the field
            
        Returns:
            List of values
        """
        result = []
        
        # Handle specific values
        if field.isdigit():
            val = int(field)
            if min_val <= val <= max_val:
                result.append(val)
        # Handle ranges
        elif "-" in field:
            start, end = map(int, field.split("-"))
            result.extend(range(start, end + 1))
        # Handle lists
        elif "," in field:
            result.extend(int(x) for x in field.split(","))
        
        return sorted(result)


# Register with NodeRegistry
try:
    from node_registry import NodeRegistry
    # Create registry instance and register the node
    registry = NodeRegistry()
    registry.register("start", StartNode)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register StartNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")
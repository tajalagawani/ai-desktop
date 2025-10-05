import logging
import subprocess
import asyncio
import time
import shlex
import os
import tempfile
import signal
import json
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor

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

class CommandExecutionError(Exception):
    """Custom exception for command execution errors."""
    pass

class CommandNode(BaseNode):
    """
    Node for executing system commands with comprehensive security controls,
    resource management, and error handling. Supports shell commands, scripts,
    and parameter substitution.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="CommandNode")
        self._setup_execution_environment()
        self._active_processes = set()
        
    def _setup_execution_environment(self):
        """Setup secure execution environment."""
        # Allowed commands for security (whitelist approach)
        self.allowed_commands = {
            # Development tools
            'coqc', 'coq', 'coqtop', 'coq_makefile',
            'gcc', 'g++', 'clang', 'make', 'cmake', 'ninja',
            'python', 'python3', 'pip', 'pip3',
            'node', 'npm', 'yarn', 'npx',
            'java', 'javac', 'mvn', 'gradle',
            'go', 'cargo', 'rustc',
            
            # System utilities
            'ls', 'cat', 'echo', 'pwd', 'which', 'whereis',
            'head', 'tail', 'grep', 'awk', 'sed', 'sort', 'uniq',
            'wc', 'find', 'xargs', 'cut', 'tr',
            
            # File operations (safe ones)
            'cp', 'mv', 'mkdir', 'touch', 'basename', 'dirname',
            
            # Archive tools
            'tar', 'zip', 'unzip', 'gzip', 'gunzip',
            
            # Text processing
            'diff', 'patch', 'file', 'stat',
            
            # Version control
            'git', 'svn', 'hg',
            
            # Package managers (read-only operations)
            'apt-cache', 'yum', 'dnf', 'pacman', 'brew',
        }
        
        # Forbidden commands for security
        self.forbidden_commands = {
            # System modification
            'rm', 'rmdir', 'sudo', 'su', 'chmod', 'chown', 'chgrp',
            'mount', 'umount', 'fdisk', 'mkfs', 'fsck',
            
            # Network operations
            'wget', 'curl', 'ssh', 'scp', 'rsync', 'nc', 'netcat',
            'telnet', 'ftp', 'sftp',
            
            # Process control
            'kill', 'killall', 'pkill', 'nohup', 'screen', 'tmux',
            
            # Package installation
            'apt-get', 'apt', 'yum install', 'dnf install', 'pip install',
            'npm install', 'yarn add',
            
            # System information that could leak sensitive data
            'ps', 'top', 'htop', 'lsof', 'netstat', 'ss',
            'env', 'printenv', 'set'
        }
        
        # Safe environment variables to preserve
        self.safe_env_vars = {
            'PATH', 'HOME', 'USER', 'LANG', 'LC_ALL', 'TZ',
            'PYTHONPATH', 'JAVA_HOME', 'NODE_PATH',
            'COQ_PATH', 'COQPATH'
        }
        
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the Command node."""
        return NodeSchema(
            node_type="command",
            version="1.0.0",
            description="Execute system commands with security controls and resource management. Supports parameter substitution and output capture.",
            parameters=[
                NodeParameter(
                    name="command",
                    type=NodeParameterType.STRING,
                    description="Command to execute with arguments. Supports template substitution.",
                    required=True
                ),
                NodeParameter(
                    name="shell",
                    type=NodeParameterType.BOOLEAN,
                    description="Execute command through shell (enables pipes, redirects, etc.)",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="working_directory",
                    type=NodeParameterType.STRING,
                    description="Working directory for command execution",
                    required=False,
                    default="."
                ),
                NodeParameter(
                    name="timeout",
                    type=NodeParameterType.NUMBER,
                    description="Execution timeout in seconds",
                    required=False,
                    default=60
                ),
                NodeParameter(
                    name="environment",
                    type=NodeParameterType.OBJECT,
                    description="Additional environment variables",
                    required=False,
                    default={}
                ),
                NodeParameter(
                    name="input_data",
                    type=NodeParameterType.STRING,
                    description="Data to send to stdin",
                    required=False,
                    default=""
                ),
                NodeParameter(
                    name="capture_output",
                    type=NodeParameterType.BOOLEAN,
                    description="Capture stdout and stderr",
                    required=False,
                    default=True
                ),
                NodeParameter(
                    name="abort_on_failure",
                    type=NodeParameterType.BOOLEAN,
                    description="Abort workflow if command returns non-zero exit code",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="allowed_exit_codes",
                    type=NodeParameterType.ARRAY,
                    description="List of exit codes considered successful",
                    required=False,
                    default=[0]
                ),
                NodeParameter(
                    name="security_mode",
                    type=NodeParameterType.STRING,
                    description="Security level: 'strict', 'moderate', 'permissive'",
                    required=False,
                    default="moderate"
                ),
                NodeParameter(
                    name="max_output_size",
                    type=NodeParameterType.NUMBER,
                    description="Maximum output size in bytes (0 = unlimited)",
                    required=False,
                    default=1048576  # 1MB default
                )
            ],
            
            # Define outputs for the node
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "stdout": NodeParameterType.STRING,
                "stderr": NodeParameterType.STRING,
                "exit_code": NodeParameterType.NUMBER,
                "execution_time": NodeParameterType.NUMBER,
                "command_info": NodeParameterType.OBJECT
            },
            
            # Add metadata
            tags=["command", "execution", "system", "shell", "secure"],
            author="System"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation for Command node."""
        params = node_data.get("params", {})
        command = params.get("command", "").strip()
        
        if not command:
            raise NodeValidationError("Command parameter is required and cannot be empty")
        
        # Validate timeout
        timeout = params.get("timeout", 60)
        if not isinstance(timeout, (int, float)) or timeout <= 0 or timeout > 3600:
            raise NodeValidationError("Timeout must be between 1 and 3600 seconds")
        
        # Validate security mode
        security_mode = params.get("security_mode", "moderate")
        if security_mode not in ["strict", "moderate", "permissive"]:
            raise NodeValidationError("Security mode must be 'strict', 'moderate', or 'permissive'")
        
        # Validate allowed exit codes
        allowed_codes = params.get("allowed_exit_codes", [0])
        if not isinstance(allowed_codes, list) or not all(isinstance(code, int) for code in allowed_codes):
            raise NodeValidationError("Allowed exit codes must be a list of integers")
        
        # Security validation based on mode
        if security_mode in ["strict", "moderate"]:
            self._validate_command_security(command, security_mode)
        
        # Validate working directory
        working_dir = params.get("working_directory", ".")
        if working_dir and not isinstance(working_dir, str):
            raise NodeValidationError("Working directory must be a string")
        
        return {}
    
    def _validate_command_security(self, command: str, security_mode: str) -> None:
        """Validate command for security issues."""
        # Parse command to get the base command
        try:
            if command.strip().startswith('sudo ') or command.strip().startswith('su '):
                raise NodeValidationError("Privilege escalation commands not allowed")
            
            # Extract base command (first word after shell operators)
            base_cmd = self._extract_base_command(command)
            
            # Check against forbidden commands
            if base_cmd in self.forbidden_commands:
                raise NodeValidationError(f"Forbidden command: {base_cmd}")
            
            # In strict mode, only allow whitelisted commands
            if security_mode == "strict" and base_cmd not in self.allowed_commands:
                raise NodeValidationError(f"Command not in whitelist: {base_cmd}")
            
            # Check for dangerous patterns
            dangerous_patterns = [
                '&&', '||', ';',  # Command chaining
                '>', '>>', '<',   # Redirects (in strict mode)
                '|',              # Pipes (in strict mode)
                '`', '$(',        # Command substitution
                'rm -rf', 'rm -r',  # Dangerous file operations
                '/etc/', '/proc/', '/sys/',  # System directories
            ]
            
            if security_mode == "strict":
                for pattern in dangerous_patterns:
                    if pattern in command:
                        raise NodeValidationError(f"Potentially dangerous pattern detected: {pattern}")
        
        except Exception as e:
            if isinstance(e, NodeValidationError):
                raise
            raise NodeValidationError(f"Command validation error: {str(e)}")
    
    def _extract_base_command(self, command: str) -> str:
        """Extract the base command from a command string."""
        try:
            # Handle shell operators and extract first command
            command = command.strip()
            
            # Split by common shell operators
            for operator in ['&&', '||', ';', '|']:
                if operator in command:
                    command = command.split(operator)[0].strip()
            
            # Parse with shlex to handle quotes properly
            parts = shlex.split(command)
            if parts:
                return os.path.basename(parts[0])
            return ""
        except:
            # Fallback to simple parsing
            return command.split()[0] if command.split() else ""
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Command node."""
        start_time = time.time()
        
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            
            # Extract parameters
            command = validated_data.get("command", "")
            shell = validated_data.get("shell", False)
            working_directory = validated_data.get("working_directory", ".")
            timeout = validated_data.get("timeout", 60)
            environment = validated_data.get("environment", {})
            input_data = validated_data.get("input_data", "")
            capture_output = validated_data.get("capture_output", True)
            abort_on_failure = validated_data.get("abort_on_failure", False)
            allowed_exit_codes = validated_data.get("allowed_exit_codes", [0])
            security_mode = validated_data.get("security_mode", "moderate")
            max_output_size = validated_data.get("max_output_size", 1048576)
            
            # Prepare environment
            exec_env = self._prepare_environment(environment)
            
            # Resolve working directory
            work_dir = self._resolve_working_directory(working_directory)
            
            # Execute command
            result = await self._execute_command(
                command=command,
                shell=shell,
                working_directory=work_dir,
                timeout=timeout,
                environment=exec_env,
                input_data=input_data,
                capture_output=capture_output,
                max_output_size=max_output_size
            )
            
            # Check exit code
            exit_code = result.get("exit_code", 1)
            if exit_code not in allowed_exit_codes:
                result["status"] = "error"
                if not result.get("error"):
                    result["error"] = f"Command failed with exit code {exit_code}"
                
                if abort_on_failure:
                    raise CommandExecutionError(f"Command failed with exit code {exit_code} (abort_on_failure=true)")
            
            # Add execution metadata
            execution_time = time.time() - start_time
            result["execution_time"] = execution_time
            result["command_info"] = {
                "original_command": command,
                "shell": shell,
                "working_directory": work_dir,
                "security_mode": security_mode,
                "timeout": timeout
            }
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_message = f"CommandNode execution error: {str(e)}"
            logger.error(f"{error_message}")
            
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "stdout": "",
                "stderr": str(e),
                "exit_code": 1,
                "execution_time": execution_time,
                "command_info": {
                    "original_command": command if 'command' in locals() else "unknown",
                    "error": "Failed to execute command"
                }
            }
    
    def _prepare_environment(self, additional_env: Dict[str, str]) -> Dict[str, str]:
        """Prepare execution environment with security filtering."""
        # Start with safe environment variables
        env = {}
        
        # Copy safe environment variables from current environment
        for var in self.safe_env_vars:
            if var in os.environ:
                env[var] = os.environ[var]
        
        # Add additional environment variables (with validation)
        for key, value in additional_env.items():
            if isinstance(key, str) and isinstance(value, str):
                # Avoid dangerous environment variables
                if not key.startswith('_') and key not in ['IFS', 'PS1', 'PS2']:
                    env[key] = value
        
        return env
    
    def _resolve_working_directory(self, working_directory: str) -> str:
        """Resolve and validate working directory."""
        try:
            # Get actfile directory if available
            actfile_dir = getattr(self, '_actfile_dir', None)
            
            if working_directory == "." and actfile_dir:
                return str(actfile_dir)
            elif os.path.isabs(working_directory):
                return working_directory
            elif actfile_dir:
                return str(actfile_dir / working_directory)
            else:
                return os.path.abspath(working_directory)
        except Exception:
            return os.getcwd()
    
    async def _execute_command(
        self,
        command: str,
        shell: bool,
        working_directory: str,
        timeout: float,
        environment: Dict[str, str],
        input_data: str,
        capture_output: bool,
        max_output_size: int
    ) -> Dict[str, Any]:
        """Execute the command in a subprocess."""
        
        try:
            # Prepare command
            if shell:
                cmd = command
                cmd_args = command
            else:
                cmd_args = shlex.split(command)
                cmd = cmd_args
            
            # Create subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd_args if not shell else ['/bin/sh', '-c', command],
                stdout=subprocess.PIPE if capture_output else None,
                stderr=subprocess.PIPE if capture_output else None,
                stdin=subprocess.PIPE if input_data else None,
                cwd=working_directory,
                env=environment
            )
            
            # Track the process for cleanup
            self._active_processes.add(process)
            
            try:
                # Send input data and wait for completion
                if input_data:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(input_data.encode('utf-8')),
                        timeout=timeout
                    )
                else:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(),
                        timeout=timeout
                    )
                
            except asyncio.TimeoutError:
                # Kill process on timeout
                try:
                    if process.returncode is None:
                        process.kill()
                        await asyncio.wait_for(process.wait(), timeout=5)
                except:
                    pass
                
                return {
                    "status": "error",
                    "result": None,
                    "error": "Process timeout",
                    "stdout": "",
                    "stderr": f"Process timed out after {timeout} seconds",
                    "exit_code": 124
                }
            finally:
                # Remove from tracking
                self._active_processes.discard(process)
            
            # Decode and limit output
            stdout_str = ""
            stderr_str = ""
            
            if capture_output:
                if stdout:
                    stdout_str = stdout.decode('utf-8', errors='replace')
                    if max_output_size > 0 and len(stdout_str) > max_output_size:
                        stdout_str = stdout_str[:max_output_size] + "\n... (output truncated)"
                
                if stderr:
                    stderr_str = stderr.decode('utf-8', errors='replace')
                    if max_output_size > 0 and len(stderr_str) > max_output_size:
                        stderr_str = stderr_str[:max_output_size] + "\n... (output truncated)"
            
            # Determine status
            status = "success" if process.returncode == 0 else "error"
            
            return {
                "status": status,
                "result": stdout_str if capture_output else None,
                "error": stderr_str if process.returncode != 0 and capture_output else None,
                "stdout": stdout_str,
                "stderr": stderr_str,
                "exit_code": process.returncode
            }
            
        except Exception as e:
            return {
                "status": "error",
                "result": None,
                "error": str(e),
                "stdout": "",
                "stderr": f"Command execution error: {str(e)}",
                "exit_code": 1
            }
    
    def set_actfile_directory(self, actfile_dir: Path):
        """Set the Actfile directory for resolving relative paths."""
        self._actfile_dir = actfile_dir
        logger.debug(f"CommandNode actfile directory set to: {actfile_dir}")
    
    def cleanup(self):
        """Clean up active processes and resources."""
        # Kill any active processes
        for process in list(self._active_processes):
            try:
                if process.returncode is None:
                    process.kill()
            except:
                pass
        
        self._active_processes.clear()
        
        # Shutdown executor
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
    
    def __del__(self):
        """Cleanup on destruction."""
        self.cleanup()

# Register with NodeRegistry
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
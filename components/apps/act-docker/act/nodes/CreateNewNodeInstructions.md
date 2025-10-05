# Complete Instructions for Creating New ACT Workflow Nodes

## Overview
This document provides comprehensive instructions for creating new nodes for the ACT workflow system, following the established patterns and ensuring full API coverage with complete testing.

## Node Creation Pipeline

### Step 1: Research Latest API Documentation
- **Objective**: Research the latest API documentation for the service
- **Actions**:
  - Use WebSearch to find official API documentation
  - Focus on finding ALL available operations, not just popular ones
  - Look for recent updates, new endpoints, and deprecated features
  - Document all available endpoints, parameters, and response formats
  - Check for rate limits, authentication methods, and error codes

### Step 2: Create Node Structure
Follow the exact pattern established in existing nodes like `StripeNode.py`, `EmailNode.py`, and `NotionNode.py`.

#### 2.1 Required Imports
```python
"""
[ServiceName] Node - Comprehensive [service description] integration
Supports all major [service] operations including [list key operations].
Uses [service] Python SDK with full API coverage.
"""

import logging
import asyncio
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone
# Import service-specific SDK
import [service_sdk]

try:
    from base_node import (
        BaseNode, NodeSchema, NodeParameter, NodeParameterType,
        NodeValidationError, NodeExecutionError
    )
except ImportError:
    try:
        from .base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError, NodeExecutionError
        )
    except ImportError:
        from src.act_workflow.nodes.base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError, NodeExecutionError
        )

# Configure logging
logger = logging.getLogger(__name__)
```

#### 2.2 Operations Class
Create a comprehensive operations class with ALL available operations:

```python
class [ServiceName]Operation:
    """All available [service] operations."""
    
    # Group operations by category
    # Example categories: CRUD operations, Management operations, etc.
    OPERATION_NAME = "operation_name"
    # ... include ALL operations from API documentation
```

#### 2.3 Node Class Structure
```python
class [ServiceName]Node(BaseNode):
    """
    Comprehensive [service] integration node supporting all major API operations.
    Handles [list key functionalities].
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        # Initialize service client if needed
        
    def get_schema(self) -> NodeSchema:
        """Return the comprehensive schema for the [service] node."""
        # Define ALL parameters for ALL operations
        # Include detailed descriptions and proper types
        # Set proper required/optional flags
        
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate [service]-specific parameters."""
        # Validate ALL operation-specific requirements
        # Include proper error messages
        
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the [service] operation."""
        # Route to appropriate operation handlers
        # Include comprehensive error handling
```

### Step 3: Schema Definition Requirements

#### 3.1 Complete Parameter Coverage
- **Include ALL parameters** for ALL operations
- **Use proper parameter types**: STRING, NUMBER, BOOLEAN, ARRAY, OBJECT, SECRET, ANY
- **Set correct required/optional flags**
- **Include detailed descriptions** for each parameter
- **Add enum values** where applicable
- **Set default values** where appropriate
- **Include min/max values** for numeric parameters

#### 3.2 Output Schema
Define all possible output types:
```python
outputs={
    "status": NodeParameterType.STRING,
    "object": NodeParameterType.OBJECT,
    "objects": NodeParameterType.ARRAY,
    "id": NodeParameterType.STRING,
    "error": NodeParameterType.STRING,
    "count": NodeParameterType.NUMBER,
    "has_more": NodeParameterType.BOOLEAN,
    # ... include ALL possible outputs
}
```

### Step 4: Validation Implementation

#### 4.1 Common Validations
```python
def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
    params = node_data.get("params", {})
    operation = params.get("operation")
    
    # Always validate operation exists
    if not operation:
        raise NodeValidationError("Operation is required")
    
    # Always validate API credentials
    if not params.get("api_key"):  # or token, etc.
        raise NodeValidationError("[Service] API key is required")
    
    # Add service-specific credential validation
    # Validate credential format if applicable
```

#### 4.2 Operation-Specific Validations
For each operation, validate:
- **Required parameters are present**
- **Parameter formats are correct**
- **Parameter combinations are valid**
- **Parameter values are within acceptable ranges**

### Step 5: Operation Implementation

#### 5.1 Implementation Pattern
```python
async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        # Initialize service client
        # Set authentication
        # Set request options
        
        # Route to specific operation handler
        if operation == [ServiceName]Operation.OPERATION_NAME:
            return await self._operation_handler(params, request_options)
        # ... route ALL operations
        
    except [ServiceError] as e:
        # Handle service-specific errors
        return self._format_error_response(e)
    except Exception as e:
        # Handle generic errors
        return self._format_generic_error(e)
```

#### 5.2 Operation Handler Pattern
```python
async def _operation_handler(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
    """Handle specific operation."""
    try:
        # Extract parameters
        operation_params = {}
        
        # Add required parameters
        operation_params["required_param"] = params.get("required_param")
        
        # Add optional parameters
        optional_params = ["param1", "param2", "param3"]
        for param in optional_params:
            if params.get(param) is not None:
                operation_params[param] = params.get(param)
        
        # Call service API
        result = service_client.operation_method(**operation_params, **request_options)
        
        # Format response
        return {
            "status": "success",
            "object": result.to_dict() if hasattr(result, 'to_dict') else result,
            "id": result.id if hasattr(result, 'id') else None,
            "type": "object_type"
        }
        
    except Exception as e:
        raise e
```

### Step 6: Helper Functions

#### 6.1 Create Helper Class
```python
class [ServiceName]Helpers:
    """Helper functions for [service] operations."""
    
    @staticmethod
    def format_response(data: Any) -> Dict[str, Any]:
        """Format service response for consistency."""
        
    @staticmethod
    def validate_parameter(param: str, value: Any) -> bool:
        """Validate parameter format."""
        
    @staticmethod
    def construct_request_data(params: Dict[str, Any]) -> Dict[str, Any]:
        """Construct request data from parameters."""
        
    # Add service-specific helper methods
```

### Step 7: Comprehensive Testing

#### 7.1 Test File Structure
Create `test_[service_name]_node.py` with the following structure:

```python
"""
Comprehensive Test Suite for [Service] Node
Tests all operations, error handling, and edge cases for the [ServiceName]Node.
"""

import asyncio
import json
import logging
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from typing import Dict, Any, List

# Import the Node and related classes
from [ServiceName]Node import [ServiceName]Node, [ServiceName]Operation, [ServiceName]Helpers
try:
    from base_node import NodeValidationError
except ImportError:
    try:
        from .base_node import NodeValidationError
    except ImportError:
        from src.act_workflow.nodes.base_node import NodeValidationError

import [service_sdk]

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Test[ServiceName]Node:
    """Test suite for [ServiceName]Node functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.node = [ServiceName]Node()
        # Define test constants
        
    def test_get_schema(self):
        """Test that the schema is properly defined."""
        # Test schema validation
        
    def test_validate_custom_missing_operation(self):
        """Test validation when operation is missing."""
        # Test missing operation
        
    def test_validate_custom_missing_credentials(self):
        """Test validation when credentials are missing."""
        # Test missing credentials
        
    # Add tests for EVERY operation
    @patch('[service_sdk].[method]')
    async def test_operation_name(self, mock_method):
        """Test specific operation."""
        # Test each operation with mocked responses
        
    # Add error handling tests
    async def test_service_error_handling(self):
        """Test handling of service errors."""
        # Test service-specific errors
        
    async def test_unknown_operation(self):
        """Test handling of unknown operation."""
        # Test unknown operation handling

class Test[ServiceName]Helpers:
    """Test suite for [ServiceName]Helpers utility functions."""
    
    # Test all helper functions
    
class Test[ServiceName]Integration:
    """Integration tests for [ServiceName]Node (requires actual API key)."""
    
    @pytest.fixture
    def api_key(self):
        """Get API key from environment."""
        # Get API key from environment
        
    # Add integration tests

class Test[ServiceName]Performance:
    """Performance tests for [ServiceName]Node."""
    
    # Add performance tests

class Test[ServiceName]ErrorHandling:
    """Test error handling scenarios."""
    
    # Add comprehensive error handling tests

# Run tests
if __name__ == "__main__":
    # Add test runner
```

#### 7.2 Test Coverage Requirements
- **Schema validation tests**: Test schema definition and parameter validation
- **Parameter validation tests**: Test all validation scenarios for each operation
- **Operation tests**: Test each operation with mocked responses
- **Error handling tests**: Test service errors, network errors, rate limits
- **Helper function tests**: Test all utility functions
- **Integration tests**: Test with real API (optional, requires credentials)
- **Performance tests**: Test concurrent operations
- **Edge case tests**: Test boundary conditions and error scenarios

#### 7.3 Test Execution
Tests must:
- **Run successfully** without failures
- **Cover all operations** defined in the node
- **Handle all error scenarios**
- **Validate all parameters** properly
- **Test all helper functions**

### Step 8: Documentation Requirements

#### 8.1 Code Documentation
- **Comprehensive docstrings** for all classes and methods
- **Parameter descriptions** for all functions
- **Return value descriptions** for all functions
- **Error descriptions** for all exception scenarios
- **Usage examples** in docstrings

#### 8.2 API Coverage Documentation
- **List all supported operations** in the node docstring
- **Document parameter requirements** for each operation
- **Include service-specific notes** and limitations
- **Reference official API documentation**

### Step 9: Quality Assurance

#### 9.1 Code Quality Checks
- **No unused imports** or variables
- **Consistent naming conventions**
- **Proper error handling** throughout
- **Async/await patterns** used correctly
- **Type hints** provided where appropriate

#### 9.2 Testing Requirements
- **All tests must pass** before submission
- **Test coverage** should be comprehensive
- **Mock all external API calls** in unit tests
- **Include integration tests** for real API validation
- **Test error scenarios** thoroughly

### Step 10: File Organization

#### 10.1 Required Files
1. **`[ServiceName]Node.py`** - Main node implementation
2. **`test_[service_name]_node.py`** - Comprehensive test suite

#### 10.2 File Placement
- Place files in: `/Users/tajnoah/newact/act_workflow/src 00-01-14-161/act_workflow/nodes/`
- Follow existing naming conventions
- Ensure proper import paths

## Example Implementation Checklist

### Before Starting:
- [ ] Research latest API documentation thoroughly
- [ ] Document all available operations
- [ ] Check for authentication requirements
- [ ] Identify required Python SDK/library

### During Implementation:
- [ ] Follow exact structure from existing nodes
- [ ] Include ALL operations from API documentation
- [ ] Implement comprehensive parameter validation
- [ ] Add proper error handling for all scenarios
- [ ] Create helper functions for common operations
- [ ] Write comprehensive test suite
- [ ] Test all operations with mocked responses
- [ ] Validate all error handling scenarios

### Before Completion:
- [ ] Run all tests and ensure they pass
- [ ] Verify code quality and documentation
- [ ] Check for unused imports/variables
- [ ] Validate parameter types and descriptions
- [ ] Test integration with real API (if possible)
- [ ] Review code for consistency with existing nodes

## Key Principles

1. **Complete API Coverage**: Include ALL operations, not just popular ones
2. **Comprehensive Testing**: Test every operation and error scenario
3. **Proper Validation**: Validate all parameters thoroughly
4. **Error Handling**: Handle all possible error scenarios gracefully
5. **Documentation**: Provide comprehensive documentation and examples
6. **Consistency**: Follow established patterns from existing nodes
7. **Quality**: Ensure high code quality and maintainability

## Common Pitfalls to Avoid

1. **Missing Operations**: Don't skip any API operations
2. **Inadequate Validation**: Don't skip parameter validation
3. **Poor Error Handling**: Don't ignore error scenarios
4. **Insufficient Testing**: Don't skip test cases
5. **Inconsistent Patterns**: Don't deviate from established patterns
6. **Missing Documentation**: Don't skip docstrings and comments
7. **Import Issues**: Don't forget proper import handling

## Success Criteria

A node is considered complete when:
- [ ] All API operations are implemented
- [ ] All tests pass successfully
- [ ] Parameter validation is comprehensive
- [ ] Error handling covers all scenarios
- [ ] Helper functions are tested
- [ ] Code follows established patterns
- [ ] Documentation is comprehensive
- [ ] Integration tests work (if applicable)

This document should be referenced for every new node creation to ensure consistency and completeness.
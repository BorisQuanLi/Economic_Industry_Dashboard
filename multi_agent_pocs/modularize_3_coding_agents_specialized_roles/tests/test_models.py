"""
Unit tests for the core data models in the Multi-Agent Orchestrator system.
"""

import pytest
from pydantic import ValidationError

# Since tests are run from the root, we can import from the package
from multi_agent_poc.models import (
    AgentType,
    AgentTask,
    AgentResult,
    WorkflowStatus,
    User
)

def test_agent_type_enum():
    """Tests that AgentType enum members are accessible."""
    assert AgentType.GEMINI.value == "gemini"
    assert AgentType.MISTRAL_VIBE.value == "mistral_vibe"
    assert AgentType.AMAZON_Q.value == "amazon_q"

def test_agent_task_instantiation():
    """Tests the creation of an AgentTask dataclass."""
    task = AgentTask(
        task_id="test_task_123",
        agent_type=AgentType.GEMINI,
        task_type="generate",
        input_data="Create a hello world function.",
        output_file="hello.py",
        dependencies=["setup_task"]
    )
    assert task.task_id == "test_task_123"
    assert task.agent_type == AgentType.GEMINI
    assert task.input_data == "Create a hello world function."
    assert task.dependencies == ["setup_task"]

def test_agent_result_instantiation():
    """Tests the creation of an AgentResult dataclass."""
    result = AgentResult(
        task_id="test_task_123",
        agent_type=AgentType.GEMINI,
        success=True,
        output="def hello(): return 'world'",
        execution_time=1.23
    )
    assert result.success is True
    assert result.agent_type == AgentType.GEMINI
    assert result.execution_time == 1.23
    assert "hello" in result.output

def test_workflow_status_enum():
    """Tests that WorkflowStatus enum members are accessible."""
    assert WorkflowStatus.RUNNING.value == "running"
    assert WorkflowStatus.COMPLETED.value == "completed"

def test_user_model_valid():
    """Tests successful creation of the User Pydantic model."""
    user = User(
        name="John Doe",
        email="john.doe@example.com",
        user_id=101
    )
    assert user.name == "John Doe"
    assert user.email == "john.doe@example.com"
    assert user.user_id == 101

def test_user_model_invalid_email():
    """Tests that Pydantic raises a ValidationError for an invalid email."""
    with pytest.raises(ValidationError):
        User(
            name="Jane Doe",
            email="not-an-email",
            user_id=102
        )

def test_user_model_invalid_type():
    """Tests that Pydantic raises a ValidationError for a wrong data type."""
    with pytest.raises(ValidationError):
        User(
            name="Jane Doe",
            email="jane.doe@example.com",
            user_id="not-an-integer"
        )


def test_agent_task_minimal():
    """Tests AgentTask creation with only required fields."""
    task = AgentTask(
        task_id="minimal_task",
        agent_type=AgentType.GEMINI,
        task_type="generate",
        input_data="test input"
    )
    assert task.task_id == "minimal_task"
    assert task.agent_type == AgentType.GEMINI
    assert task.output_file is None
    assert task.dependencies is None


def test_agent_task_empty_dependencies():
    """Tests AgentTask with empty dependencies list."""
    task = AgentTask(
        task_id="no_deps_task",
        agent_type=AgentType.MISTRAL_VIBE,
        task_type="validate",
        input_data="test input",
        dependencies=[]
    )
    assert task.dependencies == []


def test_agent_task_complex_dependencies():
    """Tests AgentTask with multiple dependencies."""
    task = AgentTask(
        task_id="complex_task",
        agent_type=AgentType.AMAZON_Q,
        task_type="documentation",
        input_data="test input",
        dependencies=["task1", "task2", "task3"]
    )
    assert len(task.dependencies) == 3
    assert "task1" in task.dependencies
    assert "task2" in task.dependencies
    assert "task3" in task.dependencies


def test_agent_result_with_error():
    """Tests AgentResult creation with error information."""
    result = AgentResult(
        task_id="failed_task",
        agent_type=AgentType.GEMINI,
        success=False,
        output="",
        error="Execution failed due to timeout",
        execution_time=5.67
    )
    assert result.success is False
    assert result.error == "Execution failed due to timeout"
    assert result.output == ""


def test_agent_result_minimal():
    """Tests AgentResult creation with minimal fields."""
    result = AgentResult(
        task_id="simple_task",
        agent_type=AgentType.MISTRAL_VIBE,
        success=True,
        output="test output"
    )
    assert result.success is True
    assert result.error is None
    assert result.execution_time == 0.0


def test_workflow_status_transitions():
    """Tests all WorkflowStatus enum values."""
    statuses = [
        WorkflowStatus.PENDING,
        WorkflowStatus.RUNNING,
        WorkflowStatus.COMPLETED,
        WorkflowStatus.FAILED
    ]
    
    expected_values = ["pending", "running", "completed", "failed"]
    
    for status, expected_value in zip(statuses, expected_values):
        assert status.value == expected_value


def test_user_model_edge_cases():
    """Tests User model with edge case values."""
    # Test with maximum reasonable values
    user = User(
        name="A" * 100,  # Long name
        email="a@b.co",  # Short but valid email
        user_id=999999999  # Large user ID
    )
    assert len(user.name) == 100
    assert user.email == "a@b.co"
    assert user.user_id == 999999999


def test_user_model_unicode():
    """Tests User model with Unicode characters."""
    user = User(
        name="José María",
        email="josé.maría@example.com",
        user_id=103
    )
    assert "José" in user.name
    assert "maría" in user.email


def test_agent_task_special_characters():
    """Tests AgentTask with special characters in input data."""
    special_input = """
    def hello_world():
        '''Function with docstring'''
        print("Hello, 世界!")
        return {"status": "success", "data": [1, 2, 3]}
    """
    
    task = AgentTask(
        task_id="special_chars_task",
        agent_type=AgentType.GEMINI,
        task_type="refactor",
        input_data=special_input,
        output_file="special.py"
    )
    
    assert "世界" in task.input_data
    assert "docstring" in task.input_data
    assert "Hello" in task.input_data


def test_agent_result_large_output():
    """Tests AgentResult with large output data."""
    large_output = "x" * 10000  # 10KB of data
    
    result = AgentResult(
        task_id="large_output_task",
        agent_type=AgentType.AMAZON_Q,
        success=True,
        output=large_output,
        execution_time=2.5
    )
    
    assert len(result.output) == 10000
    assert result.execution_time == 2.5


def test_agent_task_json_serialization():
    """Tests that AgentTask can be serialized to JSON-like dict."""
    task = AgentTask(
        task_id="json_test",
        agent_type=AgentType.GEMINI,
        task_type="generate",
        input_data="test",
        output_file="test.py",
        dependencies=["dep1"]
    )
    
    # Convert to dict (dataclass asdict)
    task_dict = {
        "task_id": task.task_id,
        "agent_type": task.agent_type.value,
        "task_type": task.task_type,
        "input_data": task.input_data,
        "output_file": task.output_file,
        "dependencies": task.dependencies
    }
    
    assert task_dict["task_id"] == "json_test"
    assert task_dict["agent_type"] == "gemini"
    assert task_dict["dependencies"] == ["dep1"]


def test_agent_result_json_serialization():
    """Tests that AgentResult can be serialized to JSON-like dict."""
    result = AgentResult(
        task_id="json_result_test",
        agent_type=AgentType.MISTRAL_VIBE,
        success=True,
        output="test output",
        error="test error",
        execution_time=1.23
    )
    
    # Convert to dict
    result_dict = {
        "task_id": result.task_id,
        "agent_type": result.agent_type.value,
        "success": result.success,
        "output": result.output,
        "error": result.error,
        "execution_time": result.execution_time
    }
    
    assert result_dict["success"] is True
    assert result_dict["agent_type"] == "mistral_vibe"
    assert result_dict["execution_time"] == 1.23


def test_workflow_status_enum_iteration():
    """Tests iteration over WorkflowStatus enum."""
    status_values = []
    for status in WorkflowStatus:
        status_values.append(status.value)
    
    expected = ["pending", "running", "completed", "failed"]
    assert status_values == expected


def test_agent_type_enum_iteration():
    """Tests iteration over AgentType enum."""
    agent_values = []
    for agent in AgentType:
        agent_values.append(agent.value)
    
    expected = ["gemini", "mistral_vibe", "amazon_q"]
    assert agent_values == expected


def test_user_model_optional_fields():
    """Tests that User model handles all field combinations."""
    # All fields provided
    user1 = User(
        name="Complete User",
        email="complete@example.com",
        user_id=1
    )
    assert user1.name == "Complete User"
    
    # Test that all fields are required (Pydantic should enforce this)
    with pytest.raises(ValidationError):
        User(name="Incomplete")  # Missing email and user_id
    
    with pytest.raises(ValidationError):
        User(email="test@example.com")  # Missing name and user_id

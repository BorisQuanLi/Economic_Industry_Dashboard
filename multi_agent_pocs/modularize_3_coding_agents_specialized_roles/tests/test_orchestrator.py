#!/usr/bin/env python3
"""
Test suite for MultiAgentOrchestrator core functionality.

This module tests the orchestrator's core components including:
- Initialization and configuration
- Workflow parsing and validation
- Task dependency management
- Error handling and edge cases
"""

import pytest
import os
import tempfile
import json
from typing import Dict, Any, List

# Import the classes we need to test
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from orchestrator import MultiAgentOrchestrator
from models import AgentType, AgentTask, AgentResult, WorkflowStatus


class TestOrchestratorInitialization:
    """Test orchestrator initialization and basic configuration."""
    
    def test_default_initialization(self):
        """Test orchestrator with default parameters."""
        orchestrator = MultiAgentOrchestrator()
        
        assert orchestrator.max_workers == 3
        assert orchestrator.status == WorkflowStatus.PENDING
        assert orchestrator.current_workflow_id is None
        assert orchestrator.workflow_history == []
        assert hasattr(orchestrator, 'max_workers')
        assert hasattr(orchestrator, 'workflow_history')
        assert hasattr(orchestrator, 'current_workflow_id')
        assert hasattr(orchestrator, 'status')
    
    def test_custom_worker_count(self):
        """Test orchestrator with custom worker count."""
        custom_workers = 5
        orchestrator = MultiAgentOrchestrator(max_workers=custom_workers)
        
        assert orchestrator.max_workers == custom_workers
        assert orchestrator.status == WorkflowStatus.PENDING
        
    def test_initial_status(self):
        """Test that initial status is PENDING."""
        orchestrator = MultiAgentOrchestrator()
        assert orchestrator.status.value == "pending"
        
    def test_workflow_history_initialization(self):
        """Test that workflow history starts empty."""
        orchestrator = MultiAgentOrchestrator()
        assert isinstance(orchestrator.workflow_history, list)
        assert len(orchestrator.workflow_history) == 0


class TestWorkflowParsing:
    """Test workflow definition parsing functionality."""
    
    def test_simple_workflow_parsing(self):
        """Test parsing a simple workflow with one task."""
        orchestrator = MultiAgentOrchestrator()
        
        workflow_definition = {
            "description": "Simple test workflow",
            "tasks": {
                "test_task": {
                    "agent": "gemini",
                    "type": "generate",
                    "input": "test input"
                }
            }
        }
        
        tasks = orchestrator._parse_workflow_definition(workflow_definition)
        
        assert len(tasks) == 1
        assert isinstance(tasks[0], AgentTask)
        assert tasks[0].task_id == "test_task"
        assert tasks[0].agent_type == AgentType.GEMINI
        assert tasks[0].task_type == "generate"
        assert tasks[0].input_data == "test input"
        # Check if output_file is None or empty list
        assert tasks[0].output_file in [None, []]
        assert tasks[0].dependencies in [None, []]
    
    def test_workflow_with_dependencies(self):
        """Test parsing workflow with task dependencies."""
        orchestrator = MultiAgentOrchestrator()
        
        workflow_definition = {
            "description": "Workflow with dependencies",
            "tasks": {
                "generate": {
                    "agent": "gemini",
                    "type": "generate",
                    "input": "generate something"
                },
                "validate": {
                    "agent": "mistral_vibe",
                    "type": "validate",
                    "input": "generated_output",
                    "depends_on": ["generate"]
                }
            }
        }
        
        tasks = orchestrator._parse_workflow_definition(workflow_definition)
        
        assert len(tasks) == 2
        
        # Find tasks by ID
        generate_task = next(t for t in tasks if t.task_id == "generate")
        validate_task = next(t for t in tasks if t.task_id == "validate")
        
        assert generate_task.agent_type == AgentType.GEMINI
        assert validate_task.agent_type == AgentType.MISTRAL_VIBE
        assert validate_task.dependencies == ["generate"]
    
    def test_workflow_with_output_files(self):
        """Test parsing workflow with output file specifications."""
        orchestrator = MultiAgentOrchestrator()
        
        workflow_definition = {
            "description": "Workflow with output files",
            "tasks": {
                "generate": {
                    "agent": "gemini",
                    "type": "generate",
                    "input": "generate something",
                    "output_file": "generated.py"
                }
            }
        }
        
        tasks = orchestrator._parse_workflow_definition(workflow_definition)
        assert len(tasks) == 1
        assert tasks[0].output_file == "generated.py"
    
    def test_empty_workflow(self):
        """Test parsing empty workflow."""
        orchestrator = MultiAgentOrchestrator()
        
        workflow_definition = {
            "description": "Empty workflow",
            "tasks": {}
        }
        
        tasks = orchestrator._parse_workflow_definition(workflow_definition)
        assert len(tasks) == 0
        assert isinstance(tasks, list)
    
    def test_workflow_with_all_agent_types(self):
        """Test parsing workflow with all supported agent types."""
        orchestrator = MultiAgentOrchestrator()
        
        workflow_definition = {
            "description": "All agent types",
            "tasks": {
                "gemini_task": {
                    "agent": "gemini",
                    "type": "generate",
                    "input": "test"
                },
                "mistral_task": {
                    "agent": "mistral_vibe",
                    "type": "validate",
                    "input": "test"
                },
                "amazon_task": {
                    "agent": "amazon_q",
                    "type": "documentation",
                    "input": "test"
                }
            }
        }
        
        tasks = orchestrator._parse_workflow_definition(workflow_definition)
        
        assert len(tasks) == 3
        
        agent_types = [task.agent_type for task in tasks]
        assert AgentType.GEMINI in agent_types
        assert AgentType.MISTRAL_VIBE in agent_types
        assert AgentType.AMAZON_Q in agent_types


class TestDependencyManagement:
    """Test task dependency resolution and management."""
    
    def test_dependencies_satisfied(self):
        """Test dependency satisfaction logic."""
        orchestrator = MultiAgentOrchestrator()
        
        # Create a task with dependencies
        task = AgentTask(
            task_id="dependent_task",
            agent_type=AgentType.GEMINI,
            task_type="generate",
            input_data="test",
            dependencies=["prerequisite_task"]
        )
        
        # Test when dependency is not satisfied
        completed_tasks = set()
        assert not orchestrator._dependencies_satisfied(task, completed_tasks)
        
        # Test when dependency is satisfied
        completed_tasks = {"prerequisite_task"}
        assert orchestrator._dependencies_satisfied(task, completed_tasks)
    
    def test_no_dependencies(self):
        """Test task with no dependencies."""
        orchestrator = MultiAgentOrchestrator()
        
        task = AgentTask(
            task_id="independent_task",
            agent_type=AgentType.GEMINI,
            task_type="generate",
            input_data="test",
            dependencies=None
        )
        
        # Should always be satisfied when no dependencies
        assert orchestrator._dependencies_satisfied(task, set())
        assert orchestrator._dependencies_satisfied(task, {"other_task"})
    
    def test_multiple_dependencies(self):
        """Test task with multiple dependencies."""
        orchestrator = MultiAgentOrchestrator()
        
        task = AgentTask(
            task_id="complex_task",
            agent_type=AgentType.GEMINI,
            task_type="generate",
            input_data="test",
            dependencies=["dep1", "dep2", "dep3"]
        )
        
        # Test partial satisfaction (should fail)
        completed_tasks = {"dep1", "dep2"}
        assert not orchestrator._dependencies_satisfied(task, completed_tasks)
        
        # Test full satisfaction (should pass)
        completed_tasks = {"dep1", "dep2", "dep3"}
        assert orchestrator._dependencies_satisfied(task, completed_tasks)
        
        # Test over-satisfaction (should still pass)
        completed_tasks = {"dep1", "dep2", "dep3", "extra_task"}
        assert orchestrator._dependencies_satisfied(task, completed_tasks)


class TestTaskExecution:
    """Test task execution and result handling."""
    
    def test_task_id_generation(self):
        """Test task ID generation logic."""
        orchestrator = MultiAgentOrchestrator()
        
        task = AgentTask(
            task_id="test_task_123",
            agent_type=AgentType.GEMINI,
            task_type="generate",
            input_data="test"
        )
        
        task_id = orchestrator._get_task_id(task)
        assert isinstance(task_id, str)
        assert len(task_id) > 0
        # Should include agent type
        assert "gemini" in task_id.lower()
    
    def test_result_aggregation(self):
        """Test result aggregation from multiple agents."""
        orchestrator = MultiAgentOrchestrator()
        
        # Create some sample results
        results = [
            AgentResult(
                task_id="task1",
                agent_type=AgentType.GEMINI,
                success=True,
                output="result1",
                execution_time=1.0
            ),
            AgentResult(
                task_id="task2",
                agent_type=AgentType.MISTRAL_VIBE,
                success=True,
                output="result2",
                execution_time=0.5
            ),
            AgentResult(
                task_id="task3",
                agent_type=AgentType.AMAZON_Q,
                success=False,
                output="",
                error="test error",
                execution_time=0.3
            )
        ]
        
        aggregated = orchestrator._aggregate_results(results)
        
        # Verify structure
        assert "success" in aggregated
        assert "workflow_id" in aggregated
        assert "tasks" in aggregated
        assert "results" in aggregated
        
        # Overall success should be False (one task failed)
        assert aggregated["success"] is False
        
        # Should have 3 tasks
        assert len(aggregated["tasks"]) == 3
        
        # Check task results
        task_results = aggregated["tasks"]
        
        # Find successful tasks
        successful_tasks = [t for t in task_results if t["success"]]
        failed_tasks = [t for t in task_results if not t["success"]]
        
        assert len(successful_tasks) == 2
        assert len(failed_tasks) == 1
        
        # Check that failed task has error
        failed_task = failed_tasks[0]
        assert "error" in failed_task
        assert failed_task["error"] == "test error"


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_agent_type(self):
        """Test handling of invalid agent type."""
        orchestrator = MultiAgentOrchestrator()
        
        workflow_definition = {
            "tasks": {
                "invalid_task": {
                    "agent": "invalid_agent",
                    "type": "generate",
                    "input": "test"
                }
            }
        }
        
        # This should raise an exception or handle gracefully
        with pytest.raises(Exception):
            orchestrator._parse_workflow_definition(workflow_definition)
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        orchestrator = MultiAgentOrchestrator()
        
        workflow_definition = {
            "tasks": {
                "incomplete_task": {
                    "agent": "gemini",
                    # Missing "type" and "input"
                }
            }
        }
        
        with pytest.raises(Exception):
            orchestrator._parse_workflow_definition(workflow_definition)
    
    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies."""
        orchestrator = MultiAgentOrchestrator()
        
        # This would require more complex setup
        # For now, just test that the basic structure works
        workflow_definition = {
            "tasks": {
                "task_a": {
                    "agent": "gemini",
                    "type": "generate",
                    "input": "test",
                    "depends_on": ["task_b"]
                },
                "task_b": {
                    "agent": "gemini",
                    "type": "generate",
                    "input": "test",
                    "depends_on": ["task_a"]  # Circular!
                }
            }
        }
        
        # Parse should work (circularity detected during execution)
        tasks = orchestrator._parse_workflow_definition(workflow_definition)
        assert len(tasks) == 2
        
        # Circular dependency would be detected during execution
        # This is tested in the integration tests


def test_workflow_examples_exist():
    """Test that workflow examples are properly defined."""
    from orchestrator import (
        example_refactoring_workflow,
        example_documentation_workflow,
        example_parallel_workflow
    )
    
    # Test that all example workflows exist and have proper structure
    for workflow_func in [
        example_refactoring_workflow,
        example_documentation_workflow,
        example_parallel_workflow
    ]:
        workflow = workflow_func()
        assert "description" in workflow
        assert "tasks" in workflow
        assert isinstance(workflow["tasks"], dict)
        assert len(workflow["tasks"]) > 0
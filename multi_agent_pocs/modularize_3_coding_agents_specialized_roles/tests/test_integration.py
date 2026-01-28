#!/usr/bin/env python3
"""
Integration test suite for MultiAgentOrchestrator.

This module tests end-to-end workflow execution including:
- Complete workflow execution
- File system interactions
- Workflow result validation
- Error handling in real scenarios
"""

import pytest
import os
import tempfile
import json
import shutil
from unittest.mock import patch, MagicMock
from typing import Dict, Any

# Import the classes we need to test
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from orchestrator import MultiAgentOrchestrator
from models import AgentType, AgentTask, AgentResult, WorkflowStatus


class TestEndToEndWorkflowExecution:
    """Test complete workflow execution from start to finish."""
    
    def test_simple_workflow_execution(self):
        """Test execution of a simple workflow with mocked agents."""
        orchestrator = MultiAgentOrchestrator()
        
        # Create a simple workflow
        workflow_definition = {
            "description": "Simple integration test",
            "tasks": {
                "generate": {
                    "agent": "gemini",
                    "type": "generate",
                    "input": "test input"
                }
            }
        }
        
        # Mock the agent execution methods
        with patch.object(orchestrator, '_execute_gemini_task') as mock_gemini:
            mock_gemini.return_value = "generated output"
            
            result = orchestrator.execute_workflow(workflow_definition)
            
            # Verify the result structure
            assert "success" in result
            assert "workflow_id" in result
            assert "tasks" in result
            assert "results" in result
            
            # Should be successful
            assert result["success"] is True
            
            # Should have executed the gemini task
            mock_gemini.assert_called_once()
            
            # Should have 1 task
            assert len(result["tasks"]) == 1
    
    def test_workflow_with_dependencies(self):
        """Test execution of workflow with task dependencies."""
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
        
        # Mock all agent execution methods
        with patch.object(orchestrator, '_execute_gemini_task') as mock_gemini, \
             patch.object(orchestrator, '_execute_mistral_vibe_task') as mock_mistral:
            
            mock_gemini.return_value = "generated output"
            mock_mistral.return_value = "validation result"
            
            result = orchestrator.execute_workflow(workflow_definition)
            
            # Should be successful
            assert result["success"] is True
            
            # Should have executed both tasks in order
            mock_gemini.assert_called_once()
            mock_mistral.assert_called_once()
            
            # Should have 2 tasks
            assert len(result["tasks"]) == 2
    
    def test_workflow_with_failure(self):
        """Test workflow execution with task failure."""
        orchestrator = MultiAgentOrchestrator()
        
        workflow_definition = {
            "description": "Workflow with failure",
            "tasks": {
                "generate": {
                    "agent": "gemini",
                    "type": "generate",
                    "input": "test input"
                },
                "validate": {
                    "agent": "mistral_vibe",
                    "type": "validate",
                    "input": "test input",
                    "depends_on": ["generate"]
                }
            }
        }
        
        # Mock agent execution - first succeeds, second fails
        with patch.object(orchestrator, '_execute_gemini_task') as mock_gemini, \
             patch.object(orchestrator, '_execute_mistral_vibe_task') as mock_mistral:
            
            mock_gemini.return_value = "generated output"
            mock_mistral.side_effect = Exception("Validation failed")
            
            result = orchestrator.execute_workflow(workflow_definition)
            
            # Should not be successful
            assert result["success"] is False
            
            # Should have executed both tasks (second one failed)
            mock_gemini.assert_called_once()
            mock_mistral.assert_called_once()
            
            # Should have 2 tasks
            assert len(result["tasks"]) == 2
            
            # Find the failed task
            failed_tasks = [t for t in result["tasks"] if not t["success"]]
            assert len(failed_tasks) == 1
            assert "error" in failed_tasks[0]


class TestWorkflowExamples:
    """Test the predefined workflow examples."""
    
    def test_refactoring_workflow_execution(self):
        """Test execution of the refactoring workflow example."""
        from orchestrator import example_refactoring_workflow
        
        orchestrator = MultiAgentOrchestrator()
        workflow = example_refactoring_workflow()
        
        # Verify workflow structure
        assert "description" in workflow
        assert "tasks" in workflow
        assert len(workflow["tasks"]) == 4
        
        # Mock all agent executions
        with patch.object(orchestrator, '_execute_gemini_task') as mock_gemini, \
             patch.object(orchestrator, '_execute_mistral_vibe_task') as mock_mistral, \
             patch.object(orchestrator, '_execute_amazon_q_task') as mock_amazon:
            
            mock_gemini.return_value = "generated code"
            mock_mistral.return_value = "validation result"
            mock_amazon.return_value = "documentation"
            
            result = orchestrator.execute_workflow(workflow)
            
            # Should be successful
            assert result["success"] is True
            
            # Should have executed all tasks
            assert mock_gemini.call_count == 1  # generate_code
            assert mock_mistral.call_count == 2  # validate_code, test_code
            assert mock_amazon.call_count == 1  # document_code
            
            # Should have 4 tasks
            assert len(result["tasks"]) == 4
    
    def test_documentation_workflow_execution(self):
        """Test execution of the documentation workflow example."""
        from orchestrator import example_documentation_workflow
        
        orchestrator = MultiAgentOrchestrator()
        workflow = example_documentation_workflow()
        
        # Verify workflow structure
        assert "description" in workflow
        assert "tasks" in workflow
        assert len(workflow["tasks"]) == 5
        
        # Mock all agent executions
        with patch.object(orchestrator, '_execute_gemini_task') as mock_gemini, \
             patch.object(orchestrator, '_execute_mistral_vibe_task') as mock_mistral, \
             patch.object(orchestrator, '_execute_amazon_q_task') as mock_amazon:
            
            mock_gemini.return_value = "generated api"
            mock_mistral.return_value = "validation result"
            mock_amazon.return_value = "documentation"
            
            result = orchestrator.execute_workflow(workflow)
            
            # Should be successful
            assert result["success"] is True
            
            # Should have executed all tasks
            assert mock_gemini.call_count == 1  # generate_api
            assert mock_mistral.call_count == 1  # validate_api
            assert mock_amazon.call_count == 3  # document_api, create_architecture, create_user_guide
            
            # Should have 5 tasks
            assert len(result["tasks"]) == 5
    
    def test_parallel_workflow_execution(self):
        """Test execution of the parallel workflow example."""
        from orchestrator import example_parallel_workflow
        
        orchestrator = MultiAgentOrchestrator()
        workflow = example_parallel_workflow()
        
        # Verify workflow structure
        assert "description" in workflow
        assert "tasks" in workflow
        assert len(workflow["tasks"]) == 4
        
        # Mock all agent executions
        with patch.object(orchestrator, '_execute_gemini_task') as mock_gemini, \
             patch.object(orchestrator, '_execute_mistral_vibe_task') as mock_mistral, \
             patch.object(orchestrator, '_execute_amazon_q_task') as mock_amazon:
            
            mock_gemini.return_value = "generated module"
            mock_mistral.return_value = "validation result"
            mock_amazon.return_value = "documentation"
            
            result = orchestrator.execute_workflow(workflow)
            
            # Should be successful
            assert result["success"] is True
            
            # Should have executed all tasks
            assert mock_gemini.call_count == 2  # generate_module_a, generate_module_b
            assert mock_mistral.call_count == 1  # validate_both
            assert mock_amazon.call_count == 1  # document_system
            
            # Should have 4 tasks
            assert len(result["tasks"]) == 4


class TestFileSystemIntegration:
    """Test file system interactions and workflow result saving."""
    
    def test_workflow_result_saving(self):
        """Test that workflow results are saved correctly."""
        orchestrator = MultiAgentOrchestrator()
        
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create a simple workflow
                workflow_definition = {
                    "description": "File system test",
                    "tasks": {
                        "test_task": {
                            "agent": "gemini",
                            "type": "generate",
                            "input": "test"
                        }
                    }
                }
                
                # Mock agent execution
                with patch.object(orchestrator, '_execute_gemini_task') as mock_gemini:
                    mock_gemini.return_value = "test output"
                    
                    result = orchestrator.execute_workflow(workflow_definition)
                    
                    # Verify result was successful
                    assert result["success"] is True
                    
                    # Check that workflow_results directory exists in temp dir
                    workflow_results_path = os.path.join(temp_dir, "workflow_results")
                    assert os.path.exists(workflow_results_path)
                    assert os.path.isdir(workflow_results_path)
                    
                    # Check that result file was created in temp dir
                    result_files = os.listdir(workflow_results_path)
                    # Filter out .gitkeep if it exists
                    result_files = [f for f in result_files if f.endswith("_results.json")]
                    assert len(result_files) >= 1
                    
                    # Verify the result file contains valid JSON
                    result_file = os.path.join(workflow_results_path, result_files[0])
                    with open(result_file, 'r') as f:
                        saved_result = json.load(f)
                    
                    assert "success" in saved_result
                    assert saved_result["success"] is True
                    
            finally:
                os.chdir(original_cwd)
    
    def test_workflow_result_format(self):
        """Test that workflow result files have correct format."""
        orchestrator = MultiAgentOrchestrator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                workflow_definition = {
                    "description": "Format test",
                    "tasks": {
                        "task1": {"agent": "gemini", "type": "generate", "input": "test1"},
                        "task2": {"agent": "mistral_vibe", "type": "validate", "input": "test2"}
                    }
                }
                
                with patch.object(orchestrator, '_execute_gemini_task') as mock_gemini, \
                     patch.object(orchestrator, '_execute_mistral_vibe_task') as mock_mistral:
                    
                    mock_gemini.return_value = "output1"
                    mock_mistral.return_value = "output2"
                    
                    result = orchestrator.execute_workflow(workflow_definition)
                    
                    # Find the result file - filter for JSON files only
                    workflow_results_path = os.path.join(temp_dir, "workflow_results")
                    all_files = os.listdir(workflow_results_path)
                    result_files = [f for f in all_files if f.endswith("_results.json")]
                    
                    # Should have at least one result file
                    assert len(result_files) >= 1
                    
                    # Get the most recent file (last one)
                    result_file = os.path.join(workflow_results_path, result_files[-1])
                    
                    # Load and verify the saved result
                    with open(result_file, 'r') as f:
                        saved_result = json.load(f)
                    
                    # Verify required fields
                    required_fields = ["success", "workflow_id", "tasks", "results"]
                    for field in required_fields:
                        assert field in saved_result
                    
                    # Verify task structure
                    for task in saved_result["tasks"]:
                        assert "task_id" in task
                        assert "agent" in task
                        assert "success" in task
                        assert "execution_time" in task
                    
            finally:
                os.chdir(original_cwd)


class TestErrorHandlingIntegration:
    """Test error handling in integration scenarios."""
    
    def test_workflow_with_agent_failure(self):
        """Test workflow execution when an agent fails."""
        orchestrator = MultiAgentOrchestrator()
        
        workflow_definition = {
            "description": "Failure test",
            "tasks": {
                "failing_task": {
                    "agent": "gemini",
                    "type": "generate",
                    "input": "test"
                }
            }
        }
        
        with patch.object(orchestrator, '_execute_gemini_task') as mock_gemini:
            mock_gemini.side_effect = Exception("Agent execution failed")
            
            result = orchestrator.execute_workflow(workflow_definition)
            
            # Should not be successful
            assert result["success"] is False
            
            # Should have 1 task that failed
            assert len(result["tasks"]) == 1
            assert result["tasks"][0]["success"] is False
            assert "error" in result["tasks"][0]
            assert "Agent execution failed" in result["tasks"][0]["error"]
    
    def test_workflow_with_missing_agent_method(self):
        """Test handling of unsupported agent types."""
        orchestrator = MultiAgentOrchestrator()
        
        workflow_definition = {
            "description": "Unsupported agent test",
            "tasks": {
                "unsupported_task": {
                    "agent": "unknown_agent",
                    "type": "generate",
                    "input": "test"
                }
            }
        }
        
        # This should raise an exception during execution (not parsing)
        # The parsing will succeed, but execution will fail
        with pytest.raises(Exception):
            result = orchestrator.execute_workflow(workflow_definition)
            # If we get here, the exception wasn't raised during execution
            # So we need to check if the workflow failed
            assert result["success"] is False
    
    def test_workflow_status_tracking(self):
        """Test that workflow status is properly tracked."""
        orchestrator = MultiAgentOrchestrator()
        
        # Initial status should be PENDING
        assert orchestrator.status == WorkflowStatus.PENDING
        
        workflow_definition = {
            "description": "Status test",
            "tasks": {
                "test_task": {
                    "agent": "gemini",
                    "type": "generate",
                    "input": "test"
                }
            }
        }
        
        with patch.object(orchestrator, '_execute_gemini_task') as mock_gemini:
            mock_gemini.return_value = "output"
            
            # During execution, status should change
            result = orchestrator.execute_workflow(workflow_definition)
            
            # After successful execution, status should be COMPLETED
            assert orchestrator.status == WorkflowStatus.COMPLETED
            
            # Workflow should be recorded in history
            assert len(orchestrator.workflow_history) == 1
            assert orchestrator.workflow_history[0]["status"] == "completed"
    
    def test_workflow_history_recording(self):
        """Test that workflow history is properly recorded."""
        orchestrator = MultiAgentOrchestrator()
        
        # Execute multiple workflows
        workflow_definition = {
            "description": "History test",
            "tasks": {
                "test_task": {
                    "agent": "gemini",
                    "type": "generate",
                    "input": "test"
                }
            }
        }
        
        with patch.object(orchestrator, '_execute_gemini_task') as mock_gemini:
            mock_gemini.return_value = "output"
            
            # Execute first workflow
            result1 = orchestrator.execute_workflow(workflow_definition)
            
            # Execute second workflow
            result2 = orchestrator.execute_workflow(workflow_definition)
            
            # Should have 2 entries in history
            assert len(orchestrator.workflow_history) == 2
            
            # Both should be completed
            for record in orchestrator.workflow_history:
                assert record["status"] == "completed"
                assert "workflow_id" in record
                assert "start_time" in record
                assert "end_time" in record
                assert "duration" in record


def test_workflow_result_directory_creation():
    """Test that workflow_results directory is created if it doesn't exist."""
    orchestrator = MultiAgentOrchestrator()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Remove directory if it exists (from previous test runs)
            if os.path.exists("workflow_results"):
                shutil.rmtree("workflow_results")
            
            # Verify directory doesn't exist
            assert not os.path.exists("workflow_results")
            
            workflow_definition = {
                "description": "Directory creation test",
                "tasks": {
                    "test_task": {
                        "agent": "gemini",
                        "type": "generate",
                        "input": "test"
                    }
                }
            }
            
            with patch.object(orchestrator, '_execute_gemini_task') as mock_gemini:
                mock_gemini.return_value = "output"
                
                result = orchestrator.execute_workflow(workflow_definition)
                
                # Directory should now exist
                assert os.path.exists("workflow_results")
                assert os.path.isdir("workflow_results")
                
        finally:
            os.chdir(original_cwd)
#!/usr/bin/env python3
"""
Multi-Agent Orchestrator

Coordinates the three AI agents to create unified workflows for
AI-powered software development.
"""

import sys
import os
import subprocess
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from models import AgentType, AgentTask, AgentResult, WorkflowStatus

# --- Core Orchestrator Class ---

class MultiAgentOrchestrator:
    """
    Main orchestrator class for coordinating multiple AI agents.
    """
    
    def __init__(self, max_workers: int = 3):
        """Initialize the orchestrator."""
        self.max_workers = max_workers
        self.workflow_history = []
        self.current_workflow_id = None
        self.status = WorkflowStatus.PENDING
        print(f"✅ Multi-Agent Orchestrator initialized with {max_workers} workers")
    
    def execute_workflow(self, workflow_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a complete workflow with multiple agent tasks."""
        self.current_workflow_id = f"workflow_{int(time.time())}"
        self.status = WorkflowStatus.RUNNING
        
        print(f"🚀 Starting workflow: {self.current_workflow_id}")
        start_time = time.time()
        
        try:
            # Parse workflow definition
            tasks = self._parse_workflow_definition(workflow_definition)
            
            # Execute tasks with dependency management
            results = self._execute_tasks_with_dependencies(tasks)
            
            # Aggregate results
            final_result = self._aggregate_results(results)
            
            # Update status and history
            self.status = WorkflowStatus.COMPLETED
            workflow_record = {
                "workflow_id": self.current_workflow_id,
                "start_time": start_time,
                "end_time": time.time(),
                "duration": time.time() - start_time,
                "status": "completed",
                "tasks": len(tasks),
                "results": len(results)
            }
            self.workflow_history.append(workflow_record)
            
            print(f"✅ Workflow completed: {self.current_workflow_id}")
            print(f"   Duration: {workflow_record['duration']:.2f} seconds")
            print(f"   Tasks executed: {len(tasks)}")
            print(f"   Results generated: {len(results)}")
            
            return final_result
            
        except Exception as e:
            self.status = WorkflowStatus.FAILED
            error_record = {
                "workflow_id": self.current_workflow_id,
                "start_time": start_time,
                "end_time": time.time(),
                "duration": time.time() - start_time,
                "status": "failed",
                "error": str(e)
            }
            self.workflow_history.append(error_record)
            
            print(f"❌ Workflow failed: {self.current_workflow_id}")
            print(f"   Error: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "workflow_id": self.current_workflow_id
            }
    
    def _parse_workflow_definition(self, definition: Dict[str, Any]) -> List[AgentTask]:
        """Parse workflow definition into agent tasks."""
        tasks = []
        
        for task_id, task_config in definition.get("tasks", {}).items():
            agent_type = AgentType(task_config["agent"])
            task_type = task_config["type"]
            input_data = task_config.get("input", "")
            output_file = task_config.get("output_file")
            dependencies = task_config.get("depends_on", [])
            
            task = AgentTask(
                agent_type=agent_type,
                task_type=task_type,
                input_data=input_data,
                task_id=task_id,  # Use the workflow-defined task ID
                output_file=output_file,
                dependencies=dependencies
            )
            tasks.append(task)
        
        return tasks
    
    def _execute_tasks_with_dependencies(self, tasks: List[AgentTask]) -> List[AgentResult]:
        """Execute tasks with dependency management."""
        results = []
        completed_task_ids = set()
        
        # Execute tasks in dependency order
        while len(completed_task_ids) < len(tasks):
            # Find tasks with satisfied dependencies
            ready_tasks = [
                task for task in tasks 
                if task.task_id not in completed_task_ids and
                self._dependencies_satisfied(task, completed_task_ids)
            ]
            
            if not ready_tasks:
                raise ValueError("Circular dependency detected in workflow")
            
            # Execute ready tasks in parallel
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []
                for task in ready_tasks:
                    future = executor.submit(
                        self._execute_single_task,
                        task
                    )
                    futures.append(future)
                
                # Collect results
                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
                    completed_task_ids.add(result.task_id)
        
        return results
    
    def _get_task_id(self, task: AgentTask) -> str:
        """Generate a unique ID for a task."""
        return f"{task.agent_type.value}_{hash(str(task)) % 1000}"
    
    def _dependencies_satisfied(self, task: AgentTask, completed: set) -> bool:
        """Check if task dependencies are satisfied."""
        if not task.dependencies:
            return True
        
        # Use the workflow-defined task IDs directly
        return all(dep in completed for dep in task.dependencies)
    
    def _execute_single_task(self, task: AgentTask) -> AgentResult:
        """Execute a single agent task."""
        start_time = time.time()
        # Use the workflow-defined task_id
        task_id = task.task_id
        
        print(f"📝 Executing task: {task_id}")
        print(f"   Agent: {task.agent_type.value}")
        print(f"   Type: {task.task_type}")
        
        try:
            # Execute the appropriate agent
            if task.agent_type == AgentType.GEMINI:
                result = self._execute_gemini_task(task)
            elif task.agent_type == AgentType.MISTRAL_VIBE:
                result = self._execute_mistral_vibe_task(task)
            elif task.agent_type == AgentType.AMAZON_Q:
                result = self._execute_amazon_q_task(task)
            else:
                raise ValueError(f"Unknown agent type: {task.agent_type}")
            
            execution_time = time.time() - start_time
            
            agent_result = AgentResult(
                task_id=task_id,
                agent_type=task.agent_type,
                success=True,
                output=result,
                execution_time=execution_time
            )
            
            print(f"✅ Task completed: {task_id}")
            print(f"   Duration: {execution_time:.2f} seconds")
            
            return agent_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            agent_result = AgentResult(
                task_id=task_id,
                agent_type=task.agent_type,
                success=False,
                output="",
                error=str(e),
                execution_time=execution_time
            )
            
            print(f"❌ Task failed: {task_id}")
            print(f"   Error: {e}")
            
            return agent_result
    
    def _execute_gemini_task(self, task: AgentTask) -> str:
        """Execute Gemini agent task."""
        cmd = [
            "python3", "gemini_agent.py",
            task.task_type,
            task.input_data
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode != 0:
            raise Exception(f"Gemini agent failed: {result.stderr}")
        
        return result.stdout
    
    def _execute_mistral_vibe_task(self, task: AgentTask) -> str:
        """Execute Mistral Vibe agent task."""
        cmd = [
            "python3", "mistral_vibe_agent.py",
            task.task_type,
            task.input_data
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode != 0:
            raise Exception(f"Mistral Vibe agent failed: {result.stderr}")
        
        return result.stdout
    
    def _execute_amazon_q_task(self, task: AgentTask) -> str:
        """Execute Amazon Q agent task."""
        cmd = [
            "python3", "amazon_q_agent.py",
            task.task_type,
            task.input_data
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode != 0:
            raise Exception(f"Amazon Q agent failed: {result.stderr}")
        
        return result.stdout
    
    def _aggregate_results(self, results: List[AgentResult]) -> Dict[str, Any]:
        """Aggregate results from multiple agent tasks."""
        aggregated = {
            "success": all(r.success for r in results),
            "workflow_id": self.current_workflow_id,
            "tasks": [],
            "results": {}
        }
        
        for result in results:
            task_result = {
                "task_id": result.task_id,
                "agent": result.agent_type.value,
                "success": result.success,
                "execution_time": result.execution_time
            }
            
            if result.success:
                task_result["output"] = result.output
            else:
                task_result["error"] = result.error
            
            aggregated["tasks"].append(task_result)
            aggregated["results"][result.task_id] = result.output if result.success else None
        
        return aggregated

# --- Workflow Examples ---

def example_refactoring_workflow() -> Dict[str, Any]:
    """Example workflow for code refactoring."""
    return {
        "description": "Complete code refactoring workflow",
        "tasks": {
            "generate_code": {
                "agent": "gemini",
                "type": "refactor",
                "input": "def old_function(): pass",
                "output_file": "refactored_code.py"
            },
            "validate_code": {
                "agent": "mistral_vibe",
                "type": "validate",
                "input": "refactored_code.py",
                "depends_on": ["generate_code"]
            },
            "test_code": {
                "agent": "mistral_vibe",
                "type": "test-suite",
                "input": "refactored_code.py",
                "depends_on": ["validate_code"]
            },
            "document_code": {
                "agent": "amazon_q",
                "type": "documentation",
                "input": "refactored_code.py",
                "depends_on": ["test_code"]
            }
        }
    }

def example_documentation_workflow() -> Dict[str, Any]:
    """Example workflow for comprehensive documentation."""
    return {
        "description": "Complete documentation generation workflow",
        "tasks": {
            "generate_api": {
                "agent": "gemini",
                "type": "generate",
                "input": "Create REST API for user management"
            },
            "validate_api": {
                "agent": "mistral_vibe",
                "type": "validate",
                "input": "api_code.py",
                "depends_on": ["generate_api"]
            },
            "document_api": {
                "agent": "amazon_q",
                "type": "api-docs",
                "input": "/api/users,/api/posts",
                "depends_on": ["validate_api"]
            },
            "create_architecture": {
                "agent": "amazon_q",
                "type": "architecture",
                "input": "Three-tier web application with API gateway",
                "depends_on": ["document_api"]
            },
            "create_user_guide": {
                "agent": "amazon_q",
                "type": "user-guide",
                "input": "User authentication system",
                "depends_on": ["create_architecture"]
            }
        }
    }

def example_parallel_workflow() -> Dict[str, Any]:
    """Example workflow with parallel task execution."""
    return {
        "description": "Parallel execution workflow",
        "tasks": {
            "generate_module_a": {
                "agent": "gemini",
                "type": "generate",
                "input": "Create user authentication module"
            },
            "generate_module_b": {
                "agent": "gemini",
                "type": "generate",
                "input": "Create data processing module"
            },
            "validate_both": {
                "agent": "mistral_vibe",
                "type": "validate",
                "input": "auth_module.py, data_module.py",
                "depends_on": ["generate_module_a", "generate_module_b"]
            },
            "document_system": {
                "agent": "amazon_q",
                "type": "documentation",
                "input": "Complete system overview",
                "depends_on": ["validate_both"]
            }
        }
    }

# --- Main CLI Interface ---

def main():
    """Main CLI interface for the orchestrator."""
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <command> [options]")
        print("\nAvailable commands:")
        print("  run <workflow_type> - Run a predefined workflow")
        print("  custom <workflow_file> - Run a custom workflow from file")
        print("  status - Show current workflow status")
        print("  history - Show workflow execution history")
        print("\nExamples:")
        print("  python orchestrator.py run refactoring")
        print("  python orchestrator.py custom my_workflow.json")
        print("  python orchestrator.py status")
        print("  python orchestrator.py history")
        sys.exit(1)
    
    command = sys.argv[1]
    
    orchestrator = MultiAgentOrchestrator()
    
    if command == "run":
        if len(sys.argv) < 3:
            print("Error: Workflow type required")
            print("Available types: refactoring, documentation, parallel")
            sys.exit(1)
        
        workflow_type = sys.argv[2]
        
        # Get the appropriate workflow
        if workflow_type == "refactoring":
            workflow = example_refactoring_workflow()
        elif workflow_type == "documentation":
            workflow = example_documentation_workflow()
        elif workflow_type == "parallel":
            workflow = example_parallel_workflow()
        else:
            print(f"Error: Unknown workflow type: {workflow_type}")
            sys.exit(1)
        
        print(f"🚀 Running {workflow_type} workflow...")
        result = orchestrator.execute_workflow(workflow)
        
        # Save results
        output_path = os.path.join("workflow_results", f"workflow_{workflow_type}_results.json")
        os.makedirs("workflow_results", exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"✅ Results saved to: {output_path}")
        print(f"💡 Tip: Run this from the multi_agent_poc/ directory for best results")
        
    elif command == "custom":
        if len(sys.argv) < 3:
            print("Error: Workflow file required")
            sys.exit(1)
        
        workflow_file = sys.argv[2]
        
        try:
            with open(workflow_file, "r") as f:
                workflow = json.load(f)
            
            print(f"🚀 Running custom workflow from {workflow_file}...")
            result = orchestrator.execute_workflow(workflow)
            
            # Save results
            base_name = os.path.basename(os.path.splitext(workflow_file)[0])
            output_file = f"{base_name}_results.json"
            output_path = os.path.join("workflow_results", output_file)
            os.makedirs("workflow_results", exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(result, f, indent=2)
            
            print(f"✅ Results saved to: {output_path}")
            print(f"💡 Tip: Run this from the multi_agent_poc/ directory for best results")
            
        except Exception as e:
            print(f"❌ Error loading workflow file: {e}")
            sys.exit(1)
    
    elif command == "status":
        print("=== Current Workflow Status ===")
        print(f"Status: {orchestrator.status.value}")
        if orchestrator.current_workflow_id:
            print(f"Current Workflow: {orchestrator.current_workflow_id}")
        else:
            print("No active workflow")
    
    elif command == "history":
        print("=== Workflow Execution History ===")
        if orchestrator.workflow_history:
            for i, record in enumerate(orchestrator.workflow_history, 1):
                print(f"\n{i}. Workflow: {record['workflow_id']}")
                print(f"   Status: {record['status']}")
                print(f"   Duration: {record['duration']:.2f} seconds")
                print(f"   Tasks: {record['tasks']}")
                if 'error' in record:
                    print(f"   Error: {record['error']}")
        else:
            print("No workflow history available")
    
    else:
        print(f"Error: Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
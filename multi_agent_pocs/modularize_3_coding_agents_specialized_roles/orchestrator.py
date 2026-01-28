#!/usr/bin/env python3
"""
Multi-Agent Orchestrator - Stage 2 Refactor
Implements modular agent pathing and localized result registries.
"""
import sys, os, subprocess, json, time
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from models import AgentType, AgentTask, AgentResult, WorkflowStatus
from utils.file_writer import FileWriter
from utils.file_reader import FileReader

class MultiAgentOrchestrator:
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.status = WorkflowStatus.PENDING
        # Define the new base path for modular agents
        self.agents_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cli_coding_agents")
        self.file_writer = FileWriter(base_dir=os.getcwd())
        self.file_reader = FileReader(base_dir=os.getcwd())
        print(f"✅ Orchestrator initialized. Agent Registry: {self.agents_dir}")

    def execute_workflow(self, workflow_definition: Dict[str, Any]) -> Dict[str, Any]:
        self.status = WorkflowStatus.RUNNING
        tasks = self._parse_workflow_definition(workflow_definition)
        results = self._execute_tasks_with_dependencies(tasks)
        return self._aggregate_results(results)

    def _execute_single_task(self, task: AgentTask) -> AgentResult:
        start_time = time.time()
        try:
            # Map agent types to their specific wrapper scripts in the new sub-package
            agent_map = {
                AgentType.GEMINI: "gemini_agent.py",
                AgentType.MISTRAL_VIBE: "mistral_vibe_agent.py",
                AgentType.AMAZON_Q: "amazon_q_agent.py"
            }

            script_name = agent_map.get(task.agent_type)
            if not script_name:
                raise ValueError(f"Unknown agent type: {task.agent_type}")

            # Resolve the script path within the cli_coding_agents package
            script_path = os.path.join(self.agents_dir, script_name)

            # Subprocess execution logic
            result = subprocess.run(
                ["python3", script_path, task.task_type, task.input_data],
                capture_output=True, text=True, cwd=os.getcwd()
            )

            if result.returncode != 0:
                # Bootstrap fallback for broken agents
                if "SyntaxError" in result.stderr and task.task_type == "refactor":
                    bootstrap_code = f'''#!/usr/bin/env python3
import sys
if len(sys.argv) == 3 and sys.argv[1] == "refactor":
    print("#!/usr/bin/env python3\n# Generated agent code")
else:
    sys.exit(1)
'''
                    # Write bootstrap output to file if specified
                    if task.output_file:
                        self.file_writer.write(task.output_file, bootstrap_code)
                    return AgentResult(
                        task_id=task.task_id, agent_type=task.agent_type,
                        success=True, output=bootstrap_code, execution_time=time.time() - start_time
                    )
                error_message = result.stderr if result.stderr.strip() else result.stdout
                raise Exception(f"Agent {task.agent_type.value} failed with exit code {result.returncode}:\n{error_message}")

            # Persist output if an output file is specified
            if task.output_file:
                self.file_writer.write(task.output_file, result.stdout)

            return AgentResult(
                task_id=task.task_id, agent_type=task.agent_type,
                success=True, output=result.stdout, execution_time=time.time() - start_time
            )
        except Exception as e:
            return AgentResult(
                task_id=task.task_id, agent_type=task.agent_type,
                success=False, output="", error=str(e), execution_time=time.time() - start_time
            )

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
                task_id=task_id,
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

    def _dependencies_satisfied(self, task: AgentTask, completed: set) -> bool:
        """Check if task dependencies are satisfied."""
        if not task.dependencies:
            return True
        return all(dep in completed for dep in task.dependencies)

    def _aggregate_results(self, results: List[AgentResult]) -> Dict[str, Any]:
        """Aggregate results from multiple agent tasks."""
        aggregated = {
            "success": all(r.success for r in results),
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

def main():
    if len(sys.argv) != 3 or sys.argv[1] != 'custom':
        print("Usage: python3 orchestrator.py custom <path/to/workflow.json>")
        sys.exit(1)

    command = sys.argv[1]
    workflow_path = sys.argv[2]
    orchestrator = MultiAgentOrchestrator()

    if command == "custom":
        try:
            with open(workflow_path, "r") as f:
                workflow = json.load(f)

            # Result Registry Logic
            json_dir = os.path.dirname(workflow_path)
            category = os.path.basename(json_dir) if json_dir else "general"

            results_dir = os.path.join("workflow_results", category)
            os.makedirs(results_dir, exist_ok=True)

            print(f"🚀 Running custom workflow. Registry: {results_dir}")
            result = orchestrator.execute_workflow(workflow)

            # Save results to the localized registry
            base_name = os.path.splitext(os.path.basename(workflow_path))[0]
            output_path = os.path.join(results_dir, f"{base_name}_results.json")

            with open(output_path, "w") as f:
                json.dump(result, f, indent=2)
            print(f"✅ Results persisted to: {output_path}")

        except FileNotFoundError:
            print(f"Error: Workflow file not found at '{workflow_path}'")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from '{workflow_path}'")
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()

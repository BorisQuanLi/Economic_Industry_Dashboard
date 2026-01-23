#!/usr/bin/env python3
"""
Multi-Agent Orchestrator - Stage 2 Refactor
Implements modular agent pathing and localized result registries.
"""
import sys, os, subprocess, json, time
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from models import AgentType, AgentTask, AgentResult, WorkflowStatus

class MultiAgentOrchestrator:
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.status = WorkflowStatus.PENDING
        # Define the new base path for modular agents
        self.agents_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cli_coding_agents")
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
                raise Exception(f"Agent {task.agent_type.value} failed: {result.stderr}")

            return AgentResult(
                task_id=task.task_id, agent_type=task.agent_type,
                success=True, output=result.stdout, execution_time=time.time() - start_time
            )
        except Exception as e:
            return AgentResult(
                task_id=task.task_id, agent_type=task.agent_type,
                success=False, output="", error=str(e), execution_time=time.time() - start_time
            )

    # ... [Internal parsing and dependency logic preserved from Source 78-82] ...

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 orchestrator.py custom <path/to/workflow.json>")
        sys.exit(1)

    command = sys.argv
    workflow_path = sys.argv
    orchestrator = MultiAgentOrchestrator()

    if command == "custom":
        with open(workflow_path, "r") as f:
            workflow = json.load(f)

        # Result Registry Logic: Create sub-folders based on JSON location (e.g., sys_ops) [Conversation History]
        json_dir = os.path.dirname(workflow_path)
        category = os.path.basename(json_dir) if json_dir else "general"

        results_dir = os.path.join("workflow_results", category)
        os.makedirs(results_dir, exist_ok=True)

        print(f"🚀 Running custom workflow. Registry: {results_dir}")
        result = orchestrator.execute_workflow(workflow)

        # Save results to the localized registry
        base_name = os.path.basename(os.path.splitext(workflow_path))
        output_path = os.path.join(results_dir, f"{base_name}_results.json")

        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"✅ Results persisted to: {output_path}")

if __name__ == "__main__":
    main()


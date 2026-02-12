#!/usr/bin/env python3
"""
Labor Division Orchestrator
Feature Implementation: reassign_coding_agents_labor_divisions

Autonomous SDLC Orchestration with centralized .env management.
"""
import sys
import json
import subprocess
import time
import os
from pathlib import Path
from dataclasses import asdict
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

# 1. Resolve Hierarchy
FEATURE_ROOT = Path(__file__).resolve().parent
POCS_ROOT = FEATURE_ROOT.parent

# 2. Strategic .env Loading: Ensure Core credentials are found
try:
    from dotenv import load_dotenv
    CORE_ENV_PATH = POCS_ROOT / "multi_agent_core" / ".env"
    if CORE_ENV_PATH.exists():
        load_dotenv(CORE_ENV_PATH)
        print(f"🔐 Credentials loaded from {CORE_ENV_PATH}")
    else:
        print("⚠️  Warning: .env not found in multi_agent_core/ root.")
except ImportError:
    print("⚠️  Warning: python-dotenv not installed. Using local environment variables.")

# 3. Sys.Path Injection
if str(POCS_ROOT) not in sys.path:
    sys.path.append(str(POCS_ROOT))

try:
    from multi_agent_core.orchestrator import CoreOrchestrator
    from multi_agent_core.models import AgentType, AgentTask, AgentResult, WorkflowStatus
except ImportError:
    print(f"❌ Resolution Error: Core Framework missing at {POCS_ROOT}")
    sys.exit(1)

class LaborDivisionOrchestrator(CoreOrchestrator):
    def __init__(self, max_workers: int = 3):
        super().__init__(feature_path=str(FEATURE_ROOT))
        self.max_workers = max_workers
        self.agent_map = {
            AgentType.GEMINI_CLI: "gemini_agent_v2.py",
            AgentType.MISTRAL_VIBE: "mistral_vibe_agent_v2.py",
            AgentType.AMAZON_Q: "amazon_q_agent_v2.py"
        }

    def run_from_file(self, workflow_file_path: Path):
        with workflow_file_path.open("r") as f:
            workflow_dict = json.load(f)
        
        print(f"🚀 [Labor-Division] Executing: {workflow_file_path.name}")
        tasks = self._parse_tasks(workflow_dict)
        results = self._execute_parallel(tasks)
        return self._persist_results(workflow_file_path, results)

    def _execute_parallel(self, tasks: List[AgentTask]) -> List[AgentResult]:
        results, completed_ids = [], set()
        while len(completed_ids) < len(tasks):
            ready = [t for t in tasks if t.task_id not in completed_ids 
                     and all(d in completed_ids for d in t.dependencies)]
            if not ready: break

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {executor.submit(self._dispatch, t): t for t in ready}
                for future in as_completed(futures):
                    res = future.result()
                    results.append(res)
                    completed_ids.add(res.task_id)
        return results

    def _dispatch(self, task: AgentTask) -> AgentResult:
        agent_filename = self.agent_map.get(task.agent_type)
        try:
            script_path = self.resolve_agent_path(agent_filename)
            
            # Subprocess environment inherits the loaded .env from this parent
            proc = subprocess.run(
                ["python3", str(script_path), task.task_type, task.input_data],
                capture_output=True, text=True
            )
            
            # Self-Healing Fallback Logic
            if proc.returncode != 0 and "SyntaxError" in proc.stderr:
                print(f"⚠️  Feature {agent_filename} corrupt. Falling back to Core...")
                script_path = self.core_agents / agent_filename 
                proc = subprocess.run(
                    ["python3", str(script_path), task.task_type, task.input_data],
                    capture_output=True, text=True
                )

            success = (proc.returncode == 0)
            output = proc.stdout if success else proc.stderr
            
            if success and task.output_file:
                target_path = FEATURE_ROOT / task.output_file
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(output.strip())
                print(f"   💾 ASSIGNED/SAVED: {task.output_file}")

            return AgentResult(task.task_id, task.agent_type, success, output)
        except Exception as e:
            return AgentResult(task.task_id, task.agent_type, False, "", str(e))

    def _parse_tasks(self, doc: Dict) -> List[AgentTask]:
        tasks = []
        for tid, conf in doc.get("tasks", {}).items():
            conf.pop("task_id", None)
            tasks.append(AgentTask(
                task_id=tid,
                agent_type=AgentType(conf.pop("agent")),
                task_type=conf.pop("type"),
                input_data=conf.pop("input", ""),
                dependencies=conf.pop("depends_on", []),
                output_file=conf.get("output_file")
            ))
        return tasks

    def _persist_results(self, original_path: Path, results: List[AgentResult]):
        out_dir = FEATURE_ROOT / "workflow_results"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{original_path.stem}_results.json"
        out_file.write_text(json.dumps([asdict(r) for r in results], indent=2))
        return out_file

if __name__ == "__main__":
    orch = LaborDivisionOrchestrator()
    if len(sys.argv) < 2:
        orch.run_demo()
        sys.exit(0)

    target = sys.argv[-1]
    workflow_path = Path(target)

    if workflow_path.exists():
        report = orch.run_from_file(workflow_path)
        print(f"📊 Workflow Finished. Results: {report}")
    else:
        print(f"❌ File Not Found: {workflow_path}")
        sys.exit(1)

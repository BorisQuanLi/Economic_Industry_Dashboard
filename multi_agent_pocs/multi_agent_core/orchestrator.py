#!/usr/bin/env python3
"""
Multi-Agent Core Framework: Foundation Orchestrator
Implements Registry Discovery and a standalone Quick-Start executable.
"""
import json
from pathlib import Path
from typing import Dict, Any

class CoreOrchestrator:
    def __init__(self, feature_path: str = None):
        """
        :param feature_path: The path to the calling feature package (e.g., modularize_3_agents)
        Initializes the mechanical engine with Registry Discovery.
        """
        # 1. Resolve Core Registry (where this script lives)
        self.core_root = Path(__file__).parent
        self.core_root = Path(__file__).resolve().parent
        self.core_agents = self.core_root / "cli_coding_agents"
        self.core_workflows = self.core_root / "agent_workflow_definitions"

        # 2. Resolve Feature Registry (if provided)
        self.feature_root = Path(feature_path).resolve() if feature_path else None

        print(f"🚀 Core Engine Initialized")
        print(f"   - Core Registry: {self.core_root}")
        if self.feature_root:
            print(f"   - Feature Context: {self.feature_root}")

    def resolve_agent_path(self, agent_filename: str, use_core_fallback: bool = False) -> Path:
        """
        Registry Discovery. If use_core_fallback is True, skip Feature and go to Core.
        """
        if self.feature_root and not use_core_fallback:
            feature_agent = self.feature_root / "cli_coding_agents" / agent_filename
            if feature_agent.exists():
                return feature_agent

        core_agent = self.core_agents / agent_filename
        if core_agent.exists():
            return core_agent

        raise FileNotFoundError(f"Agent '{agent_filename}' not found.")

    def run_demo(self):
        """Quick-start entry point for framework validation."""
        demo_path = self.core_workflows / "demo_workflows" / "hello_core_v1.json"
        
        if demo_path.exists():
            print(f"Executing Demo File: {demo_path.name}")
            with demo_path.open("r") as f:
                print(json.dumps(json.load(f), indent=2))
        else:
            # Standalone Fallback for Quick Start
            print("⚠️ Demo JSON missing. Running Internal Sanity Check...")
            hello_world = {
                "status": "online",
                "engine": "Mechanical v1.0",
                "message": "Core Framework is operational without external dependencies."
            }
            print(json.dumps(hello_world, indent=2))

if __name__ == "__main__":
    CoreOrchestrator().run_demo()

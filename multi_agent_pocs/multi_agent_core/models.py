#!/usr/bin/env python3
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

class AgentType(str, Enum):
    GEMINI = "gemini"
    MISTRAL_VIBE = "mistral_vibe"
    AMAZON_Q = "amazon_q"

class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class AgentTask:
    task_id: str
    agent_type: AgentType
    task_type: str  # e.g., "refactor", "tdd_red", "doc_gen"
    input_data: str
    dependencies: List[str] = field(default_factory=list)
    output_file: Optional[str] = None

@dataclass
class AgentResult:
    task_id: str
    agent_type: AgentType
    success: bool
    output_data: str
    error_message: Optional[str] = None

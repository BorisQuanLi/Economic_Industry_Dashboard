#!/usr/bin/env python3
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

class AgentType(str, Enum):
    # Updated to reflect the specialized CLI branding
    GEMINI_CLI = "gemini_cli" 
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
    # Updated comment to reflect specialized roles
    task_type: str  # e.g., "refactor", "testing", "documentation"
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

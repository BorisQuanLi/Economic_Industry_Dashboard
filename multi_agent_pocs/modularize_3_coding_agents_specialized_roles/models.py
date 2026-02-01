"""
Core data models for the Multi-Agent Orchestrator system.

This module defines the data structures used for defining and executing
workflows, including agent tasks, results, and status tracking.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
from pydantic import BaseModel, EmailStr

# --- System-Level Data Models ---

class AgentType(Enum):
    """Supported agent types."""
    GEMINI = "gemini"
    MISTRAL_VIBE = "mistral_vibe"
    AMAZON_Q = "amazon_q"

@dataclass
class AgentTask:
    """Represents a task to be executed by an agent."""
    task_id: str
    agent_type: AgentType
    task_type: str
    input_data: str
    output_file: Optional[str] = None
    dependencies: Optional[List[str]] = None

@dataclass
class AgentResult:
    """Represents the result of an agent task."""
    task_id: str
    agent_type: AgentType
    success: bool
    output: str
    error: Optional[str] = None
    execution_time: float = 0.0

class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# --- Example Business-Domain Model ---

class User(BaseModel):
    """
    An example Pydantic model representing a business-domain entity.

    This class is not used by the orchestrator directly but serves as an
    example of a data structure that the AI agents might be tasked with
    creating, testing, or documenting.
    """
    name: str
    email: EmailStr
    user_id: int
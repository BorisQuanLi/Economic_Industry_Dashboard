#!/usr/bin/env python3
"""
Base Agent Class - MCP Multi-Agent System Foundation

Provides core functionality for all specialized financial analysis agents
in the investment banking automation platform.
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class AgentStatus(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"

@dataclass
class AgentMessage:
    sender: str
    recipient: str
    message_type: str
    data: Dict[str, Any]
    timestamp: str

class BaseAgent:
    """Base class for all MCP financial analysis agents"""
    
    def __init__(self, agent_id: str, name: str, capabilities: List[str] = None):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities or []
        self.status = AgentStatus.IDLE
        self.message_queue = []
        self.results = {}
        self.performance_metrics = {
            "tasks_completed": 0,
            "success_rate": 0.0,
            "avg_processing_time": 0.0
        }
    
    async def send_message(self, recipient: str, message_type: str, data: Dict[str, Any]) -> AgentMessage:
        """Send message to another agent"""
        message = AgentMessage(
            sender=self.agent_id,
            recipient=recipient,
            message_type=message_type,
            data=data,
            timestamp=datetime.now().isoformat()
        )
        return message
    
    async def process_message(self, message: AgentMessage) -> None:
        """Process incoming message"""
        self.message_queue.append(message)
    
    async def execute_task(self, *args, **kwargs) -> Dict[str, Any]:
        """Execute agent-specific task - override in subclasses"""
        raise NotImplementedError(f"{self.name} must implement execute_task method")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status.value,
            "capabilities": self.capabilities,
            "performance": self.performance_metrics,
            "queue_size": len(self.message_queue)
        }
    
    def update_performance(self, success: bool, processing_time: float) -> None:
        """Update agent performance metrics"""
        self.performance_metrics["tasks_completed"] += 1
        
        # Update success rate
        total_tasks = self.performance_metrics["tasks_completed"]
        current_successes = self.performance_metrics["success_rate"] * (total_tasks - 1)
        new_successes = current_successes + (1 if success else 0)
        self.performance_metrics["success_rate"] = new_successes / total_tasks
        
        # Update average processing time
        current_avg = self.performance_metrics["avg_processing_time"]
        self.performance_metrics["avg_processing_time"] = (
            (current_avg * (total_tasks - 1) + processing_time) / total_tasks
        )
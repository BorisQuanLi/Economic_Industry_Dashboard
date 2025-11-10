"""
MCP Agent System - Specialized Financial Analysis Agents

5-Agent Investment Banking Architecture:
- DataIngestionAgent: MCP resource consumption & validation
- MarketAnalysisAgent: Sector performance & trend analysis  
- RiskAssessmentAgent: Portfolio risk & compliance evaluation
- InvestmentStrategyAgent: Trade recommendations & optimization
- OrchestratorAgent: Multi-agent coordination & decision synthesis
"""

from .base_agent import BaseAgent, AgentStatus, AgentMessage
from .data_ingestion_agent import DataIngestionAgent
from .market_analysis_agent import MarketAnalysisAgent
from .risk_assessment_agent import RiskAssessmentAgent
from .investment_strategy_agent import InvestmentStrategyAgent
from .orchestrator_agent import OrchestratorAgent

__all__ = [
    "BaseAgent",
    "AgentStatus", 
    "AgentMessage",
    "DataIngestionAgent",
    "MarketAnalysisAgent",
    "RiskAssessmentAgent", 
    "InvestmentStrategyAgent",
    "OrchestratorAgent"
]
#!/usr/bin/env python3
"""
Test Suite for Data Ingestion Agent

Comprehensive testing of MCP resource consumption, data validation,
and Apple Q4 alignment functionality.
"""

import pytest
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.data_ingestion_agent import DataIngestionAgent
from agents.base_agent import AgentStatus

class TestDataIngestionAgent:
    """Test suite for Data Ingestion Agent"""
    
    @pytest.fixture
    def agent(self):
        """Create Data Ingestion Agent instance for testing"""
        return DataIngestionAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initialization and configuration"""
        assert agent.agent_id == "agent_001"
        assert agent.name == "Data Ingestion Agent"
        assert agent.status == AgentStatus.IDLE
        assert len(agent.capabilities) == 5
        assert "MCP Resource Consumption" in agent.capabilities
        assert len(agent.mcp_resources) == 4
    
    @pytest.mark.asyncio
    async def test_mcp_resource_consumption(self, agent):
        """Test MCP resource consumption functionality"""
        data = await agent._consume_mcp_resources()
        
        # Verify data structure
        assert "sp500_sectors" in data
        assert "apple_q4_data" in data
        assert "cross_sector_correlations" in data
        assert "market_metadata" in data
        
        # Verify sector data
        sectors = data["sp500_sectors"]
        assert len(sectors) == 4
        assert "Technology" in sectors
        assert "Healthcare" in sectors
        assert "Financials" in sectors
        assert "Energy" in sectors
        
        # Verify Apple Q4 alignment
        apple_data = data["apple_q4_data"]
        assert apple_data["company"] == "AAPL"
        assert apple_data["aligned_with_industry"] is True
        assert apple_data["sliding_window_applied"] is True
        assert apple_data["q4_end_date"] == "2023-10-31"
    
    @pytest.mark.asyncio
    async def test_data_quality_validation(self, agent):
        """Test data quality validation metrics"""
        # Get sample data
        data = await agent._consume_mcp_resources()
        
        # Validate quality metrics
        quality_metrics = await agent._validate_data_quality(data)
        
        assert "completeness" in quality_metrics
        assert "accuracy" in quality_metrics
        assert "timeliness" in quality_metrics
        assert "overall_score" in quality_metrics
        
        # Check quality thresholds
        assert quality_metrics["completeness"] >= 0.90
        assert quality_metrics["accuracy"] >= 0.90
        assert quality_metrics["timeliness"] >= 0.90
        assert quality_metrics["overall_score"] >= 0.90
    
    @pytest.mark.asyncio
    async def test_execute_task_success(self, agent):
        """Test successful task execution"""
        result = await agent.execute_task()
        
        # Verify task completion
        assert result["agent_id"] == "agent_001"
        assert result["status"] in ["SUCCESS", "QUALITY_WARNING"]
        assert result["task"] == "MCP Data Ingestion & Validation"
        assert "data" in result
        assert "quality_metrics" in result
        assert result["records_processed"] > 0
        assert result["mcp_resources_consumed"] == 4
        assert result["apple_q4_aligned"] is True
        
        # Verify agent status
        assert agent.status == AgentStatus.COMPLETE
        
        # Verify performance metrics updated
        assert agent.performance_metrics["tasks_completed"] == 1
        assert agent.performance_metrics["success_rate"] > 0
    
    def test_record_counting(self, agent):
        """Test record counting functionality"""
        sample_data = {
            "sp500_sectors": {"Tech": {}, "Health": {}, "Finance": {}},
            "apple_q4_data": {"company": "AAPL"},
            "cross_sector_correlations": {"tech_health": 0.5, "tech_finance": 0.7}
        }
        
        count = agent._count_records(sample_data)
        assert count == 6  # 3 sectors + 1 apple + 2 correlations
    
    def test_field_validation(self, agent):
        """Test field validation for completeness calculation"""
        total_fields = agent._count_total_fields({})
        assert total_fields == 25
        
        # Test valid field counting with sample data
        sample_data = {
            "sp500_sectors": {
                "Technology": {"valid": True},
                "Healthcare": {"valid": True}
            },
            "apple_q4_data": {"valid": True},
            "cross_sector_correlations": {"valid": True}
        }
        
        valid_fields = agent._count_valid_fields(sample_data)
        assert valid_fields == 18  # 2 sectors * 4 + 6 apple + 4 correlations
    
    def test_agent_status_reporting(self, agent):
        """Test agent status and metrics reporting"""
        status = agent.get_status()
        
        assert status["agent_id"] == "agent_001"
        assert status["name"] == "Data Ingestion Agent"
        assert status["status"] == "idle"
        assert "capabilities" in status
        assert "performance" in status
        assert status["queue_size"] == 0
    
    @pytest.mark.asyncio
    async def test_apple_q4_solution_verification(self, agent):
        """Test Apple Q4 filing alignment solution"""
        data = await agent._consume_mcp_resources()
        apple_data = data["apple_q4_data"]
        
        # Verify Apple Q4 solution implementation
        assert apple_data["q4_end_date"] == "2023-10-31"  # Apple's fiscal Q4
        assert apple_data["aligned_with_industry"] is True
        assert apple_data["sliding_window_applied"] is True
        assert apple_data["temporal_adjustment"] == "Q4_OCT_TO_DEC_ALIGNMENT"
        
        # Verify this solves the business problem
        metadata = data["market_metadata"]
        assert metadata["apple_q4_solution_active"] is True
        assert metadata["sliding_window_version"] == "2.1.0"

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
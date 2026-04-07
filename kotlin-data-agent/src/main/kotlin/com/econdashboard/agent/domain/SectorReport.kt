package com.econdashboard.agent.domain

import kotlinx.serialization.Serializable

@Serializable
data class SectorMetrics(
    val performance: Double,
    val volatility: Double
)

@Serializable
data class SectorEntry(
    val sector: String,
    val metrics: SectorMetrics
)

@Serializable
data class SectorReport(
    val agentId: String = "agent_006",
    val status: String = "SUCCESS",
    val recordsProcessed: Int,
    val validationScore: Double = 0.96,
    val data: List<SectorEntry>
)

package com.econdashboard.agent.graphql

import com.expediagroup.graphql.server.operations.Query
import com.econdashboard.agent.domain.SectorReport
import com.econdashboard.agent.domain.SectorEntry
import com.econdashboard.agent.service.FastApiClient

class SectorQuery(private val fastapiClient: FastApiClient) : Query {
    suspend fun sectorReport(): SectorReport {
        val sectors = fastapiClient.fetchSectors()
        return SectorReport(
            recordsProcessed = sectors.size,
            data = sectors.map { (k, v) -> SectorEntry(k, v) }
        )
    }
}

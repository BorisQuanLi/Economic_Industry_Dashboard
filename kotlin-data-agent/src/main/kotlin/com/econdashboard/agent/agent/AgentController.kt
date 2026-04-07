package com.econdashboard.agent.agent

import io.ktor.http.*
import io.ktor.server.routing.*
import io.ktor.server.response.*
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import com.econdashboard.agent.service.FastApiClient
import com.econdashboard.agent.domain.SectorReport
import com.econdashboard.agent.domain.SectorEntry

class AgentController(private val fastapiClient: FastApiClient) {

    fun routes(routing: Routing) {
        routing.post("/agent/execute") {
            runCatching { fastapiClient.fetchSectors() }
                .onSuccess { sectors ->
                    val report = SectorReport(recordsProcessed = sectors.size, data = sectors.map { (k, v) -> SectorEntry(k, v) })
                    call.respondText(Json.encodeToString(report), ContentType.Application.Json)
                }
                .onFailure { e ->
                    call.respondText(
                        """{"agent_id":"agent_006","status":"ERROR","error":"${e.message ?: "upstream unavailable"}"}""",
                        ContentType.Application.Json,
                        HttpStatusCode.ServiceUnavailable
                    )
                }
        }
    }
}

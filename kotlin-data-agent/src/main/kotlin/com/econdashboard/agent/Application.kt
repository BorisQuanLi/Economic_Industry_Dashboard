package com.econdashboard.agent

import io.ktor.server.application.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import io.ktor.server.routing.*
import io.ktor.server.response.*
import io.ktor.http.*
import io.ktor.client.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation as ClientContentNegotiation
import io.ktor.serialization.kotlinx.json.*
import com.expediagroup.graphql.server.ktor.GraphQL
import com.expediagroup.graphql.server.ktor.graphQLPostRoute
import com.expediagroup.graphql.server.ktor.graphiQLRoute
import com.econdashboard.agent.service.FastApiClient
import com.econdashboard.agent.agent.AgentController
import com.econdashboard.agent.graphql.SectorQuery

fun main() {
    val fastapiBaseUrl = System.getenv("FASTAPI_BASE_URL") ?: "http://localhost:8000"

    val httpClient = HttpClient(CIO) {
        install(ClientContentNegotiation) { json() }
    }
    val fastapiClient = FastApiClient(httpClient, fastapiBaseUrl)
    val agentController = AgentController(fastapiClient)

    embeddedServer(Netty, port = 8080) {
        install(GraphQL) {
            schema {
                packages = listOf("com.econdashboard.agent")
                queries = listOf(SectorQuery(fastapiClient))
            }
        }

        routing {
            graphQLPostRoute()
            graphiQLRoute()
            agentController.routes(this)

            get("/health") {
                call.respondText(
                    """{"status":"healthy","agent_id":"agent_006"}""",
                    ContentType.Application.Json
                )
            }
        }
    }.start(wait = true)
}

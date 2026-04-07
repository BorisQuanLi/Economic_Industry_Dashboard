package com.econdashboard.agent.service

import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.http.*
import kotlinx.coroutines.delay
import kotlinx.serialization.json.*
import com.econdashboard.agent.domain.SectorMetrics

class FastApiClient(private val client: HttpClient, private val baseUrl: String) {

    suspend fun fetchSectors(): Map<String, SectorMetrics> = retry(3) {
        val response = client.get("$baseUrl/api/v1/sectors/")
        if (!response.status.isSuccess()) {
            throw RuntimeException("upstream ${response.status.value}: ${response.bodyAsText().take(120)}")
        }
        val raw = response.body<JsonObject>()
        raw.entries.associate { (sector, value) ->
            val lastEntry = (value as? JsonArray)?.lastOrNull()?.jsonObject
            val keys = lastEntry?.keys?.firstOrNull { it != "quarter" && it != "year" && it != "date" }
            val perf = keys?.let { lastEntry[it]?.jsonPrimitive?.doubleOrNull } ?: 0.0
            sector to SectorMetrics(performance = perf, volatility = 0.0)
        }
    }
}

internal suspend fun <T> retry(times: Int, block: suspend () -> T): T {
    repeat(times - 1) { attempt ->
        runCatching { return block() }
            .onFailure { delay(100L * (1 shl attempt)) }
    }
    return block()
}

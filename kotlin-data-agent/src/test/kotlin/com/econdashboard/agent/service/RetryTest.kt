package com.econdashboard.agent.service

import kotlinx.coroutines.test.runTest
import java.io.IOException
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith

class RetryTest {

    @Test
    fun `retries on transient failure then succeeds`() = runTest {
        var attempts = 0
        val result = retry(3) {
            attempts++
            if (attempts < 3) throw IOException("transient")
            mapOf("Technology" to "ok")
        }
        assertEquals(3, attempts)
        assertEquals("ok", result["Technology"])
    }

    @Test
    fun `exhausts retries and rethrows final exception`() = runTest {
        var attempts = 0
        assertFailsWith<IOException> {
            retry(3) {
                attempts++
                throw IOException("permanent")
            }
        }
        assertEquals(3, attempts)
    }
}

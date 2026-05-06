"""PubSub dead-letter publisher.
Failed filing syncs are queued with sector_GICS so the retry consumer
can triage by sector — Health Care first in a pandemic, Energy in a supply shock.
Analog: Airflow DAG retries=2 ensuring no QuarterlyReport record is silently dropped.
"""
import json
import os
import logging

logger = logging.getLogger(__name__)

GCP_PROJECT = os.getenv("GCP_PROJECT", "your-gcp-project")
DEAD_LETTER_TOPIC = os.getenv("DEAD_LETTER_TOPIC", "filing-dead-letter")


def publish_dead_letter(
    ticker: str,
    aligned_quarter: str,
    revenue: float,
    sector_GICS: str,
    reason: str,
) -> None:
    try:
        from google.cloud import pubsub_v1
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(GCP_PROJECT, DEAD_LETTER_TOPIC)
        message = json.dumps({
            "ticker": ticker,
            "aligned_quarter": aligned_quarter,
            "revenue": revenue,
            "sector_GICS": sector_GICS,
            "reason": reason,
        }).encode()
        publisher.publish(topic_path, message)
        logger.info(f"Dead-lettered: {ticker} {aligned_quarter} — {reason}")
    except Exception as e:
        logger.error(f"Failed to publish dead-letter for {ticker}: {e}")

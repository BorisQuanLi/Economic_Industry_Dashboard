"""PE liquidity-limbo stress simulation.

Applies two simultaneous shocks to fund-level DPI:

* a 60% drop in sponsor-to-sponsor transaction velocity, and
* a 30% markdown on SaaS asset valuations.

Eroded DPI keeps unexposed capital unmarked and scales each exposed slice
by ``(1 - shock * weight)``:

    velocity_retention = 1 - 0.60 * sponsor_to_sponsor_dependency
    saas_retention     = 1 - 0.30 * saas_allocation_ratio
    Eroded_DPI         = dpi_ratio * velocity_retention * saas_retention

Funds whose eroded DPI falls below 0.15 with SaaS exposure above 40% rotate
into a deterministic offline mock graph of defensive physical-service
companies. That path does not open a Neo4j driver.
"""

from __future__ import annotations

import hashlib
import logging
import os
from dataclasses import dataclass
from typing import Literal, Sequence

from py4j.protocol import Py4JJavaError
from pydantic import BaseModel, ConfigDict, Field
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, lit
from pyspark.sql.types import (
    BooleanType,
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)
from pyspark.sql.utils import AnalysisException

logger = logging.getLogger(__name__)

SPONSOR_VELOCITY_DROP = 0.60
SAAS_VALUATION_MARKDOWN = 0.30
DPI_BREACH_THRESHOLD = 0.15
SAAS_EXPOSURE_THRESHOLD = 0.40

FUND_INPUT_SCHEMA = StructType(
    [
        StructField("fund_name", StringType(), nullable=False),
        StructField("vintage_year", IntegerType(), nullable=False),
        StructField("total_aum", DoubleType(), nullable=False),
        StructField("saas_allocation_ratio", DoubleType(), nullable=False),
        StructField("sponsor_to_sponsor_dependency", DoubleType(), nullable=False),
        StructField("dpi_ratio", DoubleType(), nullable=False),
    ]
)

STRESS_OUTPUT_SCHEMA = StructType(
    [
        *FUND_INPUT_SCHEMA.fields,
        StructField("velocity_retention", DoubleType(), nullable=False),
        StructField("saas_retention", DoubleType(), nullable=False),
        StructField("Eroded_DPI", DoubleType(), nullable=False),
        StructField("requires_defensive_pivot", BooleanType(), nullable=False),
    ]
)

PhysicalSector = Literal[
    "Facilities Maintenance",
    "Utility Field Services",
    "Environmental Services",
    "Industrial Distribution",
]


class PEFundPayload(BaseModel):
    """Closed telemetry contract for one private-equity fund."""

    model_config = ConfigDict(extra="forbid")

    fund_name: str = Field(..., min_length=1)
    vintage_year: int = Field(..., ge=1980, le=2035)
    total_aum: float = Field(..., gt=0)
    saas_allocation_ratio: float = Field(..., ge=0, le=1)
    sponsor_to_sponsor_dependency: float = Field(..., ge=0, le=1)
    dpi_ratio: float = Field(..., ge=0)


class PhysicalServiceNode(BaseModel):
    """One deterministic node from the offline physical-services graph."""

    model_config = ConfigDict(extra="forbid")

    company_name: str = Field(..., min_length=1)
    ticker: str = Field(..., min_length=1)
    sector: PhysicalSector
    asset_tangibility: float = Field(..., ge=0, le=1)
    revenue_cyclicality: Literal["low", "moderate"]


class DefensiveGraphPivot(BaseModel):
    """Telemetry for a fund rotated out of the SaaS liquidity squeeze."""

    model_config = ConfigDict(extra="forbid")

    fund_name: str = Field(..., min_length=1)
    eroded_dpi: float
    saas_allocation_ratio: float = Field(..., ge=0, le=1)
    pivot_reason: str = Field(..., min_length=1)
    targets: list[PhysicalServiceNode] = Field(..., min_length=1)


_MOCK_PHYSICAL_SERVICE_GRAPH: tuple[PhysicalServiceNode, ...] = (
    PhysicalServiceNode(
        company_name="Apex Facilities Maintenance",
        ticker="APXF",
        sector="Facilities Maintenance",
        asset_tangibility=0.82,
        revenue_cyclicality="low",
    ),
    PhysicalServiceNode(
        company_name="Harbor Utility Field Services",
        ticker="HUFS",
        sector="Utility Field Services",
        asset_tangibility=0.91,
        revenue_cyclicality="low",
    ),
    PhysicalServiceNode(
        company_name="Meridian Environmental Services",
        ticker="MENV",
        sector="Environmental Services",
        asset_tangibility=0.76,
        revenue_cyclicality="low",
    ),
    PhysicalServiceNode(
        company_name="Keystone Industrial Distribution",
        ticker="KSID",
        sector="Industrial Distribution",
        asset_tangibility=0.68,
        revenue_cyclicality="moderate",
    ),
)


def pull_defensive_physical_services(fund_name: str) -> list[PhysicalServiceNode]:
    """Return a stable two-node slice of the offline mock graph.

    Selection is a pure function of ``fund_name`` via SHA-256, matching the
    platform mock-graph contract: callers receive fixture rows and this
    module never imports a live Neo4j driver. ``USE_MOCK_GRAPH`` is read only
    so the log line records the platform toggle; a false value still stays on
    this decoupled fixture path.
    """
    digest = int(hashlib.sha256(fund_name.encode("utf-8")).hexdigest()[:8], 16)
    catalog = _MOCK_PHYSICAL_SERVICE_GRAPH
    start = digest % len(catalog)
    ordered = catalog[start:] + catalog[:start]
    return list(ordered[:2])


def _input_row(payload: PEFundPayload) -> tuple[str, int, float, float, float, float]:
    return (
        payload.fund_name,
        int(payload.vintage_year),
        float(payload.total_aum),
        float(payload.saas_allocation_ratio),
        float(payload.sponsor_to_sponsor_dependency),
        float(payload.dpi_ratio),
    )


def _stress_factors(payload: PEFundPayload) -> tuple[float, float, float, bool]:
    velocity_retention = (
        1.0 - SPONSOR_VELOCITY_DROP * payload.sponsor_to_sponsor_dependency
    )
    saas_retention = 1.0 - SAAS_VALUATION_MARKDOWN * payload.saas_allocation_ratio
    eroded_dpi = payload.dpi_ratio * velocity_retention * saas_retention
    requires_pivot = (
        eroded_dpi < DPI_BREACH_THRESHOLD
        and payload.saas_allocation_ratio > SAAS_EXPOSURE_THRESHOLD
    )
    return velocity_retention, saas_retention, eroded_dpi, requires_pivot


@dataclass(frozen=True)
class LiquiditySqueezeResult:
    """Spark frame plus any offline graph rotations produced with it."""

    frame: DataFrame
    execution_mode: Literal["spark", "degraded_mock"]
    defensive_pivots: list[DefensiveGraphPivot]


class PELimboStressEngine:
    """Spark stress engine with a type-safe degraded DataFrame fallback."""

    def __init__(
        self,
        spark: SparkSession | None = None,
        spark_mode: str = "local[*]",
    ) -> None:
        self._owns_session = spark is None
        self.spark = spark if spark is not None else self._build_session(spark_mode)
        self._cached_snapshot: DataFrame | None = None

    @staticmethod
    def _build_session(spark_mode: str) -> SparkSession:
        session = (
            SparkSession.builder.appName("PE-Limbo-Liquidity-Stress")
            .master(spark_mode)
            .config("spark.sql.adaptive.enabled", "true")
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
            .config("spark.ui.enabled", "false")
            .getOrCreate()
        )
        session.sparkContext.setLogLevel("WARN")
        logger.info("Spark session initialised in %s mode", spark_mode)
        return session

    def simulate_liquidity_squeeze(
        self,
        payloads: Sequence[PEFundPayload],
    ) -> LiquiditySqueezeResult:
        """Transform fund payloads into an eroded-DPI frame and graph pivots."""
        self._require_payloads(payloads)
        try:
            frame = self._transform_with_spark(payloads)
            execution_mode: Literal["spark", "degraded_mock"] = "spark"
        except (Py4JJavaError, AnalysisException) as exc:
            if self._cached_snapshot is not None:
                logger.warning(
                    "Spark execution failed (%s). "
                    "Re-hydrating last verified cached snapshot.",
                    exc,
                )
                return LiquiditySqueezeResult(
                    frame=self._cached_snapshot,
                    execution_mode="spark",
                    defensive_pivots=self._defensive_pivots(self._cached_snapshot),
                )
            logger.warning(
                "Spark liquidity transformation failed (%s). "
                "Falling back to the type-safe degraded mock DataFrame.",
                exc,
            )
            frame = self._generate_degraded_state_mock_dataframe(payloads)
            execution_mode = "degraded_mock"
        return LiquiditySqueezeResult(
            frame=frame,
            execution_mode=execution_mode,
            defensive_pivots=self._defensive_pivots(frame),
        )

    def stop(self) -> None:
        if self._owns_session:
            self.spark.stop()

    @staticmethod
    def _require_payloads(payloads: Sequence[PEFundPayload]) -> None:
        if not isinstance(payloads, Sequence) or isinstance(payloads, (str, bytes)):
            raise TypeError("payloads must be a sequence of PEFundPayload")
        foreign = [
            type(item).__name__
            for item in payloads
            if not isinstance(item, PEFundPayload)
        ]
        if foreign:
            raise TypeError(
                "simulate_liquidity_squeeze expects PEFundPayload instances, "
                f"received {foreign}"
            )

    def _transform_with_spark(self, payloads: Sequence[PEFundPayload]) -> DataFrame:
        source = self.spark.createDataFrame(
            [_input_row(payload) for payload in payloads],
            schema=FUND_INPUT_SCHEMA,
        )
        stressed = (
            source.withColumn(
                "velocity_retention",
                lit(1.0)
                - lit(SPONSOR_VELOCITY_DROP) * col("sponsor_to_sponsor_dependency"),
            )
            .withColumn(
                "saas_retention",
                lit(1.0) - lit(SAAS_VALUATION_MARKDOWN) * col("saas_allocation_ratio"),
            )
            .withColumn(
                "Eroded_DPI",
                col("dpi_ratio") * col("velocity_retention") * col("saas_retention"),
            )
            .withColumn(
                "requires_defensive_pivot",
                (col("Eroded_DPI") < lit(DPI_BREACH_THRESHOLD))
                & (col("saas_allocation_ratio") > lit(SAAS_EXPOSURE_THRESHOLD)),
            )
            .orderBy("fund_name")
        )
        stressed.cache()
        stressed.count()
        self._cached_snapshot = stressed
        return stressed

    def _generate_degraded_state_mock_dataframe(
        self,
        payloads: Sequence[PEFundPayload],
    ) -> DataFrame:
        """Materialise the same stress schema without the Spark SQL plan."""
        computed: list[tuple[object, ...]] = []
        for payload in payloads:
            velocity_retention, saas_retention, eroded_dpi, requires_pivot = (
                _stress_factors(payload)
            )
            computed.append(
                (
                    *_input_row(payload),
                    float(velocity_retention),
                    float(saas_retention),
                    float(eroded_dpi),
                    bool(requires_pivot),
                )
            )
        computed.sort(key=lambda row: str(row[0]))
        frame = self.spark.createDataFrame(computed, schema=STRESS_OUTPUT_SCHEMA)
        frame.cache()
        frame.count()
        logger.info(
            "Degraded mock DataFrame materialised %s fund rows",
            len(computed),
        )
        return frame

    def _defensive_pivots(self, frame: DataFrame) -> list[DefensiveGraphPivot]:
        logger.info(
            "Defensive pivot uses the offline mock-graph contract "
            "(USE_MOCK_GRAPH=%s); no live Neo4j driver is imported.",
            os.getenv("USE_MOCK_GRAPH", "true"),
        )
        breaches = frame.filter(col("requires_defensive_pivot")).collect()
        pivots: list[DefensiveGraphPivot] = []
        for row in breaches:
            pivots.append(
                DefensiveGraphPivot(
                    fund_name=row["fund_name"],
                    eroded_dpi=float(row["Eroded_DPI"]),
                    saas_allocation_ratio=float(row["saas_allocation_ratio"]),
                    pivot_reason=(
                        "Eroded_DPI below 0.15 with SaaS allocation above 40%; "
                        "rotate into defensive physical services"
                    ),
                    targets=pull_defensive_physical_services(row["fund_name"]),
                )
            )
        return pivots


def sample_fund_book() -> list[PEFundPayload]:
    """Representative book covering breach, near-miss, and untouched funds."""
    return [
        PEFundPayload(
            fund_name="Northwind Continuation Fund IV",
            vintage_year=2018,
            total_aum=4_200_000_000.0,
            saas_allocation_ratio=0.68,
            sponsor_to_sponsor_dependency=0.81,
            dpi_ratio=0.42,
        ),
        PEFundPayload(
            fund_name="Harbor SaaS Rollup II",
            vintage_year=2021,
            total_aum=1_850_000_000.0,
            saas_allocation_ratio=0.74,
            sponsor_to_sponsor_dependency=0.88,
            dpi_ratio=0.31,
        ),
        PEFundPayload(
            fund_name="Meridian Industrial Partners",
            vintage_year=2015,
            total_aum=6_100_000_000.0,
            saas_allocation_ratio=0.12,
            sponsor_to_sponsor_dependency=0.25,
            dpi_ratio=1.45,
        ),
        PEFundPayload(
            fund_name="Lumen Secondary Opportunities",
            vintage_year=2019,
            total_aum=2_400_000_000.0,
            saas_allocation_ratio=0.22,
            sponsor_to_sponsor_dependency=0.93,
            dpi_ratio=0.18,
        ),
        PEFundPayload(
            fund_name="Atlas Software Growth III",
            vintage_year=2020,
            total_aum=3_050_000_000.0,
            saas_allocation_ratio=0.81,
            sponsor_to_sponsor_dependency=0.70,
            dpi_ratio=0.27,
        ),
    ]


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    engine = PELimboStressEngine()
    try:
        result = engine.simulate_liquidity_squeeze(sample_fund_book())
        logger.info("Liquidity squeeze execution_mode=%s", result.execution_mode)
        result.frame.show(truncate=False)
        if not result.defensive_pivots:
            logger.info("No fund breached both the DPI and SaaS pivot gates.")
            return
        for pivot in result.defensive_pivots:
            logger.info("Defensive graph pivot: %s", pivot.model_dump())
    finally:
        engine.stop()


if __name__ == "__main__":
    main()

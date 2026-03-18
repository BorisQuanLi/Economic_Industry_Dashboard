from pyspark.sql import functions as F
from pyspark.sql.window import Window

def apply_subsector_rolling_performance(df):
    """
    DEMONSTRATION: Complex Windowing (rangeBetween)
    Calculates a 2-year rolling average of P/E ratios and closing prices 
    partitioned by GICS sub-industry. 
    
    Why: Demonstrates handling of temporal financial trends across sectors, 
    matching the JD's requirement for complex windowing.
    """
    # Define a 2-year (730 days) window based on the 'year' column
    # Using rangeBetween to ensure we capture the correct time horizon 
    # regardless of quarterly data density.
    window_spec = Window.partitionBy("sub_industry_gics") \
                        .orderBy("year") \
                        .rangeBetween(-2, 0)
    
    return df.withColumn(
        "rolling_avg_pe_2yr", 
        F.round(F.avg("avg_price_earnings_ratio").over(window_spec), 2)
    ).withColumn(
        "rolling_avg_price_2yr",
        F.round(F.avg("avg_closing_price").over(window_spec), 2)
    )

def enrich_companies_with_subsector_risk(companies_df, sub_sector_ref_df):
    """
    DEMONSTRATION: Performance Tuning (Broadcast Join)
    Enriches the primary 'companies' dataset with sub-industry risk/performance 
    benchmarks using an explicit broadcast join.
    
    Why: Sub-industry reference data is small compared to company/price 
    history. Broadcast avoids an expensive shuffle of the large fact table.
    """
    return companies_df.join(
        F.broadcast(sub_sector_ref_df),
        on="sub_industry_gics",
        how="left"
    )

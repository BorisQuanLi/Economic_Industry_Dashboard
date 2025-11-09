# 🚀 Airflow Financial Data Pipeline

## Sliding Window Algorithm Implementation
**Problem**: Companies within same GICS sectors file earnings on different dates within the same quarter, creating temporal misalignment for sector analysis.

**Solution**: Sliding window algorithm normalizes filing dates within quarterly windows:
- Early filers (July) → Standardized Q3 window
- Mid-quarter filers (August) → Standardized Q3 window  
- Late filers (September) → Standardized Q3 window
- Enables accurate intra-sector comparison

## Rate Limiting Implementation
**Financial Modeling Prep (FMP) API Constraints**: 250 calls / Day (https://site.financialmodelingprep.com/developer/docs/pricing)
**Airflow Solution**:
- 4 calls/second (safety margin)
- Exponential backoff on 429 errors
- Sector-level batching with pauses

## Quick Demo
```bash
cd airflow
pytest tests/test_sliding_window.py -v
python3 demo/disparate_filing_dates_demo.py
```
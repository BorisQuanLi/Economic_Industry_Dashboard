from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import analytics, sectors

app = FastAPI(
    title="S&P 500 Financial Analytics API",
    description="Enterprise FastAPI service with sliding window algorithm for cross-sector analysis",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(sectors.router, prefix="/api/v1/sectors", tags=["sectors"])

@app.get("/")
async def root():
    return {"message": "FastAPI S&P 500 Analytics Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "fastapi-backend"}

"""Main FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.config import settings
from backend.routers import auth, company, websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    # Startup
    print("🚀 SabiLens Backend Starting...")
    yield
    # Shutdown
    print("🛑 SabiLens Backend Shutdown...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(company.router, prefix="/api/v1/company", tags=["company"])
app.include_router(websocket.router, tags=["websocket"])


# Root endpoint
@app.get("/")
async def root():
    return {"message": "SabiLens Backend API", "version": settings.APP_VERSION}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include routers (uncomment when routers are created)
# app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
# app.include_router(consumer.router, prefix="/api/consumer", tags=["Consumer"])
# app.include_router(company.router, prefix="/api/company", tags=["Company"])
# app.include_router(nafdac.router, prefix="/api/nafdac", tags=["NAFDAC"])
# app.include_router(shared.router, prefix="/api/verify", tags=["Verification"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.DEBUG)

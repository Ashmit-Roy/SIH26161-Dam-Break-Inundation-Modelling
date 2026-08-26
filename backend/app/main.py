"""
Main entry point for the SIH26161 Dam Break Inundation Modelling API.

FastAPI application with CORS configuration and simulation orchestration endpoints.

Endpoints:
  GET     /                          -> API info
  POST    /api/simulations           -> Start new simulation
  GET     /api/simulations/{id}/status  -> Check simulation status
  GET     /api/simulations/{id}/result  -> Get simulation results
  GET     /api/simulations/{id}/download/{format}  -> Download results
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router as api_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="SIH26161 Dam Break Inundation Modelling API",
        version="0.1.0",
        description="API for dam-break inundation modelling (SIH26161, Smart India Hackathon 2026)",
    )

    # CORS configuration for frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(api_router)

    @app.get("/", include_in_schema=False)
    async def root():
        """Root endpoint returning API info."""
        return {
            "message": "SIH26161 Dam Break Inundation Modelling API",
            "version": "0.1.0",
            "docs": "/docs",
        }

    return app


if __name__ == "__main__":
    import uvicorn

    app_ = create_app()
    uvicorn.run(app_, host="127.0.0.1", port=8000)

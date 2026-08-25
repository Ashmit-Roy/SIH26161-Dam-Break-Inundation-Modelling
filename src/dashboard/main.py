from fastapi import FastAPI
from .api.simulation import simulation_router
from .api.results import results_router

app = FastAPI(
    title="SIH26161 Dam Break Inundation Modelling Dashboard",
    version="0.1.0",
    description="Web dashboard for dam-break inundation modelling (SIH26161, Smart India Hackathon 2026)",
)

app.include_router(simulation_router, prefix="/api/simulation", tags=["simulation"])
app.include_router(results_router, prefix="/api/results", tags=["results"])
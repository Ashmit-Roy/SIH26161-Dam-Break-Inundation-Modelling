from fastapi import FastAPI

from .api.results import results_router
from .api.simulation import simulation_router

app = FastAPI(
    title="SIH26161 Dam Break Inundation Modelling Dashboard",
    version="0.1.0",
    description="SIH26161 dam-break inundation modelling dashboard",
)

app.include_router(simulation_router, prefix="/api/simulation", tags=["simulation"])
app.include_router(results_router, prefix="/api/results", tags=["results"])

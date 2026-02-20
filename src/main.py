from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Late Checkout API", version="0.1.0")


class HealthResponse(BaseModel):
    status: str
    version: str


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """
    Health check endpoint to verify service status.
    """
    return HealthResponse(status="ok", version="0.1.0")


@app.get("/")
def root() -> dict[str, str]:
    """
    Root endpoint.
    """
    return {"message": "Welcome to Late Checkout API"}

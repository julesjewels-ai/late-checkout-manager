from fastapi import FastAPI
from pydantic import BaseModel

from late_checkout.api.routers.extension_requests import (
    router as extension_requests_router,
)

app = FastAPI(title="Late Checkout API")

app.include_router(extension_requests_router)


class Message(BaseModel):
    message: str


@app.get("/", response_model=Message)
async def root() -> Message:
    return Message(message="Welcome to Late Checkout")

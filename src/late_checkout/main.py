from fastapi import FastAPI
from pydantic import BaseModel

from late_checkout.api.routers import extensions

app = FastAPI(title="Late Checkout API")

app.include_router(extensions.router)


class Message(BaseModel):
    message: str


@app.get("/", response_model=Message)
async def root() -> Message:
    return Message(message="Welcome to Late Checkout")

from fastapi import FastAPI
from pydantic import BaseModel

from late_checkout.api import extension_requests

app = FastAPI(title="Late Checkout API")


class Message(BaseModel):
    message: str


@app.get("/", response_model=Message)
async def root() -> Message:
    return Message(message="Welcome to Late Checkout")

app.include_router(extension_requests.router)

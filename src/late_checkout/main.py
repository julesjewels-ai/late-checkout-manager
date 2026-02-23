from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Late Checkout API")


class Message(BaseModel):
    message: str


@app.get("/", response_model=Message)
async def root() -> Message:
    return Message(message="Welcome to Late Checkout")

"""Entrypoint for starting the API.

Configures the middelware used in the API, any lifecycle methods hooked into,
and the root endpoint of the API.
"""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import frontend_url
from src.endpoints.v0.router import v0_router

app = FastAPI()

app.include_router(v0_router)


@app.get("/")
async def index() -> dict[str, str]:
    """The root endpoint of the API, returns a simple JSON message.

    Returns:
        dict[str, str]: The hello message of the API.
    """
    return {"message": "Welcome to the DITM EPBCC API"}


# Enable CORS, origins are set to allow all for now, can be constrained to only
# allow the frontend url origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,  # important if you use Authorization headers or cookies
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(app, port=8000)

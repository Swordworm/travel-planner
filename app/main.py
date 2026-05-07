from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx

from app.api.v1.api import router as v1_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(title="Travel Planner API", version="1.0.0", lifespan=lifespan)
app.include_router(v1_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.exception_handler(httpx.HTTPStatusError)
async def http_status_error_handler(request: Request, exc: httpx.HTTPStatusError):
    return JSONResponse(status_code=502, content={"detail": "External API error"})

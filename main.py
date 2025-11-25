"""Main FastAPI application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import init_db
from app.api import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    init_db()
    yield


app = FastAPI(
    title="Mini-CRM",
    description="CRM for distributing leads between operators",
    lifespan=lifespan
)

app.include_router(router, prefix="/api", tags=["crm"])


@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Mini-CRM API", "docs": "/docs"}


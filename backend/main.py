from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

# Import all models so SQLAlchemy knows them before create_all
import app.models  # noqa: F401


app = FastAPI(
    title=settings.APP_NAME
)


@app.on_event("startup")
def create_missing_tables():
    Base.metadata.create_all(
        bind=engine,
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX
)

app.mount(
    "/media",
    StaticFiles(directory="media"),
    name="media",
)
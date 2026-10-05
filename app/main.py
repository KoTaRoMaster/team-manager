import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api import router
from app.handlers import register_exception_handlers

logger = logging.getLogger('uvicorn')


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Начало работы приложения team-manager')
    yield
    logger.info('Завершение приложения team-manager')


app = FastAPI(lifespan=lifespan)

app.include_router(router)

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}

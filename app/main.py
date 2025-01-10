from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI,HTTPException, Request
from fastapi.responses import JSONResponse

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from redis import asyncio as aioredis

from app.users.router import router as router_users
from app.city.router import router as router_city
from app.recommendation.router import router as router_recommendation
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # при запуске
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    yield


app = FastAPI(
    title="Сервис рекомендаций",
    version="0.1.0",
    root_path="/api",
    lifespan=lifespan
)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        )

app.include_router(router_users)
app.include_router(router_city)
app.include_router(router_recommendation)
@cache()
async def get_cache():
    return 1


@app.get("/")
async def root():
    return {"message": "Привет, мир"}

@app.get("/healthcheck")
async def get_healthcheck():
    return "OK()"
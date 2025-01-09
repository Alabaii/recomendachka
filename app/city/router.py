from datetime import date
import json
import logging
from typing import Literal, Optional
from fastapi import APIRouter, HTTPException, Query,status
from pydantic import UUID4
from sqlalchemy import UUID
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from app.city.dao import CityDAO

router = APIRouter(
    prefix="/city",
    tags=["Города"],
)

@router.get("/get_or_create", summary="Get user by id")
async def get_or_create(
    city: str
):
    await CityDAO.initialize_cache()
    """
    Возвращает запись из таблицы city по city. 
    Если запись не найдена, ни в кэше, ни в базе,
    то создает новую запись.
    Параметры:
        city: str — город.
    """
    result = await CityDAO.get_or_create_city(city)
    print(result)
    decoded_data = json.loads(result)
    return decoded_data
    

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
from app.city.schemas import SCity

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse



router = APIRouter(
    prefix="/city",
    tags=["Города"],
)

@router.get("/get_or_create", summary="Get city or create new")
async def get_or_create(
    city: str
)-> SCity:
    await CityDAO.initialize_cache()
    """
    Возвращает запись из таблицы city по city. 
    Если запись не найдена, ни в кэше, ни в базе,
    то создает новую запись.
    Параметры:
        city: str — город.
    """
    try:
        result = await CityDAO.get_or_create_city(city)
        
        # Просто возвращаем результат как уже подготовленный объект
        return result # Десериализация строки JSON в объект Python
        
    except HTTPException as exc:
        # Возвращаем исключение с нужным статусом и сообщением об ошибке
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@router.get("/calculate_geo_similarity", summary="Get geo similarity")
async def geo_similarity(
    city1 :str,
    city2 :str)-> float:
    result = await CityDAO.calculate_geo_similarity(city1,city2)
    return result
    

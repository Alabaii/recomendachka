import asyncio
from datetime import timedelta
import json
import uuid
from fastapi import HTTPException
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
# from sentence_transformers import SentenceTransformer, util
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
import time


from dataclasses import asdict

from redis import asyncio as aioredis
from sqlalchemy import insert, select
from app.city.models import City
from app.dao.base import BaseDAO

from app.database import async_session_maker
import logging

logging.basicConfig(level=logging.INFO)
geolocator = Nominatim(user_agent="geoapi")

class CityDAO(BaseDAO):
    model = City

    @staticmethod
    async def initialize_cache(cls):
        """Инициализация кэша из базы данных."""
        redis_backend = FastAPICache.get_backend()
        if not isinstance(redis_backend, RedisBackend):
            raise RuntimeError("Кэш-бекенд должен быть RedisBackend")

        async with async_session_maker() as session:
            result = await session.execute(select(City))
            cities = result.scalars().all()

            for city in cities:
                city_dict_serializable = cls.prepare_city_dict(city)
                city_json = json.dumps(city_dict_serializable)
                await redis_backend.set(f"city:{city.name}", city_json, expire=604800)

    @staticmethod
    def prepare_city_dict(city: City) -> dict:
        """Подготовка словаря с данными о городе для сериализации."""
        city_dict = {
            "id": city.id,
            "name": city.name,
            "country": city.country,
            "latitude": city.latitude,
            "longitude": city.longitude,
        }
        return {key: str(value) if isinstance(value, uuid.UUID) else value for key, value in city_dict.items()}

    @classmethod
    async def get_or_create_city(cls, city_name: str):
        """Fetch city info from cache, database, or geolocator."""
        redis_backend = FastAPICache.get_backend()
        logging.info(f"Пытаемся найти город: {city_name}")

        # Проверяем кэш Redis
        cached_city = await redis_backend.get(f"city:{city_name}")
        if cached_city:
            return json.loads(cached_city)

        # Если нет в кэше, выполняем запрос к базе данных
        logging.info(f"Запрос к базе данных для города: {city_name}")
        async with async_session_maker() as session:
            result = await session.execute(select(cls.model).where(cls.model.name == city_name))
            city = result.scalars().first()

            if not city:
                logging.info(f"Город не найден, создаем новый: {city_name}")
                # Используем геолокатор, если город не найден
                await asyncio.sleep(6)
                location = geolocator.geocode(city_name)
                if not location:
                    raise HTTPException(status_code=404, detail="City not found")

                city_data = {
                    "name": city_name,
                    "country": location.address.split(",")[-1].strip(),
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                }

                logging.info(f"Вставляем новый город в базу данных: {city_name}")
                query = insert(cls.model).values(city_data).returning(cls.model)
                result = await session.execute(query)
                await session.commit()
                city = result.scalar_one()
            logging.info(f"Город найден: {city_name}")

            # Подготовим данные города
            city_dict_serializable = cls.prepare_city_dict(city)
            city_json = json.dumps(city_dict_serializable)

            # Запишем город в кэш и вернем данные
            await redis_backend.set(f"city:{city_name}", city_json, expire=604800)
            return json.loads(city_json)

    @classmethod
    async def calculate_geo_similarity(cls, city1: str, city2: str) -> float:
        """Асинхронно вычисляет географическое сходство между двумя городами."""
        city1_info = await cls.get_or_create_city(city1)
        city2_info = await cls.get_or_create_city(city2)

        if not city1_info or not city2_info:
            return 0.0

        distance = geodesic(
            (city1_info["latitude"], city1_info["longitude"]),
            (city2_info["latitude"], city2_info["longitude"])
        ).kilometers

        if distance < 50:
            return 1.0
        elif distance < 500:
            return 0.5
        elif city1_info["country"] == city2_info["country"]:
            return 0.8
        else:
            return 0.0
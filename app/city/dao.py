from datetime import timedelta
import json
import uuid
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
# from sentence_transformers import SentenceTransformer, util
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from dataclasses import asdict

from redis import asyncio as aioredis
from sqlalchemy import insert, select
from app.city.models import City
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao.base import BaseDAO

from app.database import async_session_maker

geolocator = Nominatim(user_agent="geoapi")

class CityDAO(BaseDAO):
    model = City
    @staticmethod
    async def initialize_cache():
        """Инициализация кэша из базы данных."""
        redis_backend = FastAPICache.get_backend()  # Получаем текущий бекенд
        if not isinstance(redis_backend, RedisBackend):
            raise RuntimeError("Кэш-бекенд должен быть RedisBackend")

        async with async_session_maker() as session:
            result = await session.execute(select(City))
            cities = result.scalars().all()

            for city in cities:
                city_dict = {
                            "id": city.id,
                            "name": city.name,
                            "country": city.country,
                            "latitude": city.latitude,
                            "longitude": city.longitude,
                            }
                city_dict_serializable = {
                                        key: (str(value) if isinstance(value, uuid.UUID) else value)
                                        for key, value in city_dict.items()
                                        }
                # Установка значений в Redis
                ttl = 604800
                city_json = json.dumps(city_dict_serializable)
                await redis_backend.set(
                    f"city:{city.name}",
                    city_json,
                    expire=ttl,
                    )


    @classmethod
    @cache(expire=604800)
    async def get_or_create_city(cls, city_name: str):
        """Fetch city info from cache, database, or geolocator."""
        # Check Redis cache
        redis_backend = FastAPICache.get_backend()
        cached_city = await redis_backend.get(f"city:{city_name}")
        if cached_city:
            return cached_city

        # Query database
        async with async_session_maker() as session:
            result = await session.execute(select(cls.model).where(cls.model.name == city_name))
            city = result.scalar_one_or_none()

            if not city:
                # Use geolocator if not found
                location = geolocator.geocode(city_name)
                if not location:
                    return None

                # Extract country and create city object
                city_data = {
                    "name": city_name,
                    "country": location.address.split(",")[-1].strip(),
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                }
                query = insert(cls.model).values(city_data).returning(cls.model)

                # Insert new city into database
                result = await session.execute(query)
                await session.commit()
                city = result.scalar_one()

            # Prepare the city data
            city_dict = {
                'id': city.id,
                'name': city.name,
                'country': city.country,
                'latitude': city.latitude,
                'longitude': city.longitude
            }
            
            # Ensure all values are serializable
            city_dict_serializable = {
                key: (str(value) if isinstance(value, uuid.UUID) else value)
                for key, value in city_dict.items()
            }
            
            # Serialize the city dict to JSON string
            city_json = json.dumps(city_dict_serializable)

            # Write city to cache and return as JSON
            await redis_backend.set(f"city:{city_name}", city_json, expire=604800)
            return city_json
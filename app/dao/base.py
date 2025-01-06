from datetime import datetime
from fastapi import HTTPException,status
from sqlalchemy import delete, insert, select
from sqlalchemy.exc import SQLAlchemyError

from app.database import async_session_maker
# from app.logger import logger

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO) 
class BaseDAO:
    model = None


    @classmethod
    async def find_by_id(cls,id: str):
        async with async_session_maker()  as session:
            result = await session.execute(select(cls.model).where(cls.model.id == id))
            return result.scalar_one_or_none() 


    @classmethod
    async def find_all(cls, offset: int = 0, limit: int = 10, **filter_by):
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .filter_by(**filter_by)  # Используем фильтры
                .offset(offset)         # Добавляем пагинацию
                .limit(limit)
            )
            result = await session.execute(query)
            return result.scalars().all()
    
    @classmethod
    async def add(cls, **data):
        try:
            # Преобразуем дату в naive, если она имеет временную зону
            if isinstance(data.get('date'), datetime) and data['date'].tzinfo:
                data['date'] = data['date'].replace(tzinfo=None)
            
            query = insert(cls.model).values(**data).returning(cls.model.id)
            async with async_session_maker() as session:
                result = await session.execute(query)
                await session.commit()
                return result.mappings().first()
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database Error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal Server Error: {str(e)}"
            )

    @classmethod
    async def delete(cls, **filter_by):
        async with async_session_maker() as session:  # Используем ваш сессионный менеджер
            # Находим записи, которые будут удалены
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            rows = result.scalars().all()

            if not rows:
                return None  # Возвращаем None, если записи не найдены

            # Если записи найдены, выполняем их удаление
            delete_query = delete(cls.model).filter_by(**filter_by)
            await session.execute(delete_query)
            await session.commit()
            return len(rows)

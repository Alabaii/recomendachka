from datetime import date
import logging
from typing import Literal, Optional
from fastapi import APIRouter, HTTPException, Query,status
from pydantic import UUID4
from sqlalchemy import UUID
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from app.users.dao import UsersDAO
from app.users.schemas import UserCreate, SUsers


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)



@router.get("/all", summary="Get all users", response_model=list[SUsers])
async def get_users(
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
    limit: int = Query(10, ge=1, le=100, description="Количество записей для возврата"),
    first_name: str | None = Query(None, description="Фильтр по имени"),
    surname: str | None = Query(None, description="Фильтр по фамилии"),
    birthday: date | None = Query(None, description="Фильтр по дате рождения"),
    gender: Literal["man","woman"] | None = Query(None, description="Фильтр по полу"),
    city: str | None = Query(None, description="Фильтр по городу"),
    profession : str | None = Query(None, description="Фильтр по профессии"),
):
    """
    Возвращает записи из таблицы users с возможностью фильтрации.
    Параметры:
        offset: int — смещение для пагинации.
        limit: int — количество записей для возврата.
        first_name: str — имя (необязателен).
        surname: str — фамилия (необязателен).
        birthday: date — дата рождения (необязателен).
        genger : Literal["man","woman"] — пол (необязателен).
        city: str — город (необязателен).
        profession: str — профессия (необязателен).
    """
    filters = {}
    if first_name:
        filters['first_name'] = first_name          
    if surname: 
        filters['surname'] = surname
    if birthday:
        filters['birthday'] = birthday
    if gender:
        filters['gender'] = gender
    if city:
        filters['city'] = city
    if profession:
        filters['profession'] = profession

    result = await UsersDAO.find_all(offset=offset, limit=limit, **filters)
    if not result:
        raise HTTPException(status_code=404, detail="Users not found")
    return result

@router.get("/find_by_id/{id}", summary="Get user by id")
@cache(expire=60)
async def get_users_by_id(id)-> SUsers:
    """
    Возвращает запись из таблицы users по ID.
    """
    result = await UsersDAO.find_by_id(id)
    if not result:
        raise HTTPException(status_code=404, detail="Users not found")
    return result


@router.post("/add", summary="Add a new user", status_code=201)
async def add_user(user: UserCreate):
    """
    Добаляет запись в таблицу users.
    поля:
        first_name: str - имя.
        surname: str - фамилия.
        date_created: date - дата создания.
        description: str - описание.
        birthday: date - дата рождения.
        gender: Literal["man","woman"] - пол.
        city: str - город.
        profession : str - профессия.
        experience : float - опыт.
    """
    data = user.dict()  # Преобразуем Pydantic модель в обычный dict
    try:
        result = await UsersDAO.add(**data)
        if result:
            return {"message": "Fault added successfully", "id": result["id"]}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add fault to the database"
            )
    except HTTPException as e:
        # Поймаем ошибку, сгенерированную в DAO (например, ошибка базы данных)
        raise e
    except Exception as e:
        # Обрабатываем все другие непредвиденные ошибки
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error occurred: {str(e)}"
        )
    

@router.delete("/")
async def delete_users(
    id: Optional[UUID4] = Query(None, description="Удаление по ID"), 
    first_name: str | None = Query(None, description="Удаление по имени"),
    surname: str | None = Query(None, description="Удаление по фамилии"),
    birthday: date | None = Query(None, description="Удаление по дате рождения"),
    gender: Literal["man","woman"] | None = Query(None, description="Удаление по полу"),
    city: str | None = Query(None, description="Удаление по городу"),
    profession : str | None = Query(None, description="Удаление по профессии"),):
    """
    Удаляет запись из таблицы users по фильтрам, переданным через query параметры.
    Параметры:
        id: UUID — идентификатор записи (необязателен).
        first_name: str — имя (необязателен).
        surname: str — фамилия (необязателен).
        birthday: date — дата рождения (необязателен).
        genger : Literal["man","woman"] — пол (необязателен).
        city: str — город (необязателен).
        profession: str — профессия (необязателен).
    """
    filter_params = {}
    
    if id:
        filter_params['id'] = id
    if first_name:  
        filter_params['first_name'] = first_name
    if surname:
        filter_params['surname'] = surname
    if birthday:
        filter_params['birthday'] = birthday
    if gender:
        filter_params['gender'] = gender
    if city:
        filter_params['city'] = city
    if profession:
        filter_params['profession'] = profession

    logger.info(f"Attempting to delete with filters: {filter_params}")
    
    try:
        
        result = await UsersDAO.delete(**filter_params)

        if result is None:  
            logger.error(f"No records found for filters: {filter_params}")
            raise HTTPException(status_code=404, detail="Record not found")
        
        logger.info(f"Deleted {result} record(s) with filters: {filter_params}")
        return {"status": "success", "message": f"{result} record(s) deleted successfully"}

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
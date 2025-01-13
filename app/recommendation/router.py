from datetime import date
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query,status
from sqlalchemy import delete, select

from app.recommendation.dao import RecommendationDAO
from app.recommendation.models import Recommendation
from app.recommendation.schemas import SUser
from app.database import async_session_maker
from app.users.models import Users


router = APIRouter(    
    prefix="/recommendation",
    tags=["Рекомендации"],
)

@router.get("/calculute_age", summary="Calculate age")
async def calculate_age(
    birthday: date
):
    """
    Возвращает возраст пользователя по дате рождения.
    Параметры:
        birthday: date — дата рождения.
    """
    return await RecommendationDAO.calculate_age(birthday)

@router.get("/normalize_experience", summary="Normalize experience")
async def normalize(
    experience: float
    )-> float:
    """
    Вовзращает нормализованное значение опыта
    Параметры:
        experience: float - опыт работы.
    """

    return await RecommendationDAO.normalize_experience(experience)

@router.get("/calculate_profession_similarity", summary="Calculate profession similarity")
async def profession_similarity(
    profession1: str, profession2: str
    ):
    """
    Вовзращает нормализованное значение опыта
    Параметры:
        experience: float - опыт работы.
    """

    return await RecommendationDAO.calculate_profession_similarity(profession1, profession2)

@router.get("/detect_language_and_prepare", summary="Detect language and prepare")
async def detect_language_and_prepare(
    description: str
    ):
    """
    Возвращает текст на английском языке
    Параметры:
        description: str - описание.
    """

    return await RecommendationDAO.detect_language_and_prepare(description)
@router.get("/calculate_description_similarity", summary="Calculate description similarity")
async def calculate_description_similarity(
    description1: str, description2: str
    ):
    """
    Возвращает сходство между описаниями
    Параметры:
        description1: str - описание 1.
        description2: str - описание 2.
    """

    return await RecommendationDAO.calculate_description_similarity(description1, description2)

@router.post("/calculate_similarity", summary="Calculate similarity")
async def calculate_similarity(
    user1: SUser, user2: SUser
    ):
    """
    Возвращает сходство между пользователями
    Параметры:
        user1: SUser - пользователь 1.
        user2: SUser - пользователь 2.
    """
    result = await RecommendationDAO.calculate_similarity(user1, user2)
    return result

@router.get("/recommendations/{user_id}")
async def get_recommendations(user_id: UUID):
    
    async with async_session_maker() as session:
        target_user = await session.get(Users, user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")

        result = await session.execute(
            select(Users).where(Users.id != user_id)
        )
        all_users = result.scalars().all()

        recommendations = await RecommendationDAO.calculate_similarity_for_all(target_user, all_users, session)
        recommendations.sort(key=lambda x: x["similarity"], reverse=True)
        return recommendations[:10]
@router.post("/update_recommendations/{user_id}")
async def update_recommendations_for_user(user_id: UUID)-> dict:
    async with async_session_maker() as session:
        target_user = await session.get(Users, user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")

        result = await session.execute(
            select(Users).where(Users.id != user_id)
        )
        all_users = result.scalars().all()

        recommendations = await RecommendationDAO.calculate_similarity_for_all(target_user, all_users, session)

        await session.execute(
            delete(Recommendation).where(Recommendation.user_id == user_id)
        )
        session.add_all(
            [Recommendation(user_id=user_id, recommended_user_id=r["user_id"], similarity=r["similarity"]) for r in recommendations]
        )
        await session.commit()
        return {"status": "updated"}

@router.get("/recommendations_from_database/{user_id}")
async def get_top_recommendations(user_id: UUID):
    try:
        async with async_session_maker() as session:
            result = await session.execute(
                select(Recommendation)
                .where(Recommendation.user_id == user_id)
                .order_by(Recommendation.similarity.desc())  
            )
            
            recommendations = result.scalars().all()

            if not recommendations:
                raise HTTPException(status_code=404, detail="No recommendations found for this user")

            # Ограничиваем результат первыми 5 рекомендациями
            top_recommendations = recommendations[:5]

            return top_recommendations

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {e}")
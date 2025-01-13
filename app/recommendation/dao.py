import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime
import math

from fastapi import HTTPException

from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.city.dao import CityDAO
from app.recommendation.models import Recommendation


from langdetect import detect
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from aiogoogletrans import Translator


# Weights
weights = {
    "city": 0.2,
    "profession": 0.3,
    "age": 0.2,
    "experience": 0.1,
    "description": 0.2,
}


profession_similarity_matrix = {
    ("Software Engineer", "Software Engineer"): 1.0,
    ("Software Engineer", "Data Scientist"): 0.8,
    ("Software Engineer", "Project Manager"): 0.5,
    ("Data Scientist", "Data Scientist"): 1.0,
    ("Data Scientist", "Project Manager"): 0.6,
    ("Project Manager", "Project Manager"): 1.0,
}


class RecommendationDAO(BaseDAO):
    model = Recommendation
    
    @classmethod
    async def calculate_age(cls, birthday: datetime) -> int:
        today = datetime.today()
        return today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
    

    
    @classmethod
    async def normalize_experience(cls, experience: float, mean: float = 5.0, std_dev: float = 2.0) -> float:
        """Normalize experience based on mean and standard deviation."""
        # Проверка входных данных для отладки
        print(f"experience: {experience}, type: {type(experience)}")
        print(f"mean: {mean}, type: {type(mean)}")
        print(f"std_dev: {std_dev}, type: {type(std_dev)}")
        
        # Нормализация
        """Normalize experience using a sigmoid function."""
        z_score = (experience - mean) / std_dev
        return 1 / (1 + math.exp(-z_score))
    

    @classmethod
    async def calculate_profession_similarity(cls,profession1: str, profession2: str) -> float:
        """
        Вычисление сходства между профессиями на основе матрицы сходства.
        """
        if profession1 == profession2:
            return 1.0

        # Пытаемся найти сходство в матрице
        return profession_similarity_matrix.get(
            (profession1, profession2),
            profession_similarity_matrix.get((profession2, profession1), 0.0)
        )
    
    @classmethod
    async def translate_to_english(cls,text: str) -> str:
        """Translate text to English."""
        print(f"Translating text to English: {text}")
        translator = Translator()
        try:
            translation = await translator.translate(text, dest="en")
            print(f"Translated text: {translation.text}")
            return translation.text
        except Exception:
            return ""
        
    @classmethod
    async def detect_language_and_prepare(cls, description: str) -> str:
        """Detect language and prepare description for TF-IDF."""
        if not description or len(description.strip()) < 3:  # Текст пустой или слишком короткий
            print("Description is empty or too short to detect language.")
            return ""

        try:
            lang = detect(description)
            print(f"Detected language: {lang}")
            if lang not in ["en"]:
                return await cls.translate_to_english(description)
        except Exception as e:
            print(f"Error detecting or translating language: {e}")
            return ""
        
        return description
        
    @classmethod
    async def calculate_description_similarity(cls, description1: str, description2: str) -> float:
        """Calculate similarity between two descriptions using TF-IDF and cosine similarity."""
        # Translate descriptions to English
        
        description1_en = await cls.detect_language_and_prepare(description1)
        description2_en = await cls.detect_language_and_prepare(description2)
        if not description1_en or not description2_en:
            print("One or both descriptions are empty after preprocessing.")
            return 0.0
        # Combine descriptions
        combined_description = f"{description1_en} {description2_en}"
                # If the combined description is empty, return 0 similarity
        if not combined_description.strip():
            print("Combined description is empty.")
            return 0.0
        # Calculate TF-IDF
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform([description1_en, description2_en, combined_description])
        
        # Calculate cosine similarity
        cosine_sim = cosine_similarity(tfidf_matrix)
        
        return cosine_sim[0, 1]
    @classmethod
    async def calculate_similarity(cls,user1, user2):
        """
        Вычисление сходства между двумя пользователями.
        """
        city_similarity = await CityDAO.calculate_geo_similarity(user1.city, user2.city)
        profession_similarity = await cls.calculate_profession_similarity(user1.profession, user2.profession)
        age_similarity = 1 - abs( await cls.calculate_age(user1.birthday) - await cls.calculate_age(user2.birthday)) / 100
        experience_similarity = 1 - abs( await cls.normalize_experience(user1.experience) - await cls.normalize_experience(user2.experience))

        description_similarity = await cls.calculate_description_similarity(user1.description, user2.description)

        return (
            weights["city"] * city_similarity+
            weights["profession"] * profession_similarity+
            weights["age"] * age_similarity+
            weights["experience"] * experience_similarity+
            weights["description"] * description_similarity
        )
    @classmethod
    async def calculate_similarity_for_all(cls,target_user, all_users, session: AsyncSession):
        semaphore = asyncio.Semaphore(10)
        async def worker(user):
            async with semaphore:
                similarity = await cls.calculate_similarity(target_user, user)
                return {
                    "user_id": user.id,
                    "similarity": similarity
                }

        tasks = [worker(user) for user in all_users]
        results = await asyncio.gather(*tasks)
        return results
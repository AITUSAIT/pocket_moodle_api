import asyncio
import logging
from typing import Any

from modules.database.db import DB
from modules.database.models import Grade

logger = logging.getLogger("uvicorn.error")


class GradeDB(DB):
    pending_queries_grades: list[tuple[str, tuple[Any, ...]]] = []
    commit_interval: float = 5.0
    _grades_cache: dict[int, dict[int, dict[str, Grade]]] = {}

    @classmethod
    async def get_grades(cls, user_id, course_id: int) -> dict[str, Grade]:
        if user_id in cls._grades_cache and course_id in cls._grades_cache[user_id]:
            return cls._grades_cache[user_id][course_id]

        async with cls.pool.acquire() as connection:
            rows = await connection.fetch(
                "SELECT grade_id, name, percentage FROM grades WHERE user_id = $1 and course_id = $2",
                user_id,
                course_id,
            )
            grades = {str(row[0]): Grade(**row) for row in rows}

            if user_id not in cls._grades_cache:
                cls._grades_cache[user_id] = {}
            cls._grades_cache[user_id][course_id] = grades

            return grades

    @classmethod
    async def set_grade(cls, user_id: int, course_id: int, grade: Grade):
        # Cache the new grade
        if user_id not in cls._grades_cache:
            await cls.get_grades(user_id, course_id)
        if course_id not in cls._grades_cache[user_id]:
            await cls.get_grades(user_id, course_id)

        cls._grades_cache[user_id][course_id][str(grade.grade_id)] = grade

        query = """
        INSERT INTO
            grades (course_id, grade_id, user_id, name, percentage)
        VALUES ($1, $2, $3, $4, $5)
        """
        cls.add_query(query, course_id, grade.grade_id, user_id, grade.name, grade.percentage)

    @classmethod
    async def update_grade(cls, user_id: int, course_id: int, grade: Grade):
        # Update the cached grade
        if user_id not in cls._grades_cache:
            await cls.get_grades(user_id, course_id)
        if course_id not in cls._grades_cache[user_id]:
            await cls.get_grades(user_id, course_id)

        cls._grades_cache[user_id][course_id][str(grade.grade_id)] = grade

        query = "UPDATE grades SET percentage = $1, name = $2 WHERE course_id = $3 and grade_id = $4 and user_id = $5"
        cls.add_query(query, grade.percentage, grade.name, course_id, grade.grade_id, user_id)

    @classmethod
    def add_query(cls, query, *params):
        cls.pending_queries_grades.append((query, params))

    @classmethod
    async def commit(cls):
        if not cls.pending_queries_grades:
            return  # No pending queries to commit

        async with cls.pool.acquire() as connection:
            async with connection.transaction():
                for query, params in cls.pending_queries_grades:
                    try:
                        await connection.execute(query, *params)
                    except Exception:
                        logger.error(f"{query=} {params=}", exc_info=True)
        cls.pending_queries_grades.clear()

    @classmethod
    async def commit_in_background(cls):
        """Periodically commit pending queries in the background."""
        while True:
            await asyncio.sleep(cls.commit_interval)
            await cls.commit()

    @classmethod
    async def start_commit_thread(cls):
        """Starts the commit thread when the application begins."""
        asyncio.create_task(cls.commit_in_background())

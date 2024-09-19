import asyncio
import logging
from typing import Any

from modules.database.db import DB
from modules.database.models import Course

logger = logging.getLogger("uvicorn.error")


class CourseDB(DB):
    pending_queries_courses: list[tuple[str, tuple[Any, ...]]] = []
    commit_interval: float = 5.0
    _courses_cache: dict[int, dict[str, Course]] = {}

    @classmethod
    async def is_ready_courses(cls, user_id: int) -> bool:
        async with cls.pool.acquire() as connection:
            course_count = await connection.fetchval(
                "SELECT COUNT(*) FROM courses INNER JOIN courses_user_pair cp ON cp.user_id = $1", user_id
            )
            return course_count > 0

    @classmethod
    async def get_courses(cls, user_id: int, is_active: bool | None = None) -> dict[str, Course]:
        if user_id in cls._courses_cache:
            if is_active is None:
                return cls._courses_cache[user_id]
            return {
                course_id: course
                for course_id, course in cls._courses_cache[user_id].items()
                if course.active == is_active
            }

        async with cls.pool.acquire() as connection:
            rows = await connection.fetch(
                """
            SELECT
                c.course_id, c.name, cp.active
            FROM
                courses c
            INNER JOIN
                courses_user_pair cp ON c.course_id = cp.course_id
            WHERE
                cp.user_id = $1
                AND (cp.active = $2 OR $2 IS NULL);
            """,
                user_id,
                is_active,
            )

            courses = {
                str(course[0]): Course(
                    course_id=course[0],
                    name=course[1],
                    active=course[2],
                )
                for course in rows
            }

            # Update the cache
            cls._courses_cache[user_id] = courses

            return courses

    @classmethod
    async def get_course(cls, user_id: int, course_id: int) -> Course:
        if user_id in cls._courses_cache:
            if course_id in cls._courses_cache:
                return cls._courses_cache[user_id][str(course_id)]

        async with cls.pool.acquire() as connection:
            row = await connection.fetchrow(
                """
            SELECT
                c.course_id, c.name, cp.active
            FROM
                courses c
            INNER JOIN
                courses_user_pair cp ON c.course_id = cp.course_id
            WHERE
                cp.user_id = $1
                AND cp.course_id = $2
            """,
                user_id,
                course_id,
            )

            course = Course(
                course_id=row[0],
                name=row[1],
                active=row[2],
            )

            # Update the cache
            cls._courses_cache[user_id][str(course_id)] = course
            asyncio.create_task(cls.get_courses(user_id))

            return course

    @classmethod
    async def link_user_with_course(cls, user_id: int, course: Course):
        if user_id not in cls._courses_cache:
            await cls.get_courses(user_id)
        if str(course.course_id) not in cls._courses_cache[user_id]:
            await cls.get_courses(user_id)

        cls._courses_cache[user_id][str(course.course_id)] = course

        query = """
        INSERT INTO
            courses (course_id, name)
        VALUES ($1, $2)
        ON CONFLICT
            (course_id)
        DO NOTHING;
        """
        cls.add_query(query, course.course_id, course.name)
        cls.set_course_user_pair(user_id=user_id, course_id=course.course_id, active=course.active)

    @classmethod
    def set_course_user_pair(cls, user_id: int, course_id: int, active: bool):
        query = """
        INSERT INTO
            courses_user_pair (user_id, course_id, active)
        VALUES ($1, $2, $3)
        """
        cls.add_query(query, user_id, course_id, active)

    @classmethod
    async def update_user_course_link(cls, user_id: int, course: Course):
        if user_id not in cls._courses_cache:
            await cls.get_courses(user_id)
        if str(course.course_id) not in cls._courses_cache[user_id]:
            await cls.get_courses(user_id)

        cls._courses_cache[user_id][str(course.course_id)] = course

        query = "UPDATE courses_user_pair SET active = $1 WHERE course_id = $2 and user_id = $3"
        cls.add_query(query, course.active, course.course_id, user_id)

    @classmethod
    def add_query(cls, query: str, *args: Any):
        cls.pending_queries_courses.append((query, args))

    @classmethod
    async def commit(cls):
        if not cls.pending_queries_courses:
            return  # No pending queries to commit

        async with cls.pool.acquire() as connection:
            async with connection.transaction():
                for query, params in cls.pending_queries_courses:
                    try:
                        await connection.execute(query, *params)
                    except Exception:
                        logger.error(f"{query=} {params=}", exc_info=True)
        cls.pending_queries_courses.clear()

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

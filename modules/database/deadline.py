import asyncio
import json
import logging
from datetime import datetime
from typing import Any

from modules.database.db import DB
from modules.database.models import Course, Deadline

logger = logging.getLogger("uvicorn.error")


class DeadlineDB(DB):
    pending_queries_deadlines: list[tuple[str, tuple[Any, ...]]] = []
    commit_interval: float = 5.0
    _deadlines_cache: dict[int, dict[int, dict[str, Deadline]]] = {}

    @classmethod
    async def get_deadlines(cls, user_id, course_id: int) -> dict[str, Deadline]:
        if user_id in cls._deadlines_cache and course_id in cls._deadlines_cache[user_id]:
            return cls._deadlines_cache[user_id][course_id]

        async with cls.pool.acquire() as connection:
            rows = await connection.fetch(
                """
            SELECT
                d.id, d.assign_id, d.name, dp.due, dp.graded, dp.submitted, dp.status
            FROM
                deadlines d
            INNER JOIN
                deadlines_user_pair dp ON dp.id = d.id
            WHERE
                dp.user_id = $1 and d.course_id = $2
            """,
                user_id,
                course_id,
            )

            deadlines = {
                str(row[0]): Deadline(
                    id=row[0],
                    assign_id=row[1],
                    name=row[2],
                    due=row[3],
                    graded=row[4],
                    submitted=row[5],
                    status=json.loads(row[6]),
                )
                for row in rows
            }

            # Update the cache
            if user_id not in cls._deadlines_cache:
                cls._deadlines_cache[user_id] = {}
            cls._deadlines_cache[user_id][course_id] = deadlines

            return deadlines

    @classmethod
    def link_user_with_deadline(cls, user_id: int, course: Course, deadline: Deadline):
        # Cache the new deadline
        if user_id in cls._deadlines_cache:
            if course.course_id in cls._deadlines_cache[user_id]:
                cls._deadlines_cache[user_id][course.course_id][str(deadline.id)] = deadline

        query = """
        INSERT INTO
            deadlines (id, assign_id, name, course_id)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT
            (id, assign_id)
        DO NOTHING;
        """
        cls.add_query(query, deadline.id, deadline.assign_id, deadline.name, course.course_id)
        cls.set_user_deadline_link(
            user_id=user_id,
            deadline_id=deadline.id,
            due=deadline.due,
            submitted=deadline.submitted,
            graded=deadline.graded,
            status=deadline.status,
        )

    @classmethod
    def set_user_deadline_link(
        cls, user_id: int, deadline_id: int, due: datetime, submitted: bool, graded: bool, status: dict
    ):
        query = """
        INSERT INTO
            deadlines_user_pair (user_id, id, submitted, graded, status, due)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (user_id, id)
        DO UPDATE SET
            submitted = EXCLUDED.submitted,
            graded = EXCLUDED.graded,
            status = EXCLUDED.status,
            due = EXCLUDED.due
        """
        cls.add_query(query, user_id, deadline_id, submitted, graded, json.dumps(status), due)

    @classmethod
    def update_user_deadline_link(cls, user_id: int, course: Course, deadline: Deadline):
        # Update the cached deadline
        if user_id in cls._deadlines_cache:
            if course.course_id in cls._deadlines_cache[user_id]:
                cls._deadlines_cache[user_id][course.course_id][str(deadline.id)] = deadline

        query = """
        UPDATE
            deadlines
        SET
            name = $1
        WHERE
            id = $2;
        """
        cls.add_query(query, deadline.name, deadline.id)
        query = """
        UPDATE
            deadlines_user_pair
        SET
            submitted = $1, graded = $2, status = $3, due = $4
        WHERE
            id = $5 and user_id = $6;
        """
        cls.add_query(
            query, deadline.submitted, deadline.graded, json.dumps(deadline.status), deadline.due, deadline.id, user_id
        )

    @classmethod
    def add_query(cls, query: str, *args: Any):
        cls.pending_queries_deadlines.append((query, args))

    @classmethod
    async def commit(cls):
        if not cls.pending_queries_deadlines:
            return  # No pending queries to commit

        async with cls.pool.acquire() as connection:
            async with connection.transaction():
                for query, params in cls.pending_queries_deadlines:
                    try:
                        await connection.execute(query, *params)
                    except Exception:
                        logger.error(f"{query=} {params=}", exc_info=True)
        cls.pending_queries_deadlines.clear()

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

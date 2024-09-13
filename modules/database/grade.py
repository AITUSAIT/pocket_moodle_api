from modules.database.db import DB
from modules.database.models import Grade


class GradeDB(DB):
    @classmethod
    async def get_grades(cls, user_id, course_id: int) -> dict[str, Grade]:
        async with cls.pool.acquire() as connection:
            rows = await connection.fetch(
                "SELECT grade_id, name, percentage FROM grades WHERE user_id = $1 and course_id = $2",
                user_id,
                course_id,
            )
            return {str(row[0]): Grade(**row) for row in rows}

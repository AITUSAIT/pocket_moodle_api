from datetime import datetime

from modules.database.course import CourseDB
from modules.database.db import DB
from modules.database.deadline import DeadlineDB
from modules.database.grade import GradeDB
from modules.database.models import User


class UserDB(DB):
    @classmethod
    async def create_user(cls, user_id: int) -> None:
        user_data = (user_id, None, datetime.now())

        notification_data = [
            (user_id, True, True, False, False),
        ]

        settings_app_data = [
            (user_id, False, True, True),
        ]

        settings_bot_data = [
            (user_id, True, True, True),
        ]

        async with cls.pool.acquire() as connection:
            async with connection.transaction():
                await connection.executemany(
                    "INSERT INTO users (user_id, api_token, register_date) VALUES ($1, $2, $3);", [user_data]
                )
                await connection.executemany(
                    "INSERT INTO user_notification (user_id, status, is_newbie_requested, is_update_requested, is_end_date) VALUES ($1, $2, $3, $4, $5);",
                    notification_data,
                )
                await connection.executemany(
                    "INSERT INTO user_settings_app (user_id, status, notification_grade, notification_deadline) VALUES ($1, $2, $3, $4);",
                    settings_app_data,
                )
                await connection.executemany(
                    "INSERT INTO user_settings_bot (user_id, status, notification_grade, notification_deadline) VALUES ($1, $2, $3, $4);",
                    settings_bot_data,
                )

    @classmethod
    async def get_user(cls, user_id: int) -> User | None:
        async with cls.pool.acquire() as connection:
            user_data = await connection.fetchrow(
                "SELECT user_id, api_token, register_date, mail, last_active, moodle_id FROM users WHERE user_id = $1",
                user_id,
            )
            if not user_data:
                return None

            user_id = user_data[0]
            api_token = user_data[1]
            register_date = user_data[2]
            mail = user_data[3]
            last_active = user_data[4]
            moodle_id = user_data[5]

            user = User(
                user_id=user_id,
                api_token=api_token,
                register_date=register_date,
                mail=mail,
                last_active=last_active,
                is_admin=await cls.is_admin(user_id),
                is_manager=await cls.is_manager(user_id),
                moodle_id=moodle_id,
            )
            return user

    @classmethod
    async def get_users(cls) -> list[User]:
        async with cls.pool.acquire() as connection:
            users = await connection.fetch(
                "SELECT user_id, api_token, register_date, mail, last_active, moodle_id FROM users WHERE last_active > NOW() - INTERVAL '2 weeks'"
            )
            return [
                User(
                    user_id=user_data[0],
                    api_token=user_data[1],
                    register_date=user_data[2],
                    mail=user_data[3],
                    last_active=user_data[4],
                    is_admin=await cls.is_admin(user_data[0]),
                    is_manager=await cls.is_manager(user_data[0]),
                    moodle_id=user_data[5],
                )
                for user_data in users
            ]

    @classmethod
    async def register(cls, user_id: int, mail: str, api_token: str, moodle_id: int) -> None:
        async with cls.pool.acquire() as connection:
            async with connection.transaction():
                if user_id in CourseDB._courses_cache:
                    del CourseDB._courses_cache[user_id]  # pylint: disable=protected-access
                if user_id in GradeDB._grades_cache:
                    del GradeDB._grades_cache[user_id]  # pylint: disable=protected-access
                if user_id in DeadlineDB._deadlines_cache:
                    del DeadlineDB._deadlines_cache[user_id]  # pylint: disable=protected-access
                await connection.execute("DELETE FROM courses_user_pair WHERE user_id = $1;", user_id)
                await connection.execute("DELETE FROM deadlines_user_pair WHERE user_id = $1;", user_id)
                await connection.execute("DELETE FROM grades WHERE user_id = $1;", user_id)
                await connection.execute(
                    "UPDATE users SET api_token = $1, mail = $2, moodle_id = $3 WHERE user_id = $4",
                    api_token,
                    mail,
                    moodle_id,
                    user_id,
                )

    @classmethod
    async def set_active(cls, user_id: int) -> None:
        async with cls.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    "UPDATE users SET last_active = $1 WHERE user_id = $2;", datetime.now(), user_id
                )

    @classmethod
    async def set_moodle_id(cls, user_id: int, moodle_id: int) -> None:
        async with cls.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute("UPDATE users SET moodle_id = $1 WHERE user_id = $2;", moodle_id, user_id)

    @classmethod
    async def is_admin(cls, user_id: int) -> bool:
        async with cls.pool.acquire() as connection:
            admin_data = await connection.fetchrow("SELECT user_id, status FROM admin WHERE user_id = $1", user_id)
            return admin_data is not None and admin_data["status"] == "admin"

    @classmethod
    async def is_manager(cls, user_id: int) -> bool:
        async with cls.pool.acquire() as connection:
            manager_data = await connection.fetchrow("SELECT user_id, status FROM admin WHERE user_id = $1", user_id)
            return manager_data is not None and manager_data["status"] == "manager"

from modules.database.db import DB
from modules.database.models import SettingBot


class SettingsBotDB(DB):
    @classmethod
    async def get_settings(cls, user_id: int) -> SettingBot:
        async with cls.pool.acquire() as connection:
            _ = await connection.fetchrow(
                "SELECT status, notification_grade, notification_deadline FROM user_settings_bot WHERE user_id = $1",
                user_id,
            )
            return SettingBot(*_)

    @classmethod
    async def set_setting(cls, user_id: int, settings: SettingBot) -> None:
        async with cls.pool.acquire() as connection:
            await connection.execute(
                """
                UPDATE
                    user_settings_bot
                SET
                    status = $1,
                    notification_grade = $2,
                    notification_deadline = $3
                WHERE
                    user_id = $4
                """, settings.status, settings.notification_grade, settings.notification_deadline, user_id)

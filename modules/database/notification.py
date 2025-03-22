from modules.database.db import DB
from modules.database.models import NotificationStatus


class NotificationDB(DB):
    @classmethod
    async def get_notification_status(cls, user_id: int) -> NotificationStatus:
        async with cls.pool.acquire() as connection:
            row = await connection.fetchrow(
                "SELECT status, is_newbie_requested, is_update_requested, is_end_date, error_check_token FROM user_notification WHERE user_id = $1",
                user_id,
            )
            return NotificationStatus(**row)

    @classmethod
    async def set_notification_status(cls, user_id: int, notification_status: NotificationStatus) -> None:
        async with cls.pool.acquire() as connection:
            await connection.execute(
                """
                UPDATE
                    user_notification 
                SET
                    status = $1,
                    is_newbie_requested = $2,
                    is_update_requested = $3,
                    is_end_date = $4,
                    error_check_token = $5
                WHERE
                    user_id = $6
                """,
                notification_status.status,
                notification_status.is_newbie_requested,
                notification_status.is_update_requested,
                notification_status.is_end_date,
                notification_status.error_check_token,
                user_id,
            )

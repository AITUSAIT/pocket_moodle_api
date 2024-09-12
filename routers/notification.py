from fastapi import APIRouter, HTTPException, status

from modules.database.models import NotificationStatus
from modules.database.notification import NotificationDB

router = APIRouter(
    prefix="/notification",
    tags=["notification"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"desc": "Not found"}},
)


@router.get("/{user_id}")
async def get_notification_status(user_id: int) -> NotificationStatus:
    notification_status = await NotificationDB.get_notification_status(user_id=user_id)
    if not notification_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"no notification statuses found for user with {user_id}"
        )

    return notification_status

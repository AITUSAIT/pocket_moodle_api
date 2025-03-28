from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status

from modules.database.models import NotificationStatus
from modules.database.notification import NotificationDB

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"desc": "Not found"}},
)


@router.get("/{user_id}")
async def get_notification_status(
    user_id: Annotated[int, Path(title="The ID of the user to get notification status")]
) -> NotificationStatus:
    notification_status = await NotificationDB.get_notification_status(user_id=user_id)
    if not notification_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"no notification statuses found for user with {user_id}"
        )

    return notification_status


@router.post("/{user_id}")
async def set_notification_status(
    user_id: Annotated[int, Path(title="The ID of the user to set notification status")],
    notification_status: NotificationStatus,
):
    await NotificationDB.set_notification_status(user_id=user_id, notification_status=notification_status)

    return {"success": True, "desc": "Notification status updated!"}

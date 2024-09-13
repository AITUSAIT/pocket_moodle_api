from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status

from modules.database.models import SettingBot
from modules.database.settings_bot import SettingsBotDB

router = APIRouter(
    prefix="/settings_bot",
    tags=["settings_bot"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"desc": "Not found"}},
)


@router.get("/{user_id}")
async def get_bot_settings(user_id: Annotated[int, Path(title="The ID of the user to get bot settings")]) -> SettingBot:
    settings = await SettingsBotDB.get_settings(user_id=user_id)
    if not settings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"no settings found for user {user_id=}")

    return settings


@router.post("/{user_id}")
async def set_notification_status(
    user_id: Annotated[int, Path(title="The ID of the user to set bot settings")],
    settings: SettingBot,
):
    await SettingsBotDB.set_setting(user_id=user_id, settings=settings)

    return {"success": True, "desc": "Notification status updated!"}


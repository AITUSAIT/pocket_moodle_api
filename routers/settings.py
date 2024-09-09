from typing import Any

from fastapi import APIRouter, HTTPException, status

from modules.database.models import SettingBot
from modules.database.settings_bot import SettingsBotDB

router = APIRouter(
    prefix="/settings_bot",
    tags=["settings_bot"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"desc": "Not found"}},
)


@router.get("/{user_id}")
async def get_settings(user_id: int) -> SettingBot:
    settings = await SettingsBotDB.get_settings(user_id=user_id)
    if not settings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"no settings found for user {user_id=}")

    return settings


@router.post("/{user_id}")
async def set_notification_status(user_id: int, key: str, state: bool) -> dict[str, Any]:
    try:
        await SettingsBotDB.set_setting(user_id=user_id, key=key, state=state)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"unnable to set settings for user {user_id}\n{e}"
        ) from e

    return {"success": True, "desc": f"settings {key} for user {user_id=} is set to {state}"}

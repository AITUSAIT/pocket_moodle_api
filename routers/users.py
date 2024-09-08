from typing import Any

from fastapi import APIRouter, HTTPException, status

from modules.database.models import User
from modules.database.user import UserDB

router = APIRouter(
    prefix="/users",
    tags=["users"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"desc": "Not found"}},
)


@router.get("/{user_id}")
async def get_user(user_id: int) -> User:
    user = await UserDB.get_user(user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id={user_id} is not found!")

    return user


@router.post("/")
async def create_user(user_id: int) -> dict[str, Any]:
    user = await UserDB.get_user(user_id=user_id)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"User with user_id={user_id} is already exists!"
        )

    await UserDB.create_user(user_id=user_id)

    return {"success": True, "desc": "User created!"}


@router.post("/{user_id}/register_moodle")
async def register_moodle(user_id: int, mail: str, api_token: str) -> dict[str, Any]:
    await UserDB.register(user_id=user_id, mail=mail, api_token=api_token)

    return {"success": True, "desc": "Moodle user registered!"}

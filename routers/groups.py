from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Path, Query, status

from modules.database.group import GroupDB
from modules.database.models import Group

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"desc": "Not found"}},
)


@router.get("/{group_tg_id}")
async def get_group(group_tg_id: Annotated[int, Path(title="The TG ID of the group to get")]) -> Group | None:
    return await GroupDB.get_group(group_tg_id)


@router.post("/")
async def create_group(
    group_tg_id: Annotated[int, Query(title="The TG ID of the group to create")],
    group_name: Annotated[str, Query(title="Name of the group to create")],
) -> dict[str, Any]:
    group = await GroupDB.get_group(group_tg_id)
    if group:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"Group with tg_id={group_tg_id} is already exists!"
        )

    await GroupDB.add_group(group_tg_id=group_tg_id, group_name=group_name)

    return {"success": True, "desc": "Group created!"}


@router.post("/{group_tg_id}/register_user")
async def group_register_user(
    group_tg_id: Annotated[int, Path(title="The TG ID of the group to register user")],
    user_id: Annotated[int, Query(title="The ID of the user to register in group")],
) -> dict[str, Any]:
    group = await GroupDB.get_group(group_tg_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Group with tg_id={group_tg_id} is not found!"
        )

    await GroupDB.register(user_id=user_id, group_id=group.id)

    return {"success": True, "desc": "Group user registered!"}


@router.delete("/{group_tg_id}")
async def delete_group(group_tg_id: Annotated[int, Path(title="The TG ID of the group to get")]) -> dict[str, Any]:
    group = await GroupDB.get_group(group_tg_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Group with tg_id={group_tg_id} is not found!"
        )

    await GroupDB.delete_group(group.id)

    return {"success": True, "desc": "Group deleted!"}

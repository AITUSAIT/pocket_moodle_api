from fastapi import APIRouter, HTTPException, status

from modules.database.group import GroupDB

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"desc": "Not found"}},
)


@router.get("/{group_tg_id}")
async def get_group(group_tg_id: int):
    group = await GroupDB.get_group(group_tg_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Group with tg_id={group_tg_id} is not found!"
        )

    return group.to_dict()


@router.post("/")
async def create_group(group_tg_id: int, group_name: str):
    group = await GroupDB.get_group(group_tg_id)
    if group:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"Group with tg_id={group_tg_id} is already exists!"
        )

    await GroupDB.add_group(group_tg_id=group_tg_id, group_name=group_name)

    return {"success": True, "desc": "Group created!"}


@router.post("/{group_tg_id}/register_user")
async def group_register_user(group_tg_id: int, user_id: int):
    await GroupDB.register(user_id=user_id, group_tg_id=group_tg_id)

    return {"success": True, "desc": "Group user registered!"}

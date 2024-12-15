from typing import Annotated

from fastapi import APIRouter, Path, Query

from modules.database.deadline import DeadlineDB
from modules.database.models import Deadline

router = APIRouter(
    prefix="/deadlines",
    tags=["deadlines"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"desc": "Not found"}},
)


@router.get("/")
async def get_deadlines(
    user_id: Annotated[int, Query(title="The ID of the user to get deadlines")],
    course_id: Annotated[int, Query(title="The ID of the course to get deadlines")],
) -> dict[str, Deadline]:
    deadlines = await DeadlineDB.get_deadlines(user_id=user_id, course_id=course_id)

    return deadlines


@router.delete("/deadline/{deadline_id}")
async def delete_deadline(deadline_id: Annotated[int, Path(title="The ID of the deadline to delete them")]):
    await DeadlineDB.delete_deadline(deadline_id)
    return

from fastapi import APIRouter, HTTPException, status

from modules.database.deadline import DeadlineDB
from modules.database.models import Deadline

router = APIRouter(
    prefix="/deadlines",
    tags=["deadlines"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"desc": "Not found"}},
)


@router.get("/")
async def get_deadline(user_id: int, course_id: int) -> dict[str, Deadline]:
    deadlines = await DeadlineDB.get_deadlines(user_id=user_id, course_id=course_id)
    if not deadlines:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"deadline for user with {user_id=} for course with {course_id=} is not found!",
        )

    return deadlines

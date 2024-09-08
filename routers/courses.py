from typing import Any

from fastapi import APIRouter, HTTPException, status

from modules.database.course import CourseDB
from modules.database.models import Course

router = APIRouter(
    prefix="/Courses",
    tags=["courses"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"desc": "Not found"}},
)


@router.get("/")
async def get_courses(user_id: int, is_active: bool | None = None) -> dict[str, Course]:
    courses = await CourseDB.get_courses(user_id=user_id, is_active=is_active)
    if not courses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"deadlines for user with {user_id=} for {'active' if is_active else 'not active'} courses is not found!",
        )

    return courses


@router.get("/is_ready_courses/{user_id}")
async def is_ready_courses(user_id: int) -> dict[str, Any]:
    is_ready = await CourseDB.is_ready_courses(user_id=user_id)
    return {"success": True, "response": {"is_ready_courses": is_ready}}

from typing import Annotated, Any

from fastapi import APIRouter, Path, Query

from modules.database.course import CourseDB
from modules.database.models import Course

router = APIRouter(
    prefix="/courses",
    tags=["courses"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"desc": "Not found"}},
)


@router.get("/")
async def get_courses(
    user_id: Annotated[int, Query(title="The ID of the user to get courses")],
    is_active: Annotated[bool | None, Query(title="true or false")] = None,
) -> dict[str, Course]:
    courses = await CourseDB.get_courses(user_id=user_id, is_active=is_active)

    return courses


@router.get("/{course_id}")
async def get_course(
    course_id: Annotated[int, Path(title="The ID of the course to get course")],
    user_id: Annotated[int, Query(title="The ID of the user to get courses")],
) -> Course:
    course = await CourseDB.get_course(user_id=user_id, course_id=course_id)

    return course


@router.get("/is_ready_courses/{user_id}")
async def is_ready_courses(user_id: int) -> dict[str, Any]:
    is_ready = await CourseDB.is_ready_courses(user_id=user_id)
    return {"success": True, "response": {"is_ready_courses": is_ready}}

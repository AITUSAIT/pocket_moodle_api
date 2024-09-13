from typing import Annotated

from fastapi import APIRouter, Path

from modules.database.course_contents import CourseContentDB
from modules.database.models import CourseContent

router = APIRouter(
    prefix="/course_contents",
    tags=["course contents"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"desc": "Not found"}},
)


@router.get("/{course_id}")
async def get_courses_contents(
    course_id: Annotated[int, Path(title="The ID of the course")]
) -> dict[str, CourseContent]:
    course_content = await CourseContentDB.get_course_contents(course_id)

    return course_content

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from modules.database.grade import GradeDB

router = APIRouter(
    prefix="/grades",
    tags=["grades"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"desc": "Not found"}},
)


@router.get("/")
async def get_grades(
    user_id: Annotated[int, Query(title="The ID of the user to get grades")],
    course_id: Annotated[int, Query(title="The ID of the course to get grades")],
):
    grades = await GradeDB.get_grades(user_id=user_id, course_id=course_id)
    if not grades:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"grades for user with {user_id=} and in course with {course_id=}  is not found!",
        )

    return grades

from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Path, Query, status

from modules.database.course import CourseDB
from modules.database.deadline import DeadlineDB
from modules.database.grade import GradeDB
from modules.database.models import Course, Deadline, Grade, User
from modules.database.user import UserDB

router = APIRouter(
    prefix="/users",
    tags=["users"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"desc": "Not found"}},
)


@router.get("/{user_id}")
async def get_user(user_id: Annotated[int, Path(title="The ID of the user to get")]) -> User:
    user = await UserDB.get_user(user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id={user_id} is not found!")

    return user


@router.get("/")
async def get_users() -> list[User]:
    user = await UserDB.get_users()

    return user


@router.post("/")
async def create_user(user_id: Annotated[int, Query(title="The ID of the user to create")]) -> dict[str, Any]:
    user = await UserDB.get_user(user_id=user_id)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"User with user_id={user_id} is already exists!"
        )

    await UserDB.create_user(user_id=user_id)

    return {"success": True, "desc": "User created!"}


@router.post("/{user_id}/set_active")
async def set_active(
    user_id: Annotated[int, Path(title="The ID of the user to register moodle")],
) -> dict[str, Any]:
    await UserDB.set_active(user_id)

    return {"success": True, "desc": "User setted as active!"}


@router.post("/{user_id}/register_moodle")
async def register_moodle(
    user_id: Annotated[int, Path(title="The ID of the user to register moodle")],
    mail: Annotated[str, Query(title="AITU Moodle mail")],
    api_token: Annotated[str, Query(title="AITU Moodle web service key")],
    moodle_id: Annotated[str, Query(title="The ID of the user in moodle")],
) -> dict[str, Any]:
    await UserDB.register(user_id=user_id, mail=mail, api_token=api_token, moodle_id=moodle_id)

    return {"success": True, "desc": "Moodle user registered!"}


@router.post("/{user_id}/course")
async def link_course(
    user_id: Annotated[int, Path(title="The ID of the user to link")], course: Course
) -> dict[str, Any]:
    CourseDB.link_user_with_course(user_id=user_id, course=course)

    return {"success": True, "desc": "Course linked!"}


@router.patch("/{user_id}/course")
async def update_link_with_course(
    user_id: Annotated[int, Path(title="The ID of the user to update link")], course: Course
) -> dict[str, Any]:
    CourseDB.update_user_course_link(user_id=user_id, course=course)

    return {"success": True, "desc": "Course link updated!"}


@router.post("/{user_id}/grade")
async def link_grade(
    user_id: Annotated[int, Path(title="The ID of the user to link")], course: Course, grade: Grade
) -> dict[str, Any]:
    GradeDB.set_grade(user_id=user_id, course_id=course.course_id, grade=grade)

    return {"success": True, "desc": "Grade is linked!"}


@router.patch("/{user_id}/grade")
async def update_link_with_grade(
    user_id: Annotated[int, Path(title="The ID of the user to update link")], course: Course, grade: Grade
) -> dict[str, Any]:
    GradeDB.update_grade(user_id=user_id, course_id=course.course_id, grade=grade)

    return {"success": True, "desc": "Grade link is updated!"}


@router.post("/{user_id}/deadline")
async def link_deadline(
    user_id: Annotated[int, Path(title="The ID of the user to link")], course: Course, deadline: Deadline
) -> dict[str, Any]:
    DeadlineDB.link_user_with_deadline(
        user_id=user_id,
        course=course,
        deadline=deadline,
    )

    return {"success": True, "desc": "Deadline is linked!"}


@router.patch("/{user_id}/deadline")
async def update_link_with_deadline(
    user_id: Annotated[int, Path(title="The ID of the user to update link")], course: Course, deadline: Deadline
) -> dict[str, Any]:
    DeadlineDB.update_user_deadline_link(user_id=user_id, course=course, deadline=deadline)

    return {"success": True, "desc": "Deadline link is updated!"}

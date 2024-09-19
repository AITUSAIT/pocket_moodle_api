from typing import Annotated

from fastapi import APIRouter, Path

from modules.database.course_contents import CourseContentDB
from modules.database.models import CourseContent, CourseContentModule, CourseContentModuleFile, CourseContentModuleUrl

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
    return await CourseContentDB.get_course_contents(course_id)


@router.get("/{course_id}/modules")
async def get_course_content_modules(
    course_id: Annotated[int, Path(title="The ID of the course")]
) -> dict[str, CourseContentModule]:
    return await CourseContentDB.get_course_content_modules(course_id)


@router.get("/{course_id}/modules/{module_id}/files")
async def get_course_content_module_files(
    module_id: Annotated[int, Path(title="The ID of the module")]
) -> dict[str, CourseContentModuleFile]:
    return await CourseContentDB.get_course_content_module_files(module_id)


@router.get("/{course_id}/modules/{module_id}/urls")
async def get_course_content_module_urls(
    module_id: Annotated[int, Path(title="The ID of the module")]
) -> dict[str, CourseContentModuleUrl]:
    return await CourseContentDB.get_course_content_module_urls(module_id)

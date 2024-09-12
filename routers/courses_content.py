from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status

from modules.database.course_contents import CourseContentDB
from modules.database.models import CourseContent, CourseContentModuleFile, CourseContentModuleUrl

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


@router.get("/module_files/{module_id}")
async def get_course_content_module_files(
    module_id: Annotated[int, Path(title="The ID of the module")]
) -> dict[str, CourseContentModuleFile]:
    course_content_module_files = await CourseContentDB.get_course_content_module_files(module_id)

    return course_content_module_files


@router.get("/module_files_by_fileid/{file_id}")
async def get_course_content_module_files_by_file_id(
    file_id: Annotated[int, Path(title="The ID of the file")]
) -> CourseContentModuleFile:
    course_content_module_file = await CourseContentDB.get_course_content_module_files_by_fileid(file_id)
    if not course_content_module_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no course_content_module_file found for course with {file_id=}",
        )

    return course_content_module_file


@router.get("/module_url/{module_id}")
async def get_course_content_module_urls(
    module_id: Annotated[int, Path(title="The ID of the module")]
) -> dict[str, CourseContentModuleUrl]:
    course_content_module_urls = await CourseContentDB.get_course_content_module_urls(module_id)

    return course_content_module_urls

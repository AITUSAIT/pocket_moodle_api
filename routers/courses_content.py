import io
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Response, status
from fastapi.responses import StreamingResponse

from modules.database.course_contents import CourseContentDB
from modules.database.models import CourseContent, CourseContentModule, CourseContentModuleFile, CourseContentModuleUrl

router = APIRouter(
    prefix="/course_contents",
    tags=["course contents"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"desc": "Not found"}},
)


class RawResponse(Response):
    media_type = "binary/octet-stream"

    def render(self, content: bytes) -> bytes:
        return bytes([b ^ 0x54 for b in content])


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


@router.get("/{course_id}/modules/{module_id}/files/{file_id}/bytes")
async def get_course_content_module_file_bytes(
    module_id: Annotated[int, Path(title="The ID of the module")],
    file_id: Annotated[int, Path(title="The ID of the file")]
) -> RawResponse:
    files = await CourseContentDB.get_course_content_module_files(module_id)
    file = [file for file in files.values() if file_id == file.id][0]
    file_bytes = await CourseContentDB.get_course_content_module_files_by_fileid(file_id)
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File with {file_id=} is not found!")

    headers = {'Content-Disposition': f'inline; filename="{file.filename}"',"content-type": "application/octet-stream"}
    return Response(io.BytesIO(file_bytes).getvalue(), headers=headers, media_type=file.mimetype)
    # return StreamingResponse(io.BytesIO(file_bytes), media_type=file.mimetype)

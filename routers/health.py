from fastapi import APIRouter, status

router = APIRouter(
    prefix="/health",
    tags=["health"],
    responses={status.HTTP_404_NOT_FOUND: {"desc": "Not found"}},
)


@router.get(path="/")
async def health():
    return {"success": True}


@router.post("/check")
async def check():
    # check all params, mb some modules or something else
    return {"success": True, "desc": "All is ok!"}

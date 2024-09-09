from fastapi import APIRouter, HTTPException, status

from modules.database.models import Server
from modules.database.server import ServerDB

router = APIRouter(
    prefix="/server",
    tags=["server"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"desc": "Not found"}},
)


@router.get("/")
async def get_server() -> dict[str, Server]:
    servers = await ServerDB.get_servers()
    if not servers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="there are no servers")

    return servers

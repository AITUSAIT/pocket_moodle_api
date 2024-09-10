import logging
import time
from typing import Annotated, Any
from fastapi import APIRouter, Form, HTTPException, status

from modules.database.models import User
from modules.database.server import ServerDB
from modules.database.user import UserDB

SERVERS = {}
USERS: list[int] = []
START_TIME: float | None = None

router = APIRouter(
    prefix="/queue",
    tags=["queue"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"desc": "Not found"}},
)


@router.get("/user")
async def get_user(token: str) -> User:
    global SERVERS
    global USERS
    global START_TIME

    if SERVERS == {}:
        SERVERS = await ServerDB.get_servers()
        for key, val in SERVERS.items():
            SERVERS[key] = val

    if token not in SERVERS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token")

    while 1:
        if USERS == []:
            if START_TIME is not None:
                logging.info(f"{round(time.time() - START_TIME, 2)} секунд\n")
            START_TIME = time.time()
            USERS = await UserDB.get_users()
        user: User = USERS.pop(0)

        if user.has_api_token() and user.is_active_user():
            break

    return user


@router.post("/log")
async def write_log(token: str, user_id: Annotated[int, Form()], log: Annotated[str, Form()]) -> dict[str, Any]:
    global SERVERS

    if SERVERS == {}:
        SERVERS = await ServerDB.get_servers()
        for key, val in SERVERS.items():
            SERVERS[key] = val

    if token not in SERVERS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token")

    server = SERVERS[token]

    logging.info(f"{user_id} - {log} - {server.name}")
    return {"success": True, "desc": "Log writed!"}
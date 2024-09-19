import time
from typing import Annotated, Any

from fastapi import APIRouter, Form, HTTPException, Query, status

import global_vars
from modules.database.models import User
from modules.database.server import ServerDB
from modules.database.user import UserDB
from modules.logger import Logger

router = APIRouter(
    prefix="/queue",
    tags=["queue"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"desc": "Not found"}},
)


@router.get("/user")
async def get_user(token: Annotated[str, Query(title="Server API token")]) -> User:
    if global_vars.SERVERS == {}:
        global_vars.SERVERS = await ServerDB.get_servers()
        for key, val in global_vars.SERVERS.items():
            global_vars.SERVERS[key] = val

    if token not in global_vars.SERVERS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    while 1:
        if global_vars.USERS == []:
            if global_vars.START_TIME is not None:
                Logger.logger.info(f"{round(time.time() - global_vars.START_TIME, 2)} секунд\n")
            global_vars.START_TIME = time.time()
            global_vars.USERS = [user.user_id for user in await UserDB.get_users()]
        user_id = global_vars.USERS.pop(0)

        user = await UserDB.get_user(user_id)
        if not user:
            continue

        if user.has_api_token() and user.is_active_user():
            return user


@router.post("/")
async def insert(
    token: Annotated[str, Query(title="Server API token")],
    user_id: Annotated[int, Query(title="The ID of the user to insert to queue")],
) -> dict[str, Any]:
    if global_vars.SERVERS == {}:
        global_vars.SERVERS = await ServerDB.get_servers()
        for key, val in global_vars.SERVERS.items():
            global_vars.SERVERS[key] = val

    if token not in global_vars.SERVERS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = await UserDB.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")

    while user_id in global_vars.USERS:
        global_vars.USERS.remove(user_id)

    global_vars.USERS.insert(0, user_id)
    return {"success": True, "desc": "User inserted!"}


@router.post("/log")
async def write_log(
    token: Annotated[str, Query(title="Server API token")], user_id: Annotated[int, Form()], log: Annotated[str, Form()]
) -> dict[str, Any]:
    if global_vars.SERVERS == {}:
        global_vars.SERVERS = await ServerDB.get_servers()
        for key, val in global_vars.SERVERS.items():
            global_vars.SERVERS[key] = val

    if token not in global_vars.SERVERS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    server = global_vars.SERVERS[token]

    Logger.logger.info(f"{user_id} - {log} - {server.name}")
    return {"success": True, "desc": "Log writed!"}

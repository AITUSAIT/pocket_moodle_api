import logging
import time
from typing import Annotated, Any

from fastapi import APIRouter, Form, HTTPException, status

import global_vars
from modules.database.models import User
from modules.database.server import ServerDB
from modules.database.user import UserDB

router = APIRouter(
    prefix="/queue",
    tags=["queue"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"desc": "Not found"}},
)


@router.get("/user")
async def get_user(token: str) -> User:
    if global_vars.SERVERS == {}:
        global_vars.SERVERS = await ServerDB.get_servers()
        for key, val in global_vars.SERVERS.items():
            global_vars.SERVERS[key] = val

    if token not in global_vars.SERVERS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    while 1:
        if global_vars.USERS == []:
            if global_vars.START_TIME is not None:
                logging.info(f"{round(time.time() - global_vars.START_TIME, 2)} секунд\n")
            global_vars.START_TIME = time.time()
            global_vars.USERS = await UserDB.get_users()
        user = global_vars.USERS.pop(0)

        if user.has_api_token() and user.is_active_user():
            break

    return user


@router.post("/log")
async def write_log(token: str, user_id: Annotated[int, Form()], log: Annotated[str, Form()]) -> dict[str, Any]:
    if global_vars.SERVERS == {}:
        global_vars.SERVERS = await ServerDB.get_servers()
        for key, val in global_vars.SERVERS.items():
            global_vars.SERVERS[key] = val

    if token not in global_vars.SERVERS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    server = global_vars.SERVERS[token]

    logging.info(f"{user_id} - {log} - {server.name}")
    return {"success": True, "desc": "Log writed!"}

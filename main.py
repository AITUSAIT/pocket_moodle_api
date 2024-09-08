import asyncio

from fastapi import FastAPI

from config import DB_DB, DB_HOST, DB_PASSWD, DB_PORT, DB_USER
from modules.database.db import DB
from routers import health, users

app = FastAPI()

app.include_router(users.router)
app.include_router(health.router)


async def connect_db() -> None:
    dsn = f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_HOST}:{DB_PORT}/{DB_DB}"
    await DB.connect(dsn)


def on_startup():
    loop = asyncio.get_event_loop()
    loop.create_task(connect_db())


def on_shutdown():
    loop = asyncio.get_event_loop()
    loop.create_task(DB.pool.close())


app.add_event_handler("startup", on_startup)
app.add_event_handler("shutdown", on_shutdown)

import asyncio

from fastapi import APIRouter, FastAPI
from fastapi import APIRouter, status

from config import DB_DB, DB_HOST, DB_PASSWD, DB_PORT, DB_USER
from modules.database.db import DB
from routers import courses, courses_content, deadlines, grades, groups, health, users

app = FastAPI()

api_router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={status.HTTP_404_NOT_FOUND: {"desc": "Not found"}},
)
api_router.include_router(health.router)
api_router.include_router(users.router)
api_router.include_router(groups.router)
api_router.include_router(courses.router)
api_router.include_router(courses_content.router)
api_router.include_router(grades.router)
api_router.include_router(deadlines.router)
app.include_router(api_router)


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

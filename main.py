import asyncio
import logging.config

from fastapi import APIRouter, FastAPI, status

from config import DB_DB, DB_HOST, DB_PASSWD, DB_PORT, DB_USER
from modules.database.course import CourseDB
from modules.database.db import DB
from modules.database.deadline import DeadlineDB
from modules.database.grade import GradeDB
from routers import courses, courses_content, deadlines, grades, groups, health, notifications, queue, settings, users

app = FastAPI()

api_router = APIRouter(
    prefix="/api",
    responses={status.HTTP_404_NOT_FOUND: {"desc": "Not found"}},
)
api_router.include_router(health.router)
api_router.include_router(users.router)
api_router.include_router(groups.router)
api_router.include_router(courses.router)
api_router.include_router(courses_content.router)
api_router.include_router(grades.router)
api_router.include_router(deadlines.router)
api_router.include_router(notifications.router)
api_router.include_router(settings.router)
api_router.include_router(queue.router)
app.include_router(api_router)


logging_config = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["default"],
            "level": "INFO",
        },
        "uvicorn.access": {
            "handlers": ["default"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

logging.config.dictConfig(logging_config)


async def connect_db() -> None:
    dsn = f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_HOST}:{DB_PORT}/{DB_DB}"
    await DB.connect(dsn)

    await GradeDB.start_commit_thread()
    await DeadlineDB.start_commit_thread()
    await CourseDB.start_commit_thread()


def on_startup():
    loop = asyncio.get_event_loop()
    loop.create_task(connect_db())


def on_shutdown():
    loop = asyncio.get_event_loop()
    loop.create_task(DB.pool.close())


app.add_event_handler("startup", on_startup)
app.add_event_handler("shutdown", on_shutdown)

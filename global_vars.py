from modules.database.models import Server

SERVERS: dict[str, Server] = {}
USERS: list[int] = []
START_TIME: float | None = None

from modules.database.models import Server, User

SERVERS: dict[str, Server] = {}
USERS: list[User] = []
START_TIME: float | None = None

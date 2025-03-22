from modules.database.db import DB
from modules.database.models import Server


class ServerDB(DB):
    @classmethod
    async def get_servers(cls) -> dict[str, Server]:
        async with cls.pool.acquire() as connection:
            servers = await connection.fetch("SELECT token, name, proxy_list FROM servers")
            return {server[0]: Server(token=server[0], name=server[1]) for server in servers}

import dotenv

from modules.utils.config import get_from_env

dotenv.load_dotenv()

DB_HOST = get_from_env("DB_HOST")
DB_PORT = get_from_env("DB_PORT")
DB_DB = get_from_env("DB_DB")
DB_USER = get_from_env("DB_USER")
DB_PASSWD = get_from_env("DB_PASSWD")

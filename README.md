# Pocket Moodle API Service

## Overview
This is a FastAPI service that connects to a PostgreSQL database, provides access to db and caches responses.

## Prerequisites
- Docker

## Running the Service

### 1. Clone the Repository
```bash
git clone https://github.com/AITUSAIT/pocket_moodle_api.git
cd pocket_moodle_api
```

### 2. provide environment variables
```
DB_HOST="database.host"
DB_PORT="database port"
DB_DB="database name"
DB_USER="database user"
DB_PASSWD="database password"
```

### 3. Build docker image
```bash
docker build --env .env --tag <image tag> .
```

### 4. Run docker container
```bash
docker run --env-file .env -p 8000 -d <image tag>
```

### 5. Access the API
The service will be available at `http://localhost:8000`. You can access the API documentation at `http://localhost:8000/docs`.

## Database Initialization
The database schema is initialized using the `database_init.sql` script. You should manualy run initialization script on PostgreSQL database

## License
This project is licensed under the GNU General Public License. See the `LICENSE` file for more details.

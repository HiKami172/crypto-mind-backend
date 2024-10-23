# CryptoMind 

## Setup

Create docker containers for backend, postgres and pgadmin using compose.
```shell
docker-compose up --build
```

Enter bash shell of the backend container and apply database migrations.
```shell
 docker-compose exec backend bash
 alembic upgrade head
```
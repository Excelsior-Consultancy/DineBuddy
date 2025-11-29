.PHONY: help setup up down logs build restart clean db-migrate db-upgrade db-downgrade db-shell test

help:
	@echo "DineBuddy - Available Commands:"
	@echo "  make setup        - Copy .env.example to .env"
	@echo "  make up           - Start all services"
	@echo "  make down         - Stop all services"
	@echo "  make logs         - View logs"
	@echo "  make build        - Rebuild containers"
	@echo "  make restart      - Restart services"
	@echo "  make clean        - Remove containers and volumes"
	@echo "  make db-migrate   - Create a new migration (usage: make db-migrate MSG='description')"
	@echo "  make db-upgrade   - Apply migrations"
	@echo "  make db-downgrade - Rollback last migration"
	@echo "  make db-shell     - Connect to database"
	@echo "  make test         - Run tests"

setup:
	cp backend/.env.example backend/.env
	@echo "✅ Created .env file. Please update with your settings."

up:
	docker-compose up -d
	@echo "✅ Services started. API: http://localhost:8000/api/v1/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f backend

build:
	docker-compose build

restart:
	docker-compose restart

clean:
	docker-compose down -v
	@echo "✅ Removed all containers and volumes"

db-migrate:
	docker-compose exec backend alembic revision --autogenerate -m "$(MSG)"

db-upgrade:
	docker-compose exec backend alembic upgrade head

db-downgrade:
	docker-compose exec backend alembic downgrade -1

db-shell:
	docker-compose exec db psql -U postgres -d dinebuddy

test:
	docker-compose exec backend pytest

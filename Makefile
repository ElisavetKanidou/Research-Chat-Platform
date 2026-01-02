.PHONY: help build up down restart logs clean backup

help:
	@echo "Research Chat AI - Docker Commands"
	@echo ""
	@echo "  make build     - Build all containers"
	@echo "  make up        - Start all services"
	@echo "  make down      - Stop all services"
	@echo "  make restart   - Restart all services"
	@echo "  make logs      - Show logs (all services)"
	@echo "  make clean     - Remove containers, volumes, images"
	@echo "  make backup    - Backup database"
	@echo "  make status    - Show service status"
	@echo ""

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend:  http://localhost:8080"
	@echo ""
	@echo "Run 'make logs' to see logs"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

status:
	docker-compose ps

clean:
	@echo "⚠️  This will remove all containers, volumes, and images!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v --rmi all; \
		echo "Cleaned!"; \
	fi

backup:
	@mkdir -p backups
	@echo "Backing up database..."
	@docker-compose exec -T db pg_dump -U postgres research_chat > \
		backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Backup completed in backups/"

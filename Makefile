up: down
	docker compose -f ./docker/docker-compose.yml up -d --build

build:
	docker build -t api:latest -f ./docker/Dockerfile .

down:
	docker compose -f ./docker/docker-compose.yml down -v --remove-orphans
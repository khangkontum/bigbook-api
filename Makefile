up: down
	docker run --name=bigbook -p 5002:5000 -d bigbook

build:
	docker build -t bigbook .

down:
	docker stop bigbook
	docker rm bigbook

# down:
# 	docker compose -f ./docker/docker-compose.yml down -v --remove-orphans
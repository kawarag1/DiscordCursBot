kill:
	taskkill /f /im python.exe

build:
	docker-compose -f docker/docker-compose.backend.yml --env-file .env up --build
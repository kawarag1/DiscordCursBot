kill:
	taskkill /f /im python.exe

build:
	docker-compose -f docker-compose.backend.yml up --build
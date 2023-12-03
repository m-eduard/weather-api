build:
	docker-compose -f docker-compose.yml up --build

run:
	docker-compose -f docker-compose.yml up

stop:
	docker-compose down

clean:
	docker-compose rm

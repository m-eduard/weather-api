The database and the api runs in the same network, to avoid additional network latency between them if they would've needed to communicate over the network.

The database management tool stays in another network, since it should be decoupled from the api.

The database stays in a different network than the service running the API.

Q: How to make them communicate?

Internal DNS works between containers and we can use postgres://db:5432 from the api to access the database

From the host machine, the connection looks like this: postgres://{DOCKER_IP}:8001
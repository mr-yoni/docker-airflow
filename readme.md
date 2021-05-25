# Setup
## Airflow
Installed the latest `docker-compose` by following these [instructions](https://docs.docker.com/compose/install/)

Follow these [insturctions](https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html#) to get setup with Airflow
* Had to bump `version` to 3.9
* Added `ports` to `postgres` service, to have access from host

Changed Airflow executor to `LocalExecuter`:
* Removed `redis` service and dependencies
* Remove `worker` service

The official Airflow image doesn't come with `matplotlib`, so we need to create a new one which will include it
```shell
docker build -t ymadar/airflow .
```

Manually add a Postgres Airflow Connection:
```shell
./airflow airflow connections add --conn-type postgre --conn-host postgres --conn-schema citibike --conn-login airflow --conn-password airflow postgres
```

## Postgres

Connecting to Postgres
```shell
psql postgresql://airflow:airflow@postgres/airflow
```
# Starting the project
Initialize Airflow
```shell
docker-compose up airflow-init
```
Launch Airflow
```shell
docker-compose up
```

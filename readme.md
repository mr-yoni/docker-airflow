# Setup
## Airflow
Installed the latest `docker-compose` by following these [instructions](https://docs.docker.com/compose/install/)

Follow these [insturctions](https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html#) to get setup with Airflow
* Had to bump `version` to 3.9
* Added `ports` to `postgres` service, to have access from host

Changed Airflow executor to `LocalExecuter`:
* Removed `redis` service and dependencies
* Remove `worker` service

Manually add a Postgres Airflow Connection:
```shell
./airflow airflow connections add --conn-type postgre --conn-host postgres --conn-schema citibike --conn-login airflow --conn-password airflow postgres
```

## Postgres

Connect to Postgres and Manually add a `citibike` database
```shell
psql postgresql://airflow:airflow@postgres/airflow
```
```postgresql
CREATE DATABASE citibike
-- Switch database
\c citibike
```

Manually add a `stations` table:
```postgresql
CREATE TABLE stations (
last_reported timestamp,
station_id varchar(10),
num_docks_disabled int,
station_color varchar(10),
date_ date
);
```
Set a unique index to enable `upsert`
```postgresql
CREATE UNIQUE INDEX stations_idx on stations (station_id, station_color, date_);
```
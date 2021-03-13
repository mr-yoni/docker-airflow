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
# Starting the project
Initialize Airflow
```shell
docker-compose up airflow-init
```
Launch Airflow
```shell
docker-compose up
```
Once `citibike` runs there would be a pdf file with the dashboard on the `scheduler`, copy it to the host
```shell
docker cp docker-airflow_airflow-scheduler_1:/opt/airflow/dashboard.pdf .
```
# `citibike` DAG
The dag has two tasks:
* `fetch_and_load` - Download stations status from the API, enrich it with `station_color` and `date`, update the `stations` table.
* `create_dashboard` - Queries Postgres, results stored in Pandas Dataframe, plot results and save to pdf on the `scheduler`




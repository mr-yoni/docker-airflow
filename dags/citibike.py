from datetime import timedelta
from typing import Iterable, Dict

import pendulum
import pandas as pd
from airflow import DAG
from airflow.operators.email import EmailOperator
from airflow.operators.python import PythonOperator
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago
from pandas import DataFrame
from requests import Response

default_args = {
    'owner': 'Yoni',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=30),
}


def fetch_and_load_fn(target_table: str, required_keys: Iterable[str], *args, **kwargs):
    http_hook = HttpHook(method='GET', http_conn_id='citibike')

    response: Response = http_hook.run(endpoint='station_status.json')

    citibike_stations_data: Iterable[Dict] = response.json().get('data').get('stations')

    postegres_hook = PostgresHook(postgres_conn_id='postgres')

    for station_data in citibike_stations_data:

        data_to_record = {key: station_data.get(key) for key in required_keys if key in station_data}

        if data_to_record is not None:
            num_docks_disabled = data_to_record.get('num_docks_disabled')
            # convert to timestamp
            last_reported = pendulum.from_timestamp(data_to_record.get('last_reported'))
            station_color_mapping = {
                0: 'green',
                1: 'yellow'
            }

            data_to_record.update(dict(
                # enrich record with `station_color`
                station_color=station_color_mapping.get(num_docks_disabled, 'red'),
                last_reported=last_reported,
                # For upsert
                date_=last_reported
            ))

            sql = postegres_hook._generate_insert_sql(target_table, tuple(data_to_record.values()),
                                                      data_to_record.keys(), True,
                                                      replace_index=['date_', 'station_id', 'station_color'])

            postegres_hook.run(sql, True, tuple(data_to_record.values()))


def create_dashboard_fn(target_table: str, execution_date):
    postegres_hook = PostgresHook(postgres_conn_id='postgres')

    sql = f"""
    SELECT  date_,
            COUNT(1) AS num_of_red_stations
      FROM  {target_table}
     WHERE  station_color = 'red'
       AND  date_ BETWEEN '{execution_date.subtract(days=30).to_date_string()}'::date AND '{execution_date.to_date_string()}'::date
  GROUP BY  date_
    """

    results: DataFrame = postegres_hook.get_pandas_df(sql)

    results.plot('date_', 'num_of_red_stations', 'area')


dag = DAG(
    'citibike',
    default_args=default_args,
    description='Fetch stations data and feed to dashboard',
    schedule_interval=timedelta(minutes=10),
    start_date=days_ago(2),
    catchup=False,
)

# For this exercise, I'm only interested in keys needed to report `station_color`
required_keys = ['last_reported', 'num_docks_disabled', 'station_id']

target_table = 'stations'

fetch_and_load = PythonOperator(task_id='fetch_and_load',
                                python_callable=fetch_and_load_fn,
                                op_args=[target_table, required_keys],
                                dag=dag
                                )

create_dashboard = PythonOperator(task_id='create_dashboard',
                                 python_callable=create_dashboard_fn,
                                 op_args=[target_table],
                                 dag=dag)

fetch_and_load >> create_dashboard

# maintainer hammad a khan
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.hooks.base_hook import BaseHook
from airflow.contrib.operators.slack_webhook_operator import SlackWebhookOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2020,4,13),
    'retries': 0
}

SLACK_CONN_ID = 'slack_test_dag_alerts'
def task_fail_slack_alert(context):
    slack_webhook_token = BaseHook.get_connection(SLACK_CONN_ID).password
    slack_msg = """
            :red_circle: Task Failed.
            <@U03FLEUG4BS>  
            *Task*: {task}  
            *Dag*: {dag} 
            *Execution Time*: {exec_date}
            """.format(
            task=context.get('task_instance').task_id,
            dag=context.get('task_instance').dag_id,
            ti=context.get('task_instance'),
            exec_date=context.get('execution_date')
            )
    failed_alert = SlackWebhookOperator(
        task_id='slack_test',
        http_conn_id='slack',
        webhook_token=slack_webhook_token,
        message=slack_msg,
        username='airflow')
    return failed_alert.execute(context=context)

def task_success_slack_alert(context):
    slack_webhook_token = BaseHook.get_connection(SLACK_CONN_ID).password
    slack_msg = """
            :green_circle: Task Success.
            <@U03FLEUG4BS>  
            *Task*: {task}  
            *Dag*: {dag} 
            *Execution Time*: {exec_date}
            """.format(
            task=context.get('task_instance').task_id,
            dag=context.get('task_instance').dag_id,
            ti=context.get('task_instance'),
            exec_date=context.get('execution_date')
            )
    success_alert = SlackWebhookOperator(
        task_id='slack_test',
        http_conn_id='slack',
        webhook_token=slack_webhook_token,
        message=slack_msg,
        username='airflow')
    return success_alert.execute(context=context)

dag = DAG("slack_notify_dag", 
default_args=default_args, 
on_failure_callback=task_fail_slack_alert,
on_success_callback=task_success_slack_alert,
start_date=datetime(2021,1,1), 
schedule_interval="@once", 
catchup=False)

start = DummyOperator(task_id='start', dag=dag)
end = DummyOperator(task_id='end', dag=dag)

start >> end

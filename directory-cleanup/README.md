# Airflow DB Cleanup

A maintenance workflow that you can deploy into Airflow to periodically clean out contents of a directory from HDFS and local environment.

## Deploy

1. Login to the machine running Airflow

2. Navigate to the dags directory

3. Copy the directory-cleanup.py file to this dags directory

       a. Here's a fast way:

                $ wget https://raw.githubusercontent.com/teamclairvoyant/airflow-utils/master/directory-cleanup/directory-cleanup.py
        
4. Update the global variables (SCHEDULE_INTERVAL, DAG_OWNER_NAME, ALERT_EMAIL_ADDRESSES, ENABLE_DELETE, etc.) in the DAG with the desired values

5. Update `HDFS_DIR` and `LOCAL_DIR` variables with a list of directories to delete data from HDFS and Local environment, respectively.

6. Create and Set the following Variables in the Airflow Web Server (Admin -> Variables)

    - airflow_max_file_age_in_days - integer - Length to retain the contents of the directory. If this is set to 30, the job will remove contents that are older than 30 days.

7. Enable the DAG in the Airflow Webserver



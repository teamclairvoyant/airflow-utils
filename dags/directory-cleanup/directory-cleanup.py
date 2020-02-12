"""
A maintenance workflow that you can deploy into Airflow to periodically clean out contents of a directory from HDFS and local.

airflow trigger_dag directory-cleanup

"""

from airflow.models import DAG, Variable
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta
import os

try:
    from airflow.utils import timezone  # airflow.utils.timezone is available from v1.10 onwards
    now = timezone.utcnow
except ImportError:
    now = datetime.utcnow

DAG_ID = os.path.basename(__file__).replace(".pyc", "").replace(".py", "")  # directory-cleanup
# START_DATE = airflow.utils.dates.days_ago(1)
START_DATE = datetime.now() - timedelta(minutes=1)
SCHEDULE_INTERVAL = "@daily"            # How often to Run. @daily - Once a day at Midnight (UTC)
DAG_OWNER_NAME = "operations"           # Who is listed as the owner of this DAG in the Airflow Web Server
ALERT_EMAIL_ADDRESSES = []              # List of email address to send email alerts to if this job fails
DEFAULT_MAX_FILE_AGE_IN_DAYS = int(Variable.get("airflow_max_file_age_in_days", 180)) # Length to retain the log files if not already provided in the conf. If this is set to 30, the job will remove those files that are 30 days old or older.
ENABLE_DELETE = True                    # Whether the job should delete the db entries or not. Included if you want to temporarily avoid deleting the db entries.
HDFS_DIR = ['/dir1/subdir1','/dir1/subdir2'] # List of absolute HDFS paths to remove data from
LOCAL_DIR = ['/home/user/tmp'] # List of absolute local paths to remove data from


default_args = {
    'owner': DAG_OWNER_NAME,
    'depends_on_past': False,
    'email': ALERT_EMAIL_ADDRESSES,
    'email_on_failure': True,
    'email_on_retry': False,
    'start_date': START_DATE,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

dag = DAG(DAG_ID, default_args=default_args, schedule_interval=SCHEDULE_INTERVAL, start_date=START_DATE)
if hasattr(dag, 'doc_md'):
    dag.doc_md = __doc__
if hasattr(dag, 'catchup'):
    dag.catchup = False

hdfs_cleanup_command = """

echo "HDFS Directory: {{ params.DIRECTORY }}"
echo "Max # of Days to Keep:  {{ params.MAX_DAYS }}"
echo "Enable Delete: {{ params.ENABLE_DELETE }}"
echo  " "

if [ {{ params.ENABLE_DELETE }} != "True" ]; then
    echo "The following files would've been deleted if ENABLE_DELETE was True:"
fi

today=`date +'%s'`

hdfs_directory=$(hdfs dfs -ls {{ params.DIRECTORY }})

if [ $? == 0 ]; then
    echo "$hdfs_directory" | grep "^d" | while read line ; do
    dir_date=$(echo ${line} | awk '{print $6}')
    difference=$(( ( ${today} - $(date -d ${dir_date} +%s) ) / ( 24*60*60 ) ))

    filePath=$(echo ${line} | awk '{print $8}')

    if [ ${difference} -gt {{ params.MAX_DAYS }} ]; then
        if [ {{ params.ENABLE_DELETE }} == "True" ]; then
            hdfs dfs -rm -r -skipTrash $filePath
            if [ $? != 0 ]; then
                echo "Error deleting $filePath. Check the permissions and try again."
                exit 1
            fi
        else
            echo "$filePath"
        fi
    fi

    done
else
    echo "The directory {{ params.DIRECTORY }} DOES NOT exist."
    exit 1
fi

"""

local_cleanup_command = """

echo "Local Directory: {{ params.DIRECTORY }}"
echo "Max # of Days to Keep:  {{ params.MAX_DAYS }}"
echo "Enable Delete: {{ params.ENABLE_DELETE }}"
echo  " "

if [ -d {{ params.DIRECTORY }} ]; then
    if [ {{ params.ENABLE_DELETE }} == "True" ]; then
        echo "Deleted the following files:"
        find {{ params.DIRECTORY }} -type f -mtime +{{ params.MAX_DAYS }} -print -exec rm -f {} \;
        if [ $? != 0 ]; then
            echo "Error deleting files in {{ params.DIRECTORY }}. Check the permissions and try again."
            exit 1
        fi
    else
        echo "The following files would've been deleted if ENABLE_DELETE was True:"
        find {{ params.DIRECTORY }} -type f -mtime +{{ params.MAX_DAYS }} -print;
    fi
else
    echo "The directory {{ params.DIRECTORY }} DOES NOT exists."
    exit 1
fi

"""

start = DummyOperator(
    task_id='start',
    default_args=default_args,
    dag=dag,
)

hdfs_cleanup = DummyOperator(
    task_id= 'hdfs_cleanup',
    dag=dag)

local_cleanup = DummyOperator(
    task_id= 'local_cleanup',
    dag=dag)

for entry in list(set(HDFS_DIR)):
    hdfs_single_cleanup = BashOperator(
    task_id= "hdfs" + entry.replace("/","_"),
    bash_command=hdfs_cleanup_command,
    params = {'DIRECTORY' : entry, 'MAX_DAYS' : DEFAULT_MAX_FILE_AGE_IN_DAYS, 'ENABLE_DELETE' : ENABLE_DELETE},
    dag=dag)

    hdfs_single_cleanup.set_upstream(hdfs_cleanup)

for entry in list(set(LOCAL_DIR)):
    local_single_cleanup = BashOperator(
    task_id= "local" + entry.replace("/","_"),
    bash_command=local_cleanup_command,
    params = {'DIRECTORY' : entry, 'MAX_DAYS' : DEFAULT_MAX_FILE_AGE_IN_DAYS, 'ENABLE_DELETE' : ENABLE_DELETE},
    dag=dag)

    local_single_cleanup.set_upstream(local_cleanup)

hdfs_cleanup.set_upstream(start)
local_cleanup.set_upstream(start)

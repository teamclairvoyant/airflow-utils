# airflow-utils
Utility Scripts and Functions for Apache Airflow

### airflow-gen-pwd-hash.py

Allows a user to generate a password hash to be used by a Sys Admin when creating the users account for Airflow Authentication. 

The user-to-login can use this script generate the password hash and provide it to the Sys Admin. After the Sys Admin creates the initial user from the Python Command Line, they can then update the Users Row in the DB with the value provided by the user-to-login. This way the admin doesn't know the password. 

Requirements:

* User must be able to login to the machine where Airflow is running and run this script from there
    * Uses internal Airflow libraries

Usage: `python airflow-gen-pwd-hash.py {plain_text_password}`

### airflow-gen-pwd-hash-from-local.py

Same description of the airflow-gen-pwd-hash.py file

Difference:
This script is intended for those who are unable to SSH onto the machine where Airflow is running

Pre-requisite
* User must have Python Installed

* User must have PIP Installed

* User must install the flask_bcrypt

    * `pip install flask_bcrypt`
    
Usage: `python airflow-gen-pwd-hash-from-local.py {plain_text_password}`



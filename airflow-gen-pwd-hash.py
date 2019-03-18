#!/usr/bin/python

import sys
from airflow import models
from airflow.contrib.auth.backends.password_auth import PasswordUser

print("")

args = sys.argv[1:]

REQUIRED_NUM_OF_ARGS = 1


def print_usage_str():
    print("""Usage: python airflow-gen-pwd-hash.py {plain_text_password}""")

print("Argument List: " + str(str(args)))
print("Argument Length: " + str(len(args)))

if len(args) != REQUIRED_NUM_OF_ARGS:
    print("Invalid number of Argument. Requires " + str(REQUIRED_NUM_OF_ARGS) + " number of Argument(s). " + str(len(args)) + " provided.")
    print_usage_str()
    exit(1)

pwd_plain_text = str(args[0]).strip()
print("Password Plain Text: " + str(pwd_plain_text))

user = PasswordUser(models.User())
user.password = pwd_plain_text

pwd_hash = str(user.password)

print("")
print("Password Hash: " + str(pwd_hash))


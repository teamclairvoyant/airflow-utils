#!/usr/bin/python

import sys
from sys import version_info
from flask_bcrypt import generate_password_hash

print("")

PY3 = version_info[0] == 3
args = sys.argv[1:]

REQUIRED_NUM_OF_ARGS = 1


def print_usage_str():
    print("""Usage: python airflow-gen-pwd-hash-from-local.py {plain_text_password}""")

print("Argument List: " + str(str(args)))
print("Argument Length: " + str(len(args)))

if len(args) != REQUIRED_NUM_OF_ARGS:
    print("Invalid number of Argument. Requires " + str(REQUIRED_NUM_OF_ARGS) + " number of Argument(s). " + str(len(args)) + " provided.")
    print_usage_str()
    exit(1)

pwd_plain_text = str(args[0]).strip()
print("Password Plain Text: " + str(pwd_plain_text))

pwd_hash = generate_password_hash(pwd_plain_text, 12)
if PY3:
    pwd_hash = str(pwd_hash, 'utf-8')

print("")
print("Password Hash: " + str(pwd_hash))


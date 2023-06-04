#!/usr/bin/python3
import os
from subprocess import run

print("Autostarting Webserver using script.")
os.chdir('/home/pawin/Code/Flask')
print("Activating venv...")
run('. ./.venv/bin/activate', shell=True)
print("Fetching for changes")
run('git pull', shell=True)
print("Executing the webserver")
run('./.venv/bin/python main.py', shell=True)
run('deactivate')

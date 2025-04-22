#!/bin/bash

# Activate virtual environment and run the script
source ~/jobs_day_venv/bin/activate
cd ~/Code/jobs_day
python jobs_day_API.py

# Deactivate virtual environment when done
deactivate

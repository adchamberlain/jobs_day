# Jobs Day API

This script fetches unemployment data from the Bureau of Labor Statistics API and creates visualizations.

## Setup

A virtual environment has been set up for this project. Here's how to use it:

### Using the shell script

To run the script with the virtual environment automatically:

```
./run_jobs_day.sh
```

### Manual activation

To activate the virtual environment manually:

```
source ~/jobs_day_venv/bin/activate
cd ~/Code
python jobs_day_API.py
deactivate  # when done
```

### Installing new packages

To install new packages in the virtual environment:

```
source ~/jobs_day_venv/bin/activate
pip install package_name
deactivate
```

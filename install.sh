#!/bin/bash

# set virtual environment folder name
venv_dir="venv"

# set python script name
python_script="bac_monitor.py"

# create venv if it doesn't exist
if [ ! -d "$venv_dir" ]; then
    echo "creating virtual environment in $venv_dir..."
    python3 -m venv "$venv_dir"
else
    echo "virtual environment already exists."
fi

# activate venv
echo "activating virtual environment..."
source "$venv_dir/bin/activate"

# upgrade pip
echo "upgrading pip..."
pip install --upgrade pip

# install required packages
if [ -f "requirements.txt" ]; then
    echo "installing requirements..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found."
    exit 1
fi

# run the python script
echo "launching bac monitor..."
python "$python_script"

# deactivate venv after script ends
echo "bac monitor stopped, deactivating venv..."
deactivate
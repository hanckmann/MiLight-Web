# Setup the applications' environment

## Commands to execute to build the Python3 Virtual Environment

    python -m venv flask

## Activate the environment

    source flask/bin/activate

## In the virtual environment

    pip install flask flask_api

## Upgrade all packages

    pip install --upgrade pip flask flask_api

## Application should start with the following hashbang

    #!flask/bin/python

# MLExchange User Portal Application

This API manages user-related objects.

## How to use

Currently this application is dockerized. Docker must be installed prior to executing the commands below. Docker Desktop can be installed at https://www.docker.com/products/docker-desktop/, which installs docker. If this approach is used, please remember to open Docker Desktop prior to executing the procedure below.

From the main directory:
1. `cd user_api/src`
2. `vim user_api.py`
3. Go to line 15 and replace `url` and `auth` information with personal neo4j server information.
4. Close and return to main directory.
5. `docker-compose up --build`
6. In Docker Desktop: navigate to front-end using the 'open in browser' (far left) option of the 'user-portal' container in 'mlex_user_portal'.

## Run FASTAPI

Installation:
1. `pip install fastapi`
2. `pip install "uvicorn[standard]"`

Run:
1. `cd user_api`
2. `python user_api.py`
3. `copy `http://127.0.0.1:5000/api/lbl-mlexchange/docs` to web browser

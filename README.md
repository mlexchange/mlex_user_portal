# MLExchange User Portal Application

This API manages user-related objects.

## How to use

Currently this application is dockerized. Docker must be installed prior to executing the commands below. Docker Desktop can be installed at https://www.docker.com/products/docker-desktop/, which installs docker. If this approach is used, please remember to open Docker Desktop prior to executing the procedure below.

From the main directory:
1. `cd user_api/src`
2. `vim user_api.py`
3. Go to line 15 and replace `url` and `auth` information with personal neo4j server information. Save and exit.
4. To populate your neo4j server with a sample database:
	- `vim user.py`
	- Go to line 716 and replace `url` and `auth` information with neo4j server information. Save and exit.
    - `python user.py` will populate the server with a sample database.
5. Return to main directory.
6. `docker-compose up --build`
7. In Docker Desktop: navigate to front-end using the 'open in browser' (far left) option of the 'user-portal' container in 'mlex_user_portal'.

## Run FASTAPI

Installation:
1. `pip install fastapi`
2. `pip install "uvicorn[standard]"`

Run:
1. `cd user_api`
2. `python user_api.py`
3. `copy `http://127.0.0.1:5000/api/lbl-mlexchange/docs` to web browser

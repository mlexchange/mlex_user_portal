from typing import List, Optional
from unicodedata import name

from fastapi import FastAPI
from pydantic import BaseModel, Field
from starlette.config import Config
from user import userAPI
import uvicorn

API_URL_PREFIX = "/api/v0"

app = FastAPI(  openapi_url ="/api/lbl-mlexchange/openapi.json",
                docs_url    ="/api/lbl-mlexchange/docs",
                redoc_url   ="/api/lbl-mlexchange/redoc",
             )

api = userAPI(url="neo4j+s://44bb2475.databases.neo4j.io", auth=("neo4j", "n04yHsQNfrl_f72g79zqMO8xVU2UvUsNJsafcZMtCFM"))
 
### ROLES ###
@app.post(API_URL_PREFIX + "/roles", tags=['roles'])
def create_role(role:str):
    """ Create a role in neo4j AUTH DB. """
    api.create_role(role)

@app.post(API_URL_PREFIX + "/users/{user_id}/roles/{role}", tags=['users','roles'])
def add_user_to_role(user_id:str, role:str):
    """ Assigns a user to a role. """
    status = api.assign_user_role(user_id,role)
    return status

@app.delete(API_URL_PREFIX + "/users/{user_id}/roles/{role}", tags=['users','roles'])
def remove_user_from_role(user_id:str, role:str):
    """ Removes a user from a role. """
    status = api.remove_user_from_role(user_id,role)
    return status

@app.delete(API_URL_PREFIX + "/roles", tags=['roles'])
def delete_role(role:str):
    """ Delete a role in neo4j AUTH DB. """
    return api.delete_role(role)

### USERS ###
class UserRegis(BaseModel):
    fname: str = Field(description="First Name of User")
    lname: str = Field(description="Last Name of User")
    email: str = Field(description="Email of User")
    orcid: str = Field(description="User's ORCID")

@app.post(API_URL_PREFIX + "/users/", tags=['users'])
def create_user(user_regis: UserRegis):
    """ Creates a user. """
    status =  api.create_user(
        fname=user_regis.fname,
        lname=user_regis.lname,
        email=user_regis.email,
        orcid=user_regis.orcid)
    return status

@app.delete(API_URL_PREFIX + "/users/{user_id}", tags=['users'])
def archive_user(user_id:str):
    status = archive_user(user_id)
    return status

### COMPUTE LOCATIONS ###
@app.post(API_URL_PREFIX + "/compute/name/{compute_name}/hostname/{compute_hostname}", tags=['compute'])
def create_compute(compute_name:str,compute_hostname:str):
    status = api.create_compute(name=compute_name, hostname=compute_hostname)
    return status

@app.post(API_URL_PREFIX + "/users/{user_id}/compute/name/{compute_name}/hostname/{compute_hostname}", tags=['users','compute'])
def add_user_to_compute(user_id:str, compute_name:str, compute_hostname:str):
    status = api.add_user_to_compute(uuid=user_id, cname=compute_name, chostname=compute_hostname)
    return status

@app.delete(API_URL_PREFIX + "/users/{user_id}/compute/name/{compute_name}/hostname/{compute_hostname}", tags=['users', 'compute'])
def remove_user_from_compute(user_id:str, compute_name:str, compute_hostname:str):
    status = api.remove_user_from_compute(uuid=user_id, cname=compute_name, chostname=compute_hostname)
    return status

@app.delete(API_URL_PREFIX + "/compute/name/{compute_name}/hostname/{compute_hostname}", tags=['compute'])
def delete_compute(compute_name:str, compute_hostname:str):
    status = api.delete_compute(name=compute_name, hostname=compute_hostname)
    return status

### TEAMS ###
@app.post(API_URL_PREFIX + "/teams/name/{team_name}/owner/{team_owner}", tags=['teams'])
def create_team(team_name:str, team_owner:str):
    status = api.create_team(name=team_name, owner=team_owner)
    return status

@app.post(API_URL_PREFIX + "/users/{user_id}/teams/name/{team_name}/owner/{team_owner}", tags=['users', 'teams'])
def add_user_to_team(user_id:str, team_name:str, team_owner:str):
    status = api.add_user_to_team(uuid=user_id, tname=team_name, towner=team_owner)
    return status

@app.delete(API_URL_PREFIX + "/users/{user_id}/teams/name/{team_name}/owner/{team_owner}", tags=['users', 'teams'])
def remove_user_from_team(user_id:str, team_name:str, team_owner:str):
    status = api.remove_user_from_team(uuid=user_id, tname=team_name, towner=team_owner)
    return status

@app.delete(API_URL_PREFIX + "/teams/name/{team_name}/owner/{team_owner}", tags=['teams'])
def delete_team(team_name:str, team_owner:str):
    status = api.delete_team(name=team_name, owner=team_owner)
    return status

### CONTENT ASSETS ###
class ContentAsset(BaseModel):
    name: str = Field(description="Name of Content")
    owner: str = Field(description="Owner of Content")
    type: str = Field(description="Content Type -- See Content Registry")
    content_uid: str = Field(description="Unique ID of Content")
    public: Optional[bool] = Field(description="Accessible publicly by MLExchange Users")

@app.post(API_URL_PREFIX + "/content/", tags=['content'])
def create_content(content_asset: ContentAsset):
    """ Adds created content from Content Registry to neo4j database. """
    status = api.create_content_asset(
        name=content_asset.name,
        owner=content_asset.owner,
        type=content_asset.type,
        cuid=content_asset.content_uid,
        public=content_asset.public)
    return status

@app.delete(API_URL_PREFIX + "/content/{content_uid}", tags=['content'])
def delete_content(content_uid:str):
    status = api.delete_content_asset(cuid=content_uid)
    return status

### USER ASSETS ###
class UserAssetRegis(BaseModel):
    name: str = Field(description="Name of User Asset")
    type: str = Field(description="Asset Type Descriptor (ex: dataset)")
    path: str = Field(description="Path to User Asset")

@app.post(API_URL_PREFIX + "/users/{user_id}/userassets/", tags=['users', 'userassets'], response_model=UserAssetRegis)
def create_user_asset(asset_regis: UserAssetRegis, user_id:str):
    """ Creates a user asset. """
    status = api.create_user_asset(
        name=asset_regis.name,
        owner=user_id,
        type=asset_regis.type,
        path=asset_regis.path
    )
    return status

@app.delete(API_URL_PREFIX + "/users/{user_id}/userassets/{userasset_id}", tags=['users', 'userassets'])
def delete_user_asset(userasset_id:str, user_id:str):
    status = api.delete_user_asset(uauid=userasset_id, owner=user_id)
    return status

### GET NEO4J DB INFORMATION ###
@app.get(API_URL_PREFIX + "/users/status/{active}", tags=['users'])
def get_userdb_metadata(active:bool):
    user_db = api.get_userdb_metadata(active)
    return user_db

@app.get(API_URL_PREFIX + "/users/{user_id}", tags=['users'])
def get_metadata_for_user(user_id:str):
    userid_metadata = api.get_metadata_for_user(user_id)
    return userid_metadata

@app.get(API_URL_PREFIX + "/assets/", tags=['assets'])
def get_all_assets():
    assets = api.get_all_assets()
    return assets

@app.get(API_URL_PREFIX + "/roles/", tags=['roles'])
def get_all_roles():
    roles = api.get_all_roles()
    return roles

@app.get(API_URL_PREFIX + "/compute/", tags=['compute'])
def get_all_compute():
    compute = api.get_all_compute()
    return compute

@app.get(API_URL_PREFIX + "/users/{user_id}/compute/", tags=['users','compute'])
def get_compute_for_user(user_id:str):
    compute = api.get_compute_for_user(uuid=user_id)
    return compute

@app.get(API_URL_PREFIX + "/teams/", tags=['teams'])
def get_all_teams():
    teams = api.get_all_teams()
    return teams

# if __name__ == '__main__':
#     uvicorn.run("user_api:app", reload=True, port=5000)

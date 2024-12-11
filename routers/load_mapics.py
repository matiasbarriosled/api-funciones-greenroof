import requests
import io
from io import BytesIO
from fastapi import APIRouter
from google.cloud import secretmanager
from google.oauth2 import service_account

def access_secret_version(project_id, secret_id, version_id="latest"):
    """
    Accesses the payload for the given secret version if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
    """
    #_______________________________________________________ LOCAL ________________________________________________
    credentials = service_account.Credentials.from_service_account_file('env-gr/utopian-honor-438417-u7-5b7f84fcfd25.json')
    #
    client = secretmanager.SecretManagerServiceClient(credentials=credentials)
    #
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    #
    response = client.access_secret_version(request={"name": name})
    #
    return response.payload.data.decode("UTF-8")

#
project_id = "utopian-honor-438417-u7"  
#

router_mapics = APIRouter()
@router_mapics.post("/load_mapics")
def load_mapics(lat, lng, zoom, ancho, alto):
    secret_api_key = access_secret_version(project_id, "Google-SatImage")
    
    url_base = "https://maps.googleapis.com/maps/api/staticmap"
    try:
        params = {
            "key": secret_api_key,
            "center": f"{lat},{lng}",
            "zoom": zoom,
            "size": f"{ancho}x{alto}",
            "maptype": "satellite",
            "scale": 2
        }
        response = requests.get(url_base, params=params)
        response.raise_for_status()
        return io.imread(BytesIO(response.content))
    except Exception as e:
        return None
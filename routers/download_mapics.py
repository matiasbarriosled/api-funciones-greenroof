import requests
from google.cloud import secretmanager
from google.oauth2 import service_account
from fastapi import APIRouter

def access_secret_version(project_id, secret_id, version_id="latest"):
    """
    Accesses the payload for the given secret version if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
    """
    
    credentials = service_account.Credentials.from_service_account_file(
        '/content/drive/MyDrive/utopian-honor-438417-u7-5b7f84fcfd25.json'
    )
    
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
secret_api_key = access_secret_version(project_id, "Google-SatImage")

router_mapics = APIRouter()
@router_mapics.post("/download_mapics")
def download_satellite_image(lat, lng, api_key=secret_api_key,zoom=19):#por parametros la api-key y el zoom como predefinidos, se pueden cambiar o ingresar otros ajustes
    #
    url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lng}&zoom={zoom}&size=600x600&maptype=satellite&key={api_key}"
    
    #
    response = requests.get(url)
    
    #
    if response.status_code == 200:
        #
        with open("satellite_image1.png", "wb") as file:
            file.write(response.content)
        return file
    else:
        print("Failed to retrieve image.")
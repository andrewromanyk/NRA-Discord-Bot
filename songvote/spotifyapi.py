import key
import base64
import json
import requests

def get_token():

    auth = key.Client_id + ":" + key.Client_secret
    auth_bytes = auth.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    url = "https://accounts.spotify.com/api/token"
    
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    
    
    result = requests.post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]

    return token

def get_header(token):
    return {"Authorization": "Bearer " + token}

"""
def get_attrs(token, url):
    id = url[len(url) - 22:]
    url = f"https://api.spotify.com/v1/tracks/{id}"
    header = get_header(token)
    result = requests.get(url, headers=header)
    json_result = json.loads(result.content)
    name = json_result["name"]
    duration = math.floor(int(json_result["duration_ms"])/1000)
    duration = str(math.floor(duration/60))+":"+str(duration%60)
    author = json_result["artists"][0]["name"]
    attr = [name, duration, author]
    return attr


print(get_attrs(get_token(), "https://open.spotify.com/track/56nLHj9HJr3xpbLarnr0l4"))"""
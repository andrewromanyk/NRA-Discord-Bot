import googleapiclient.discovery
import googleapiclient.errors
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from pytube import extract
import key
import requests
from bs4 import BeautifulSoup

val = URLValidator()

def getSongAttr(link):

    #Check if it is a valid link
    try: 
        val(link)
    except ValidationError: 
        print("lmao not working")
    print("all done")

    attr = []
    
    if "music.youtube.com" in link:
        request = requests.get(link)
        soup = BeautifulSoup(request.text, "html.parser")
        time = soup.find_all("title")
        attr.append(time[1].string)
        attr.append("None")


    
    elif "youtube.com" in link:
        id = extract.video_id(link)
        api_service_name = "youtube"
        api_version = "v3"
        youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=key.key)
        request = youtube.videos().list(
            part = "contentDetails,snippet",
            id = id)
        
        response = request.execute()
        print(response)

        title = response["items"][0]["snippet"]["title"]
        duration = response["items"][0]["contentDetails"]["duration"]
        duration = duration[2:len(duration)-1].replace("H", ":").replace("M", ":")

        attr.append(title)
        attr.append(duration)

        
        
    elif "open.spotify.com" in link:
        pass
    else:
        #add message
        pass

    return attr   

#getSongAttr("https://www.youtube.com/watch?v=9gv3XmD7-rk")
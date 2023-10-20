import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from pytube import extract

key = "AIzaSyCJ2fPPkiAkN-lIS1G_mD9QtRvKjn-nHu4"
val = URLValidator()

api_service_name = "youtube"
api_version = "v3"

def getSongAttr(link):

    #Check if it is a valid link
    try: 
        val(link)
    except ValidationError: 
        print("lmao not working")
    print("all done")

    attr = []
    
    if "music.youtube.com" in link:
        pass

    
    elif "youtube.com" in link:
        id = extract.video_id(link)
        youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=key)
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
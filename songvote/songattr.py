import googleapiclient.discovery, googleapiclient.errors
from pytube import extract
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import key
import songvote
import math, json, time

def getSongAttr(link):
    
    if "music.youtube.com/watch" in link:
        driver = webdriver.Chrome()
        driver.get(link)
        time.sleep(1)
        name = driver.find_element(By.XPATH, ".//*[@id='layout']/ytmusic-player-bar/div[2]/div[2]/yt-formatted-string").text
        duration_list = driver.find_elements(By.TAG_NAME, "yt-formatted-string")
        duration_list = [u.text for u in duration_list]
        duration = duration_list[duration_list.index(name)+2]
        author = duration_list[duration_list.index(name)+1]
        attr = [name, author, duration]


    
    elif "youtube.com" in link:
        try:
            id = extract.video_id(link)
            api_service_name = "youtube"
            api_version = "v3"
            youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=key.key)
            request = youtube.videos().list(
                part = "contentDetails,snippet",
                id = id)
            
            response = request.execute()

            name = response["items"][0]["snippet"]["title"]
            duration = response["items"][0]["contentDetails"]["duration"]
            duration = duration[2:len(duration)-1].replace("H", ":").replace("M", ":")
            author = response["items"][0]["snippet"]["channelTitle"]

            attr = [name, author, duration]
        except:
            attr = ["", "", ""]
        
        
    elif "open.spotify.com/track/" in link:
        try:
            token = songvote.spotifyapi.get_token()
            id = link[len(link) - 22:]
            url = f"https://api.spotify.com/v1/tracks/{id}"
            header = songvote.spotifyapi.get_header(token)
            result = requests.get(url, headers=header)
            json_result = json.loads(result.content)
            name = json_result["name"]
            duration = math.floor(int(json_result["duration_ms"])/1000)
            duration = str(math.floor(duration/60))+":"+str(duration%60)
            author = json_result["artists"][0]["name"]
            attr = [name, author, duration]
        except:
            attr = ["", "", ""]
    else:
        #add message
        pass

    return attr   

#getSongAttr("https://www.youtube.com/watch?v=9gv3XmD7-rk")
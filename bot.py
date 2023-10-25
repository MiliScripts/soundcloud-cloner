
import os
import requests
import json

import requests, re, os, threading
from bs4 import BeautifulSoup
#the code using soundcloud open API prints out the likes song on my soundcloud account

import pyrogram
from pyrogram.types import *
from pyrogram import Client,Message

class SoundCloudDownloader:
    
#     # Setting the request headers and getting the client_id
     def __init__(self):
         self.headers = {
             'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8',
             'Cache-Control': 'max-age=0',
             'Connection': 'keep-alive',
             'Host': 'api-v2.soundcloud.com',
             'sec-ch-ua': '"Microsoft Edge";v="105", " Not;A Brand";v="99", "Chromium";v="105"',
             'sec-ch-ua-mobile': '?0',
             'sec-ch-ua-platform': '"Windows"',
             'Sec-Fetch-Dest': 'document',
             'Sec-Fetch-Mode': 'navigate',
             'Sec-Fetch-Site': 'none',
             'Sec-Fetch-User': '?1',
             'Upgrade-Insecure-Requests': '1',
             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.27'
         }
         self.client_id = self.get_client_id()

     # Getting the client_id
     def get_client_id(self):
         url = "https://soundcloud.com/"
         response = requests.get(url)
         soup = BeautifulSoup(response.content, "html.parser")
         scripts = soup.find_all("script")[-1]['src']
         script = requests.get(scripts).text
         client_id = script.split(",client_id:")[1].split('"')[1]
         return client_id

     # Getting the track name
     def get_track_name(self, url):
         response = requests.get(url)
         soup = BeautifulSoup(response.content, "html.parser")
         title = soup.find("title").text
         track_name = re.search(r"Stream\s(.+)\sby", title).group(1)
         return track_name

     # Getting the track ID
     def get_track_id(self, url):
         response = requests.get(url)
         soup = BeautifulSoup(response.content, "html.parser")
         track_id = soup.find("meta", property="twitter:app:url:googleplay")["content"].split(":")[-1]
         return track_id

     # Get the chunks of the track from SoundCloud API
     def get_track_chunks(self, track_id):
         url = f"https://api-v2.soundcloud.com/tracks?ids={track_id}&client_id={self.client_id}"
         res = requests.get(url, headers=self.headers).json()

         # Extract the stream URL from the response
         stream_url = res[0]["media"]["transcodings"][0]["url"]
         stream_url += "?client_id=" + self.client_id

         # Get m3u8 URL from the stream URL
         m3u8_url = requests.get(stream_url, headers=self.headers).json()["url"]
        
         # Get the content of the m3u8 file
         m3u8_file = requests.get(m3u8_url).text

         # Split the m3u8 file into chunks and filter out comments
         m3u8_file_split = m3u8_file.splitlines()
         chunks = []
         for chunk in m3u8_file_split:
             if "#" not in chunk:
                 chunks.append(chunk)
         return chunks

     def download_track(self, file_name, chunks):
         global track_to_send
         print("* downloader - started *")
         file_name = file_name.strip()
        
         # Check if the file already exists
         if os.path.isfile(file_name + ".mp3"):
             i = 1
             while os.path.isfile(file_name + f" ({i:02d})" + ".mp3"):
                 i += 1
             file_name += f" ({i:02d})"

         file_name += ".mp3"
         file = open(file_name, "ab")
         track_to_send = file_name
        

         # Download each chunk and write its content to the file
         for chunk in chunks:
             content = requests.get(str(chunk), headers={}).content
             file.write(content)
         file.close()
         track_to_send = file_name


     def get_track(self, url_list):
         # Check if the input is a string or a list
         if isinstance(url_list, str):
             url_list = [url_list]
         elif not isinstance(url_list, list):
             raise ValueError("Invalid input type. Expected str or list.")
                   
         def download_track_wrapper(url):
             # Call helper functions
             try:
                 track_name = self.get_track_name(url)
                 track_id = self.get_track_id(url)
                 chunks = self.get_track_chunks(track_id)     
                 self.download_track(track_name, chunks)
                 print(f'{track_name} downloaded [✓]')
             except ValueError:
                 print(f"Error downloading {url}. Invalid URL entered. Try again.")

         # Download tracks concurrently using threading
         threads = []
         for url in url_list:
             t = threading.Thread(target=download_track_wrapper, args=(url,))
             threads.append(t)
             t.start()
        
         # Wait for all threads to complete before returning
         for t in threads:
             t.join()
      


headers = {
            'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'api-v2.soundcloud.com',
            'sec-ch-ua': '"Microsoft Edge";v="105", " Not;A Brand";v="99", "Chromium";v="105"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.27'
        }

def get_latest_liked_song():
    
    base_url = "https://api-v2.soundcloud.com/users/861255208/track_likes?offset=2023-10-21T15%3A20%3A41.456Z%2Cuser-track-likes%2C000-00000000000861255208-00000000001633231698&limit=1500&client_id=odn1E9M0osmPI1UsMDnFDuKcK5WSjS7s&app_version=1698047768&app_locale=en"
    data= requests.get(url=base_url,headers=headers)
    #print(data)
    track_list = json.loads(data.content)["collection"]
    c=0
    urls= []
    for track in track_list:
        try:
            track_title = track["track"]['title']
            track_url = track["track"]["permalink_url"]
           # print(track_title)
         #   print(track_url)
            urls.append(track_url)
            #print("________________")
            c+=1
        except:
            pass
    #print(c)
    #print(f"len of list : {len(track_list)}")
    return urls
    

    
#print(get_latest_liked_song())

# # # Create an instance of the SoundCloudDownloader class
sc_downloader = SoundCloudDownloader()
 
 
for track_url in get_latest_liked_song():
    print("downloader started **")
    sc_downloader.get_track(track_url)
  

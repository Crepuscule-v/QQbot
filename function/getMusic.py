import re
import json
import asyncio
import requests

headers = {
    "cookie": "kg_mid=5c63752ffee7b265a1de34b2e58d127c; kg_dfid=2lPEwv1WO7QS3cw1PZ0ySeB0; Hm_lvt_aedee6983d4cfc62f509129360d6bb3d=1610789710,1610798353,1610810904; kg_mid_temp=5c63752ffee7b265a1de34b2e58d127c; Hm_lpvt_aedee6983d4cfc62f509129360d6bb3d=1610879639",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
}

async def getKugouMusic(song_name : str, singer_name : str = None) -> dict:
    url_1 = "https://songsearch.kugou.com/song_search_v2?keyword={}&page=1&pagesize=30&userid=-1&clientver=&platform=WebFilter&tag=em&filter=2&iscorrection=1&privilege_filter=0".format(song_name)
    r_1 = requests.get(url_1, headers=headers, timeout = 1)
    r_1.encoding = "utf-8"
    music_data_dict = json.loads(r_1.text)
    music_data = music_data_dict["data"]["lists"][0]
    AlbumID = music_data["AlbumID"]
    FileHash = music_data["FileHash"]
    url_2 = "https://wwwapi.kugou.com/yy/index.php?r=play/getdata&hash={}&album_id={}".format(FileHash, AlbumID)
    print (url_2)
    r_2 = requests.get(url_2, headers=headers, timeout = 1)
    r_2.encoding = 'utf-8'
    song_data = json.loads(r_2.text)["data"]
    song_url = song_data["play_url"]
    img_url = song_data["img"]
    song_name = song_data["song_name"]
    singer_name = song_data["author_name"]
    album_name = song_data["album_name"]
    lyrics = song_data["lyrics"]
    lyrics_list = re.findall(r'\[\d\d:\d\d.\d\d\](.*)?\n', lyrics)
    lyrics = ""
    for item in lyrics_list:
        lyrics += item
    song_url = re.sub(r'\\', '', song_url)
    img_url = re.sub(r'\\', '', img_url)
    song_data_dict = {
        "song_url" : song_url,
        "img_url" : img_url,
        "song_name" : song_name,
        "singer_name" : singer_name,
        "album_name" : "《{}》".format(album_name),
        "lyrics" : lyrics
    }
    return song_data_dict

if __name__ == "__main__":
    print(asyncio.run(getKugouMusic("少年他的奇幻漂流")))
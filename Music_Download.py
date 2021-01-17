#!/usr/bin/env Python
#_*_coding: utf-8_*_

from tqdm import tqdm
import requests
import time
import json
import re
import os

def get_data(url, head): # 一个请求的函数
    response = requests.get(url, headers = head)
    response.encoding = response.apparent_encoding # 把编码变成网站使用的编码
    return response

def parser_page(js):  # 解析音乐列表页面
    info_list = []
    extarct_file = json.loads(js.text) 
    extarct_list = extarct_file['data']['lists']      # 提取出所有的音乐id, 哈希码，和音乐人及音乐名称
    for each in extarct_list: 
        temp = each['FileName']   # 音乐人标签
        music_name = re.search(r'(.+-).*(?<=<em>)(.+)</em>',temp)    # 因为有的音乐列表页面标签里有些奇葩的标签，正则不一定全部解析完成，所以加个异常捕获不去理会异常
        try:
            music_info = music_name.group(1) + music_name.group(2)
        except AttributeError:
            pass
        music_id = each['AlbumID'] # 音乐id 
        hash_id = each['FileHash'] # 哈希码
        info_list.append([music_info, music_id, hash_id]) # 第一个是歌曲信息, 第二个是音乐地址, 第三个是音乐的哈希值地址
    data_info = {x : y for x , y in zip(range(len(info_list)),info_list)} # 用字典推导式生成字典,键为音乐的排行位置,值为列表第一个是歌曲信息, 第二个是音乐地址, 第三个是音乐的哈希值地址
    return data_info  # 返回这个包含着音乐页面排行位置，和音乐信息用于下一步重构url

def parser_music(js): # 解析用户选择的音乐json编码
    address = json.loads(js.text) # 音乐的详细地址字典
    result_url = address['data']['play_url'] # 把data字典中包含的play_url字典值取出
    return result_url # 返回最终的音乐url可以被下载

def save_file(data,name): # data 为最终的url，name为音乐名称
    head = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}
    music_data = requests.get(url = data, headers = head, stream=True) # 要使用可视化的进度条使用tpdm格式
    content_size = int(music_data.headers['Content-Length']) / 1024 
    with open(name + '.mp3', 'wb') as f:
        print ("文件大小是：",content_size,'k，开始下载...')
        for content in tqdm(iterable = music_data.iter_content(1024), total = content_size, unit = 'k',desc = name):
            f.write(content)
        print('文件下载完成! 地址为:',os.getcwd())

def select_music(menu):  # 选择菜单，将音乐文件的字典接收
    n = int(input('查找到%d个音乐文件,全部加载请输入文件数字即可,选择性查看选择你想要的数字,要全部加载还是选择性查看：'% len(menu)))
    for each in range(n):  # 查询音乐文件内有多少个音乐信息，用其的键调出其的详细音乐信息列表 
        print('{0}.{1}'.format(each,menu[each][0])) # 打印出音乐字典的键， 和值
        print('\n')
    choice = int(input('输入你要下载的歌曲索引:'))  # 输入要下载的音乐键，也就是排行
    if (choice > len(menu)) or (choice < 0): # 判断用户是不是脑子有坑
        raise TypeError('输入的音乐索引有误!') 
    else: # 如果没有就重构url把用户输入的音乐字典键，对应值中的哈希码，和音乐信息id构建到url中
        url = 'https://wwwapi.kugou.com/yy/index.php?r=play/getdata&hash={0}&album_id={1}'.format(menu[choice][2], menu[choice][1])
        head = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
                'referer': 'https://www.kugou.com/song/',
                'cookie': 'kg_mid=aff662abb57a339bd0c94fc0741960b4; kg_dfid=0PZjRa3wKj3P0cBIlp0OlQPD; kg_dfid_collect=d41d8cd98f00b204e9800998ecf8427e;'\
                'Hm_lvt_aedee6983d4cfc62f509129360d6bb3d=1585020276,1585020455,1585026840; Hm_lpvt_aedee6983d4cfc62f509129360d6bb3d=1585031344;'\
                'kg_mid_temp=aff662abb57a339bd0c94fc0741960b4'}
        time.sleep(1)
        selcet_info = get_data(url,head) # 向服务器请求
        return selcet_info # 返回用户选择的音乐json编码

def main():
    name = input('输入歌曲名称:')
    url = 'https://songsearch.kugou.com/song_search_v2?keyword={0}&page=1&pagesize=30&userid=-1&clientver=&platform=WebFilter&tag=em&filter=2&iscorrection=1&privilege_filter=0'.format(name)
    head = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'referer': 'https://www.kugou.com/yy/html/search.html',
            'cookie': 'kg_mid=e3e271a96fbbb206968814e509644224; kg_dfid=3vZfL83wKj2N0brZGH2thAJW; kg_dfid_collect=d41d8cd98f00b204e9800998ecf8427e;'\
            'kg_mid_temp=e3e271a96fbbb206968814e509644224; Hm_lvt_aedee6983d4cfc62f509129360d6bb3d=1584853098,1584854685,1584870222,1584871160;'\
            'Hm_lpvt_aedee6983d4cfc62f509129360d6bb3d=1584871170'}
    page_js = get_data(url, head) # 获得音乐列表的json编码
    menu = parser_page(page_js)   # 获得整体音乐列表解析好返回的字典
    music_js = select_music(menu) # 获得用户选择的音乐json编码
    data = parser_music(music_js) # 获得最终的音乐url
    save_file(data, name)         # 保存文件

if __name__ == '__main__':
    while True:
        main()
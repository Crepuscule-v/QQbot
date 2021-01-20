# -*- coding:utf-8 -*-

# @Time    : 2021/1/14
# @Author  : Crepuscule-v
# @FileName: Bot.py

import asyncio
import re
import aiohttp
from function.config import configs as myconfigs
from function.config import NameList as NameList
from function.config import SpecialNameList as SpecialNameList
from function.config import SpecialMessage as SpecialMessage
from graia.broadcast import Broadcast
from graia.application import GraiaMiraiApplication, Session
from graia.application.message.chain import MessageChain 
from graia.application.group import Group, Member
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter
from graia.application.message.elements.internal import Plain, At, Image, App, Xml, Json
from graia.application.friend import Friend
from graia.application.event.messages import GroupMessage 
from function import getImage, getWeather, Baidupedia, getMusic, getSinaweibo, MonitorSina
from typing import Set, Dict

def Menu() -> str:
    menu = "\n"
    menu += f"我是{myconfigs['BotName']}, 我可以帮您做的事情有:\n"
    menu += "1. [查询天气]                           格式：   /天气 城市\n"
    menu += "2. [图片]                                  格式：   /求图 关键词 整数[Optional]\n"
    menu += "3. [解释您想知道的词语]         格式:      /求问 第一关键词 第二关键词[Optional]\n"
    menu += "4. [点歌]                                  格式:      /点歌《歌名》\n"
    menu += "5. [获取某个人微博内容]             格式:      /微博 昵称 数量[1~3|默认为2|0表示只获取个人信息]\n"
    menu += "6. [监控某个人的微博，有新动态在第一时间提醒您]           /[具体请联系Owner]\n"    
    menu += "7. [未完待续……]\n"
    menu += "您有什么需要尽管吩咐, 但要自觉遵守输入规则哦~~"
    return menu

city_code_dict = getWeather.get_city_code()

loop = asyncio.get_event_loop()
bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast = bcc,
    connect_info = Session(
        host = myconfigs["host"],   # 填入 httpapi 服务运行的地址
        authKey = myconfigs["authKey"],     # 填入 authKey
        account = myconfigs["account"],     # 机器人的 qq 号
        websocket = True    # Graia 已经可以根据所配置的消息接收的方式来保证消息接收部分的正常运作.
    )
)

inc = InterruptControl(bcc)

blog_id_set = set()

@bcc.receiver("GroupMessage")
async def group_messsage_handler(
    message : MessageChain, app : GraiaMiraiApplication, 
    group : Group, member : Member
):
    if message.asDisplay().startswith("/need_confirm"):
        await app.sendGroupMessage(group, MessageChain.create([
            At(member.id),
            Plain("Post [/confirm] to continue")
        ]))
        @Waiter.create_using_function([GroupMessage])
        def waiter(
            event : GroupMessage, waiter_group : Group, 
            waiter_member : Member, waiter_message : MessageChain
        ):
            if all([
                waiter_member.id == member.id,
                waiter_group.id == group.id,
                waiter_message.asDisplay() == "/confirm"
            ]):
                return event
        await inc.wait(waiter)
        await app.sendGroupMessage(group, MessageChain.create([
            Plain("\nCompleted")
        ]))
    elif message.asDisplay().startswith("/Menu"):
        await app.sendGroupMessage(group, MessageChain.create([
            At(member.id),
            Plain(Menu())
        ]))
    elif message.asDisplay().startswith("/求图"):
        msg = message.asDisplay()
        msg = re.split(r' +', msg)
        msg_to_send = MessageChain.create([At(member.id)])
        if msg.__len__() > 3 or msg.__len__() <= 1:
            msg_to_send.plus(MessageChain.create([Plain("\n不要搞事情! 要遵守输入格式 : '/求图 关键词 整数[可选]', 请重新输入~")]))
            await app.sendGroupMessage(group, msg_to_send)
        elif msg.__len__() == 2:
            img_url_list = await getImage.get_normal_image(msg[1])
            msg_to_send.plus(MessageChain.create([Plain("\n您要的图~ "), Image.fromNetworkAddress(img_url_list[0])]))
            await app.sendGroupMessage(group, msg_to_send)
        else :
            if re.search(r'\D', msg[2]) != None:
                await app.sendGroupMessage(group, msg_to_send.plus(MessageChain.create([Plain("\n您输入的数字有问题哦~, 请您重新输入 ")])))
            else:
                num = int(msg[2])
                img_url_list = await getImage.get_normal_image(msg[1], num)
                msg_to_send = ""
                if img_url_list.__len__() < num:
                    msg_to_send.plus(MessageChain.create([Plain("\n您要的太多了，小的只能找到这么多[卑微~]")]))
                else:
                    msg_to_send.plus(MessageChain.create([Plain("\n您要的图~ ")]))
                for i in range(0, img_url_list.__len__()):
                    try:
                        msg_to_send.plus(MessageChain.create([Image.fromNetworkAddress(img_url_list[i])]))
                        await app.sendGroupMessage(group, msg_to_send)
                    except aiohttp.client_exceptions.InvalidURL:
                        pass
    elif message.asDisplay().startswith("/天气"):
        msg = message.asDisplay()
        msg = re.split(r' +', msg)
        if (msg.__len__() != 2):
            await app.sendGroupMessage(group, MessageChain.create([
                At(member.id),
                Plain("不要搞事情！ 看好输入格式 : '/天气 城市', 请重新输入~")
            ]))
        else:
            city = msg[1]
            city_code = city_code_dict[city]
            wea_list = await getWeather.get_weather(city, city_code)
            wea_dict = wea_list[1]
            string = ""
            for date in wea_dict:
                string += date + "  ".join(wea_dict[date]) + "\n"
            await app.sendGroupMessage(group, MessageChain.create([
                At(member.id),
                Plain("\n["+city+"] 近七日天气情况如下:  \n"),
                Plain(string),
                Plain("From: " + wea_list[0])
            ]))
    elif message.asDisplay().startswith("/求问"):
        msg = message.asDisplay()
        msg = re.split(r' +', msg)
        msg_to_send = MessageChain.create([At(member.id)])
        if msg.__len__() > 3 or msg.__len__() <= 1:
            msg_to_send.plus(MessageChain.create([Plain("\n不要捣乱哦，要遵守输入格式 : '/求问 第一关键词 第二关键词[Optional]', 请您重新输入一遍~")]))
            await app.sendGroupMessage(group, msg_to_send)
        else:
            firstKeyword = msg[1]
            if firstKeyword in NameList:
                msg_to_send.plus(MessageChain.create([Plain("\n" + firstKeyword + "太丑了，我才不查他呢，哼~")]))
                await app.sendGroupMessage(group, msg_to_send)
            elif firstKeyword in SpecialNameList:
                msg_to_send.plus(MessageChain.create([Plain("\n噢，你说" + firstKeyword + "啊，她是我主人的儿子[doge]~")]))
                await app.sendGroupMessage(group, msg_to_send)
            elif firstKeyword == myconfigs["OwnerName"] and msg.__len__() == 2:
                msg_to_send.plus(MessageChain.create([Plain("\n一边去！我主人可不是你想问就能问的~")]))
                await app.sendGroupMessage(group, msg_to_send)
            elif firstKeyword == "白敬亭女朋友":
                msg_to_send.plus(MessageChain.create([Plain("\n白敬亭现在还单身哦~~你每多zkk吃一顿饭, 你的希望就大一些[doge]")]))
                await app.sendGroupMessage(group, msg_to_send)
            elif firstKeyword == "张丹" and msg.__len__() == 2:
                msg_to_send.plus(MessageChain.create([Plain("\n{}".format(SpecialMessage[firstKeyword]))]))
                await app.sendGroupMessage(group, msg_to_send)
            elif firstKeyword == "陈露" and msg.__len__() == 2:
                msg_to_send.plus(MessageChain.create([Plain("\n{}".format(SpecialMessage[firstKeyword]))]))
                await app.sendGroupMessage(group, msg_to_send)
            else:
                if msg.__len__() == 3:
                    ans = await Baidupedia.QueryPedia(firstKeyword, msg[2])
                else :
                    ans = await Baidupedia.QueryPedia(firstKeyword)
                brief_introduction = ans[0]
                movie_url = ans[1]
                msg_to_send.plus(MessageChain.create([Plain("\n" + brief_introduction + "\n")]))
                await app.sendGroupMessage(group, msg_to_send)
                await asyncio.sleep(1.5)
                if(movie_url != ""):
                    await app.sendGroupMessage(group, MessageChain.create([
                    Plain(f'有关 [{firstKeyword}] 的短视频介绍在这里哦~\n' + movie_url)
                ]))
    elif message.asDisplay().startswith("/点歌"):
        msg = message.asDisplay()
        msg = re.search(r'(《.*》)', msg)
        song_data_dict = await getMusic.getKugouMusic(msg[1])
        msg_to_send = "\n{}\n歌手：{}\n专辑：{}\n".format(song_data_dict["song_name"], song_data_dict["singer_name"], song_data_dict["album_name"])
        await app.sendGroupMessage(group, MessageChain.create([
            At(member.id),
            Plain(msg_to_send),
            Image.fromNetworkAddress(song_data_dict["img_url"]),
            Plain(song_data_dict["lyrics"]),
            Plain(song_data_dict["song_url"])
        ]))
    elif message.has(At) and message.get(At)[0].target == myconfigs["account"]:
        await app.sendGroupMessage(group, MessageChain.create([
            At(member.id),
            Plain(Menu())
        ]))

    elif message.asDisplay().startswith("/微博"):
        msg = message.asDisplay()
        msg = re.split(r' +', msg)
        if msg.__len__() > 3 or msg.__len__() <= 1:
            await app.sendGroupMessage(group, MessageChain.create([
                At(member.id),
                Plain("\n小伙子你不讲武德, 你把输入格式看看好: '/微博 昵称 数量(1~10|按时序先后)")
            ]))
        else:
            nickname = msg[1]
            if msg.__len__() == 2:
                num = 2
            else:
                num = int(msg[2])
            blog_list = await getSinaweibo.get_blog(nickname, num)
            msg_to_send = MessageChain.create([(At(member.id))])
            if blog_list.__len__() == 0:
                msg_to_send.plus(MessageChain.create([Plain(f"抱歉, [{nickname}]好像不想被您知道~~")]))
                await app.sendGroupMessage(group, msg_to_send)
            if num == 0:
                msg  = "[昵称] : {}\n".format(blog_list[0]["nickname"])
                msg += "[关注数] : {}\n".format(blog_list[0]["follow_count"])
                msg += "[粉丝数] : {}\n".format(blog_list[0]["followers_count"])
                msg += "[微博认证] : {}\n".format(blog_list[0]["verified_reason"]) 
                msg += "[简介] : {}\n".format(blog_list[0]["description"])
                msg += "[头像] : \n"
                msg_to_send.plus(MessageChain.create([Plain(msg)]))
                msg_to_send.plus(MessageChain.create([Image.fromNetworkAddress(blog_list[0]["profile_img"])]))
                await app.sendGroupMessage(group, msg_to_send)
            else:
                if blog_list.__len__() < num:
                    num = blog_list.__len__()
                    msg_to_send.plus(MessageChain.create([Plain(f"\n抱歉，暂时只能找到{num}条微博")]))
                for i in range(0, num):
                    item = blog_list[i]
                    msg_st    = "\n"
                    msg_st   += "[Content] : \n{}\n".format(item["blog_text"])
                    msg_end   = "[Time] : {}\n".format(item["blog_time"])
                    msg_end  += "[Source] : {}\n".format(item["source"])
                    msg_end  += "[Likes] : {}\n".format(item["attitudes_count"])
                    msg_end  += "[Comments] : {}\n".format(item["comments_count"])
                    msg_end  += "[Reposts] : {}\n".format(item["reposts_count"])
                    msg_to_send.plus(MessageChain.create([Plain(msg_st)]))
                    if item["blog_imgs"].__len__() > 0:
                        msg_to_send.plus(MessageChain.create([Image.fromNetworkAddress(img) for img in item["blog_imgs"]]))
                    msg_to_send.plus(MessageChain.create([Plain(msg_end)]))
                await app.sendGroupMessage(group, msg_to_send)

async def init_blog_id_set(blog_id_set : Set):
    try:
        with open("blog_id.txt", 'r') as file:
            for line in file:
                tempStr = re.sub(r'\n', '', line)
                blog_id_set.add(tempStr)
    except:
        pass
    print(blog_id_set)

# 定时模块！！ Thanks for TA
async def routine_group_task(
    app : GraiaMiraiApplication
):
    await asyncio.sleep(2.5)
    await MonitorSina.Monitor("Sch_zh", app, 1312213379, 1050869147, blog_id_set)
    loop.create_task(routine_group_task(app))

loop.create_task(init_blog_id_set(blog_id_set))
loop.create_task(routine_group_task(app))

@bcc.receiver("FriendMessage")
async def friend_message_listener(
    message : MessageChain, 
    app: GraiaMiraiApplication, 
    friend: Friend
):
    if message.asDisplay().startswith("/天气" or "/weather"):
        msg = message.asDisplay()
        msg = re.split(r' +', msg)
        if (msg.__len__() != 2):
            await app.sendFriendMessage(friend, MessageChain.create([
                Plain("不要捣乱哦，要遵守输入格式 : '/天气 城市', 请您重新输入~"),
            ]))
        else:
            city = msg[1]
            city_code = city_code_dict[city]
            wea_list = await getWeather.get_weather(city, city_code)
            wea_dict = wea_list[1]
            string = ""
            for date in wea_dict:
                string += date + "  ".join(wea_dict[date]) + "\n"
            await app.sendFriendMessage(friend, MessageChain.create([
                Plain("["+city+"]  近七日天气情况如下:  \n"),
                Plain(string),
                Plain("From: " + wea_list[0])
            ]))

app.launch_blocking()

import asyncio
import re
import aiohttp
from config import configs as myconfigs
from config import NameList as NameList
from config import SpecialNameList as SpecialNameList
from config import SpecialMessage as SpecialMessage
from graia.broadcast import Broadcast
from graia.application import GraiaMiraiApplication, Session
from graia.application.message.chain import MessageChain 
from graia.application.group import Group, Member
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter
from graia.application.message.elements.internal import Plain, At, Image, App, Xml, Json
from graia.application.friend import Friend
from graia.application.event.messages import GroupMessage 
from function.getImage import get_normal_image
from function.getWeather import get_weather, get_city_code
from function.Baidupedia import QueryPedia, get_movie
from function.getMusic import getKugouMusic

def Menu() -> str:
    menu = "\n"
    menu += f"我是{myconfigs['BotName']}, 我可以帮您做的事情有:\n"
    menu += "1. [查询天气]                           格式：   /天气 城市\n"
    menu += "2. [图片]                                  格式：   /求图 关键词 整数[Optional]\n"
    menu += "3. [解释您想知道的词语]         格式:      /求问 第一关键词 第二关键词[Optional]\n"
    menu += "4. [点歌]                                  格式:      /点歌《歌名》\n"
    menu += "5. [未完待续……]\n"
    menu += "您有什么需要尽管吩咐~~"
    return menu

city_code_dict = get_city_code()

loop = asyncio.get_event_loop()
bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host = myconfigs["host"],   # 填入 httpapi 服务运行的地址
        authKey = myconfigs["authKey"],     # 填入 authKey
        account = myconfigs["account"],     # 你的机器人的 qq 号
        websocket = True    # Graia 已经可以根据所配置的消息接收的方式来保证消息接收部分的正常运作.
    )
)
inc = InterruptControl(bcc)

# 函数中
# 冒号后面跟的是参数的建议类型
# -> 后面跟的是返回值的建议类型

@bcc.receiver("GroupMessage")
async def group_messsage_handler(
    message : MessageChain, app : GraiaMiraiApplication, 
    group : Group, member : Member
):
    if message.asDisplay().startswith("/need_confirm"):
        await app.sendGroupMessage(group, MessageChain.create([
            At(member.id),
            Plain("发送 /confirm 以继续运行")
        ]))
        # listening_events 为 GroupMessage
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
            Plain("执行完毕")
        ]))
    elif message.asDisplay().startswith("/Menu"):
        await app.sendGroupMessage(group, MessageChain.create([
            At(member.id),
            Plain(Menu())
        ]))
    elif message.asDisplay().startswith("/求图"):
        msg = message.asDisplay()
        msg = re.split(r' +', msg)
        if msg.__len__() > 3 or msg.__len__() <= 1:
            await app.sendGroupMessage(group, MessageChain.create([
                At(member.id),
                Plain("\n不要捣乱哦，要遵守输入格式 : '/求图 关键词 整数[可选]', 请您重新输入~")
            ]))
        elif msg.__len__() == 2:
            img_url_list = await get_normal_image(msg[1])
            await app.sendGroupMessage(group, MessageChain.create([
                At(member.id),
                Plain("\n您要的图~ "),
                Image.fromNetworkAddress(img_url_list[0])
            ]))
        else :
            if re.search(r'\D', msg[2]) != None:
                await app.sendGroupMessage(group, MessageChain.create([
                At(member.id),
                Plain("\n您输入的数字有问题哦~, 请您重新输入 "),
            ]))
            else :
                num = int(msg[2])
            img_url_list = await get_normal_image(msg[1], num)
            msg_to_send = ""
            if img_url_list.__len__() < num:
                await app.sendGroupMessage(group, MessageChain.create([
                    At(member.id),
                    Plain("\n您要的太多了，小的只能找到这么多[卑微~]")
                ]))
            else:
                await app.sendGroupMessage(group, MessageChain.create([
                    At(member.id),
                    Plain("\n您要的图~ ")
                ]))
            i = 0
            while i < img_url_list.__len__():
                # 有异常时 else 不执行， 无异常时 else 执行
                try:
                    await app.sendGroupMessage(group, MessageChain.create([
                        Image.fromNetworkAddress(img_url_list[i])
                        ]))
                except aiohttp.client_exceptions.InvalidURL:
                    pass 
                finally:
                    i += 1
    elif message.asDisplay().startswith("/天气"):
        msg = message.asDisplay()
        msg = re.split(r' +', msg)
        if (msg.__len__() != 2) :
            await app.sendGroupMessage(group, MessageChain.create([
                At(member.id),
                Plain("不要捣乱哦，要遵守输入格式 : '/天气 城市', 请您重新输入~")
            ]))
        else :
            city = msg[1]
            city_code = city_code_dict[city]
            wea_list = await get_weather(city, city_code)
            wea_dict = wea_list[1]
            string = ""
            for date in wea_dict:
                string += date + "  ".join(wea_dict[date]) + "\n"
            await app.sendGroupMessage(group, MessageChain.create([
                At(member.id),
                Plain("\n["+city+"]  近七日天气情况如下:  \n"),
                Plain(string),
                Plain("数据来源: 中国天气网 " + wea_list[0])
            ]))
    elif message.asDisplay().startswith("/求问"):
        msg = message.asDisplay()
        msg = re.split(r' +', msg)
        if msg.__len__() > 3 or msg.__len__() <= 1:
            await app.sendGroupMessage(group, MessageChain.create([
                At(member.id),
                Plain("\n不要捣乱哦，要遵守输入格式 : '/求问 第一关键词 第二关键词[Optional]', 请您重新输入一遍~")
            ]))
        else :
            firstKeyword = msg[1]
            if firstKeyword in NameList:
                await app.sendGroupMessage(group, MessageChain.create([
                    At(member.id),
                    Plain("\n" + firstKeyword + "太丑了，我才不查他呢，哼~")
                ]))
            elif firstKeyword in SpecialNameList:
                await app.sendGroupMessage(group, MessageChain.create([
                    At(member.id),
                    Plain("\n噢，你说" + firstKeyword + "啊，她是我主人的儿子[doge]~")
                ]))
            elif firstKeyword == myconfigs["OwnerName"]:
                await app.sendGroupMessage(group, MessageChain.create([
                    At(member.id),
                    Plain("\nwoo~，你也想知道他嘛，我的主人超强的~")
                ]))
            elif firstKeyword == "白敬亭女朋友":
                await app.sendGroupMessage(group, MessageChain.create([
                    At(member.id),
                    Plain("\n他现在还单身哦~~你要加油啦！")
                ]))
            elif firstKeyword == "张丹":
                await app.sendGroupMessage(group, MessageChain.create([
                    At(member.id),
                    Plain("\n{}".format(SpecialMessage[firstKeyword]))
                ]))
            elif firstKeyword == "陈露":
                await app.sendGroupMessage(group, MessageChain.create([
                    At(member.id),
                    Plain("\n{}".format(SpecialMessage[firstKeyword]))
                ]))
            else:
                if msg.__len__() == 3:
                    ans = await QueryPedia(firstKeyword, msg[2])
                else :
                    ans = await QueryPedia(firstKeyword)
                brief_introduction = ans[0]
                movie_url = ans[1]
                await app.sendGroupMessage(group, MessageChain.create([
                    At(member.id),
                    Plain("\n" + brief_introduction)
                ]))
                if(movie_url != "") :
                    await app.sendGroupMessage(group, MessageChain.create([
                    Plain(f'有关 [{firstKeyword}] 的短视频介绍在这里哦~\n' + movie_url)
                ]))
    elif message.asDisplay().startswith("/点歌"):
        msg = message.asDisplay()
        msg = re.search(r'(《.*》)', msg)
        song_data_dict = await getKugouMusic(msg[1])
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

@bcc.receiver("FriendMessage")
async def friend_message_listener(
    message : MessageChain, 
    app: GraiaMiraiApplication, 
    friend: Friend
):
    if message.asDisplay().startswith("/天气"):
        msg = message.asDisplay()
        msg = re.split(r' +', msg)
        if (msg.__len__() != 2) :
            await app.sendFriendMessage(friend, MessageChain.create([
                Plain("不要捣乱哦，要遵守输入格式 : '/天气 城市', 请您重新输入~"),
            ]))
        else :
            city = msg[1]
            city_code = city_code_dict[city]
            wea_list = await get_weather(city, city_code)
            wea_dict = wea_list[1]
            string = ""
            for date in wea_dict:
                string += date + "  ".join(wea_dict[date]) + "\n"
            await app.sendFriendMessage(friend, MessageChain.create([
                Plain("["+city+"]  近七日天气情况如下:  \n"),
                Plain(string),
                Plain("数据来源: 中国天气网 " + wea_list[0])
            ]))

app.launch_blocking()

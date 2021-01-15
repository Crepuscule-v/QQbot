import asyncio
import getImage
import re
from config import configs as myconfigs
from graia.broadcast import Broadcast
from graia.application import GraiaMiraiApplication, Session
from graia.application.message.chain import MessageChain 
from graia.application.group import Group, Member
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter
from graia.application.message.elements.internal import Plain, At, Image, App
from graia.application.friend import Friend
from graia.application.event.messages import GroupMessage 
from weather import get_weather, get_city_code
from Baidupedia import QueryPedia, get_movie


def Menu() -> str:
    menu = '''
我可以帮您做的事情有:
1. [查询天气]                 格式：   /天气 城市
2. [来一张NBA球星图]           格式：   /NBA球星照
3. [解释您想知道的词语]        格式:    /求问 关键词
3. [...开发中] '''
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
    
    elif message.asDisplay().startswith("/menu"):
        await app.sendGroupMessage(group, MessageChain.create([
            At(member.id),
            Plain(Menu())
        ]))
    
    elif message.asDisplay().startswith("/NBA球星照片"):
        img_url = await getImage.get_d77_image()
        await app.sendGroupMessage(group, MessageChain.create([
            At(member.id),
            Image.fromNetworkAddress(img_url)
        ]))
    
    elif message.asDisplay().startswith("/天气"):
        msg = message.asDisplay()
        msg = re.split(r' +', msg)
        if (msg.__len__() != 2) :
            await app.sendGroupMessage(group, MessageChain.create([
                At(member.id),
                Plain("您的查询格式错误哦, 应该为'/天气 城市', 请您重新输入~")
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
        if (msg.__len__() != 2):
            await app.sendGroupMessage(group, MessageChain.create([
                At(member.id),
                Plain("您的查询格式是错误的哦, 应该为'/求问 关键词', 请您重新输入一遍~")
            ]))
        else :
            Keyword = msg[1]
            if Keyword == "李培宁" or Keyword == "刘培栋" or Keyword == "龙儿子":
                await app.sendGroupMessage(group, MessageChain.create([
                    At(member.id),
                    Plain("\n他太菜了，我才不查他呢，哼~")
                ]))
            elif Keyword == myconfigs["OwnerName"]:
                await app.sendGroupMessage(group, MessageChain.create([
                    At(member.id),
                    Plain("\nwoooo~，你也认识他嘛！他超帅的！")
                ]))
            else:
                ans = QueryPedia(Keyword)
                ans_url = get_movie(Keyword)
                await app.sendGroupMessage(group, MessageChain.create([
                    At(member.id),
                    Plain("\n" + ans),
                ]))
                await asyncio.sleep(2)
                if(ans_url != "") :
                    await app.sendGroupMessage(group, MessageChain.create([
                    Plain(f'有关 [{Keyword}] 的短视频介绍在这里哦~\n' + ans_url)
                ]))
    # elif message.asDisplay().startswith("/ban"):
    #     if (message.has(At)):
            # At_list = message.get(At)
            





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
                Plain("您的查询格式是错误的哦, 应该为'/天气 城市', 请您重新输入~")
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

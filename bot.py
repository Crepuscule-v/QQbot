import asyncio
from config import configs as myconfigs
from graia.broadcast import Broadcast
from graia.application import GraiaMiraiApplication, Session
from graia.application.message.chain import MessageChain 
from graia.application.group import Group, Member
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter
from graia.application.message.elements.internal import Plain, At
from graia.application.friend import Friend
from graia.application.event.messages import GroupMessage 

def Menu():
    menu = '''
我现在可以帮您做的事情有：
    1. 打刘培栋
    2. 骂刘培栋
    3. 一边打一遍骂刘培栋'''
    return menu

loop = asyncio.get_event_loop()
bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host = myconfigs["host"], # 填入 httpapi 服务运行的地址
        authKey = myconfigs["authKey"], # 填入 authKey
        account = myconfigs["account"], # 你的机器人的 qq 号
        websocket = True # Graia 已经可以根据所配置的消息接收的方式来保证消息接收部分的正常运作.
    )
)
inc = InterruptControl(bcc)

# app : GraiaMiraiApplication
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
    
    if message.asDisplay().startswith("/menu"):
        await app.sendGroupMessage(group, MessageChain.create([
            At(member.id),
            Plain(Menu())
        ]))


@bcc.receiver("FriendMessage")
async def friend_message_listener(app: GraiaMiraiApplication, friend: Friend):
    await app.sendFriendMessage(friend, MessageChain.create([Plain("Hello, World!")]))

app.launch_blocking()
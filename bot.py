import asyncio
from graia.broadcast import Broadcast
from graia.scheduler import GraiaScheduler
from graia.scheduler import timers
from graia.application import GraiaMiraiApplication, Session
from graia.application.message.elements.internal import Plain
from graia.application.message.elements.internal import Image
from graia.application.message.elements.internal import At
from graia.application.message.elements.internal import App
from graia.application.message.elements.internal import Source
from graia.application.event.messages import *
from graia.application.event.mirai import *
from graia.application.exceptions import *

loop = asyncio.get_event_loop()

bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host="http://localhost:8080", # 填入 httpapi 服务运行的地址
        authKey="INITKEY8HenxCwF", # 填入 authKey
        account=2121784398, # 你的机器人的 qq 号
        websocket=True # Graia 已经可以根据所配置的消息接收的方式来保证消息接收部分的正常运作.
    )
)
scheduler = GraiaScheduler(loop, bcc)

# 秒 分 时 一个月的第几天 月份 星期几
@scheduler.schedule(timers.crontabify("* * * * * *"))
async def declare_dragon():
    groups = await app.groupList()
    print(groups)

loop.run_forever()

# @bcc.receiver("FriendMessage")
# async def friend_message_listener(
#     app: GraiaMiraiApplication, 
#     friend: Friend
# ):
#     await app.sendFriendMessage(friend, MessageChain.create([
#         Plain("Hello, World!"),
#     ]))

# inc = InterruptControl(bcc)

# @bcc.receiver("GroupMessage")
# async def group_message_handler(
#     message : MessageChain,
#     app : GraiaMiraiApplication,
#     group : Group, 
#     member : Member,
# ):
#     if message.asDisplay().startswith("/test_need_confirm"):
#         await app.sendGroupMessage(group, MessageChain.create([
#             At(member.id), Plain("  发送 /confirm 以继续运行")
#         ]))
#         @Waiter.create_using_function([GroupMessage])
#         def waiter(
#             event: GroupMessage, waiter_group: Group,
#             waiter_member: Member, waiter_message: MessageChain
#         ):
#             if all([
#                 waiter_group.id == group.id,
#                 waiter_member == member.id,
#                 waiter_message.asDisplay().startswith("/confirm")
#             ]):
#                 return event
        
#         await inc.wait(waiter)
#         await app.sendGroupMessage(group, MessageChain,create([
#             Plain("执行完毕.")
#         ]))

# app.launch_blocking()
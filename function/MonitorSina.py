# -*- coding:utf-8 -*-

# @Time    : 2021/1/20
# @Author  : Crepuscule-v
# @FileName: MonitorSina.py

from graia.application.event.messages import GroupMessage 
from function.getSinaweibo import get_blog, get_blog_from_id
from graia.application import GraiaMiraiApplication
from graia.application.message.chain import MessageChain 
from graia.application.message.elements.internal import Plain, At, Image
import asyncio
from typing import List, Dict, Set
import time

async def raw_monitor(nickname : str, blog_id_set : Set) -> List:
    '''
    用于实时监控某个人的微博动态, 一旦有新微博发出，向指定群组中发送通知
    '''
    blog_list = await get_blog(nickname)
    new_blog_id_list = []
    for blog in blog_list:
        if blog["blog_id"] not in blog_id_set:
            new_blog_id_list.append(blog["blog_id"])
            blog_id_set.add(blog["blog_id"])
    flag = False
    blog_info_list = []  # 存放新的blog_info
    if new_blog_id_list.__len__() != 0:
        for blog_id in new_blog_id_list:
            single_blog_info = await get_blog_from_id(blog_id)
            if single_blog_info is not {}:
                flag = True
                blog_info_list.append(single_blog_info)
    # 把 blogid 写入文件中, 以防下次用的时候从头开始都当成新微博
    if flag:
        try :
            with open("blog_id.txt", 'a') as file:
                for item in blog_info_list:
                    file.write('\n')
                    file.write(item["blog_id"])
        except:
            print("[文件写入失败, pos = 2]")
    return [flag, blog_info_list]

async def Monitor(
    nickname : str, app : GraiaMiraiApplication, 
    QQ_id : int, Group_id : int,
    blog_id_set : Set
) -> List:
    '''
    每隔一段时间监控一次, 如有新微博，发送给指定群组, 并@指定人
    '''
    try :
        tempList = await raw_monitor(nickname, blog_id_set)
    except:
        tempList = [False, []]
    if tempList[0] is True:
        new_blog_list = tempList[1]
        msg_to_send = MessageChain.create([At(QQ_id)])
        msg_st  = "\n"
        msg_st += f"您关注的[ {nickname} ]有新动态哦, 请注意查收~~\n"
        msg_to_send.plus(MessageChain.create([Plain(msg_st)]))
        for blog in new_blog_list:
            try:
                msg_end   = ""
                msg_end  += "[Content] : \n{}\n".format(blog["blog_text"])
                msg_end  += "[Time] : {}\n".format(blog["blog_time"])
                msg_end  += "[Source] : {}\n".format(blog["source"])
                msg_end  += "[Likes] : {}\n".format(blog["attitudes_count"])
                msg_end  += "[Comments] : {}\n".format(blog["comments_count"])
                msg_end  += "[Reposts] : {}\n".format(blog["reposts_count"])
                if blog["blog_imgs"].__len__() > 0:
                    msg_to_send.plus(MessageChain.create([Image.fromNetworkAddress(img) for img in blog["blog_imgs"]]))
                msg_to_send.plus(MessageChain.create([Plain(msg_end)]))
            except:
                print("[发送错误, pos = 1]")
        await app.sendGroupMessage(Group_id, msg_to_send)
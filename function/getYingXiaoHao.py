# -*- coding:utf-8 -*-
# @author: Crepuscule_v
# @time  : 2021/1/22
# @file  : getYingXiaoHao.py

'''
给定关键词，自动生成一篇营销号文章
'''

import asyncio

async def getPassage(obj : str, event : str, anotherWay : str) -> str:
    passage = ""
    passage += f"{obj}{event}是怎么回事呢？"
    passage += f"{obj}相信大家都很熟悉, 但是{obj}{event}是怎么回事呢？下面小编就来带大家一起了解吧。"
    passage += f"{obj}{event}其实就是{anotherWay},大家可能会很惊讶，{event}怎么会是{anotherWay}呢? 但事实就是这样。"
    passage += f"这就是关于{obj}{event}的事情。大家有什么想法呢? 欢迎在评论区告诉小编一起讨论哦!"
    print(passage)
    return passage

# DEBUG
if __name__ == "__main__":
    asyncio.run(getPassage("xxx", "高数挂了", "高数不及格"))
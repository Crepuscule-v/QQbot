# -*- coding:utf-8 -*-

# @author : Crepuscule_v
# @time   : 2021/1/22
# @file   : getCouplet.py

'''
实现自动对下联功能
'''
import requests
import json
import random
import asyncio

async def getXiaLian(shanglian : str) -> str:
    Posturl = "http://duilian.msra.cn/app/CoupletsWS_V2.asmx/GetXiaLian"
    RequestPayload = {
        "shanglian": f"{shanglian}", 
        "xialianLocker": "0" * shanglian.__len__(),
        "isUpdate": "false"
    }
    headers = {
        "Content-Type" : "application/json; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"
    }
    r = requests.post(Posturl, data=json.dumps(RequestPayload), headers=headers)
    r.encoding = 'utf-8'
    with open("test.json", "a", encoding='utf-8') as file:
        file.write(r.text)
    XialianWellKnownSets = json.loads(r.text)["d"]["XialianWellKnownSets"]
    if XialianWellKnownSets is not None:
        XialianWellKnownSets = XialianWellKnownSets[0]
        XialianCandidates = XialianWellKnownSets["XialianCandidates"]
        xialianStr = XialianCandidates[random.randint(0, XialianCandidates.__len__() - 1)]
    else:
        XialianSystemGeneratedSets = json.loads(r.text)["d"]["XialianSystemGeneratedSets"][0]
        WordCandidatesInColumnOrder = XialianSystemGeneratedSets["WordCandidatesInColumnOrder"]
        xialianStr = ""
        for item in WordCandidatesInColumnOrder:
            xialianStr += item[random.randint(0, item.__len__() - 1)]
    print(xialianStr)
    return xialianStr

if __name__ == "__main__":
    asyncio.run(getXiaLian("姑苏城外寒山寺"))


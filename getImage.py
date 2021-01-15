import re
import requests
import random
import asyncio

async def get_d77_image():
    url = "https://image.baidu.com/search/index?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=2&nc=1&ie=utf-8&word=%E4%B8%9C%E5%A5%91%E5%A5%87"
    headers = {
        "Host" : "image.baidu.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cache-Control": "max-age=0",
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "Cookie": "BDqhfp=%E4%B8%9C%E5%A5%91%E5%A5%87%26%26NaN-1undefined%26%260%26%261; BIDUPSID=597345ED74CF4E3930C64240937C9235; PSTM=1570242689; BDUSS=lpZXpPWmd3S3d6aTdSTnFQeTFqZ3J1SkZpZDhQT05xbWxmTE1USEpYS3NIbHRmRVFBQUFBJCQAAAAAAQAAAAEAAAAVPnMcd2VfY29vcGVyYXRlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKyRM1-skTNfcl; BDUSS_BFESS=lpZXpPWmd3S3d6aTdSTnFQeTFqZ3J1SkZpZDhQT05xbWxmTE1USEpYS3NIbHRmRVFBQUFBJCQAAAAAAQAAAAEAAAAVPnMcd2VfY29vcGVyYXRlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKyRM1-skTNfcl; BAIDUID=F4E0498C3C26DA8FA4AF2DF0A945A12C:FG=1; indexPageSugList=%5B%22Css%E8%83%8C%E6%99%AF%E5%A6%82%E4%BD%95%E4%BD%BF%E7%94%A8%E8%87%AA%E5%B7%B1%E7%9A%84%E5%9B%BE%E7%89%87%22%2C%22%E7%8B%AC%E8%A1%8C%E4%BE%A0logo%22%5D; __yjs_duid=1_7a971a10c081c6e03fb4c01476b584381608970232503; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; H_PS_PSSID=33425_33479_33418_33344_31254_33284_33286_26350_33370; delPer=0; PSINO=5; BAIDUID_BFESS=F4E0498C3C26DA8FA4AF2DF0A945A12C:FG=1; BDRCVFR[dG2JNJb_ajR]=mk3SLVN4HKm; BDRCVFR[-pGxjrCMryR]=mk3SLVN4HKm; BCLID=11319232103746959752; BDSFRCVID=W0FOJeC62uhhJpJe0DQFh2dbgm5rbsOTH6f3sISw2YGjVnjSaYvgEG0P8U8g0KubG3lmogKKyeOTHu0F_2uxOjjg8UtVJeC6EG0Ptf8g0f5; H_BDCLCKID_SF=tbCt_D0MJDI3HJTg-J7hbDCbblrt2D62aJ3UopQvWJ5TMCoGM-7kKMI8D-OI0tkH5IrMWC5-KtOcShPCb6b5yqtWDRrxaq5X2H7Kh4Qj3l02VKnae-t2ynLVQNbQ24RMW2380l7mWPK2sxA45J7cM4IseboJLfT-0bc4KKJxbnLWeIJIjj6jK4JKjH-jtf5; BCLID_BFESS=11319232103746959752; BDSFRCVID_BFESS=W0FOJeC62uhhJpJe0DQFh2dbgm5rbsOTH6f3sISw2YGjVnjSaYvgEG0P8U8g0KubG3lmogKKyeOTHu0F_2uxOjjg8UtVJeC6EG0Ptf8g0f5; H_BDCLCKID_SF_BFESS=tbCt_D0MJDI3HJTg-J7hbDCbblrt2D62aJ3UopQvWJ5TMCoGM-7kKMI8D-OI0tkH5IrMWC5-KtOcShPCb6b5yqtWDRrxaq5X2H7Kh4Qj3l02VKnae-t2ynLVQNbQ24RMW2380l7mWPK2sxA45J7cM4IseboJLfT-0bc4KKJxbnLWeIJIjj6jK4JKjH-jtf5; ZD_ENTRY=baidu; userFrom=www.baidu.com; BA_HECTOR=a5a021a12h8h218gat1g022ok0q; ab_sr=1.0.0_NmQyOTgwYzQ2MGQxNmNhMTFkNDU0NTM3OWUxYWQ5YmExNzRhMmViOWI1ZTE3MTE0ZTAxZjZkZDk3NzVkOWNmY2ZmNTZlNTNiOTIxNTVjMTgyNjVjYWU0ZTgxOTdiNzJhZTEyNjNkZThlNTQ4ZTUzNTcxNTU2YjYyNjM3MGYwNzk="
    }
    response = requests.get(url = url, headers = headers)
    response.encoding = "utf-8"
    res = response.text
    url_list = re.findall(r'"thumbURL":"(.*?)"', res)
    url_num = url_list.__len__()
    rnd_idx = random.randint(0, url_num)
    return url_list[rnd_idx]

import re
import asyncio
import requests
import bs4
import time

def QueryPedia(keyword : str) -> str:
    url_1 = "https://baike.baidu.com/item/" + keyword
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
        "Host": "baike.baidu.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Cookie": "BIDUPSID=91A1503D5D79FE71F78910CD28127214; PSTM=1604569164; BAIDUID=91A1503D5D79FE715477842ED026ADF5:FG=1; __yjs_duid=1_fca8a7300c7e9a3fecb7e7152a9546761608821539130; BDUSS=kNRU0RTVHctYVZHOWZ0Z3BoVWJTb3BLc21KdzVXaFhUV014R2dVMnhuSXBaeVZnRVFBQUFBJCQAAAAAAQAAAAEAAAAVPnMcd2VfY29vcGVyYXRlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACna~V8p2v1fY; BDUSS_BFESS=kNRU0RTVHctYVZHOWZ0Z3BoVWJTb3BLc21KdzVXaFhUV014R2dVMnhuSXBaeVZnRVFBQUFBJCQAAAAAAQAAAAEAAAAVPnMcd2VfY29vcGVyYXRlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACna~V8p2v1fY; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; H_PS_PSSID=33423_33359_33273_31660_33287_26350_33268; delPer=0; PSINO=5; BAIDUID_BFESS=91A1503D5D79FE715477842ED026ADF5:FG=1; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; BA_HECTOR=al850l25818gak2gee1g036ar0r; ab_sr=1.0.0_NGMyZmY5ZmRhZDJmNGM3NjlmNjM5ZmJjZTJjZGI3MTk1ZTcxZTJlYTMyMDY5MWM1NWE2Y2U3YzFlMDcwNDFlZTlkZWY5OGNiZGU3NTBmMTE2MTllNTAyNTMyNWY4Y2ZiYzU3ZTc3ZWNlNTM1NGQ3MTFlNDg2YjY3MWJiNzI2OTI=",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "no-cache",
    }
    r = requests.get(url_1, headers = headers)
    r.encoding = "utf-8"
    soup = bs4.BeautifulSoup(r.text, features="html.parser")
    # with open("html.txt", mode="w") as file:
    #     file.write(soup.prettify())
    lemma_summary = soup.find("div", class_ = "lemma-summary")
    if lemma_summary == None: 
        return "您查询的内容不存在哦~"
    para = lemma_summary.find_all("div", class_ = "para")
    ans = ""
    for item in para:
        ans += item.get_text()
    ans = re.sub(r'\[.*\]|\s', '', ans)
    return ans

def get_movie(keyword : str):
    url_1 = "https://baike.baidu.com/item/" + keyword
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
    }
    r_1 = requests.get(url_1, headers = headers)
    r_1.encoding = 'utf-8'
    # 格式 c.initialize({"secondsKnow":[{"videoSrc":{"type":"baikePlayer","secondKind":"1","secondId":
    secondId = re.search(r'{"secondsKnow":\[{"videoSrc":{"type":"baikePlayer","secondKind":"1","secondId":(\d+?),', r_1.text)
    if secondId != None :
        secondId = secondId.group(1)
    else :
        return ""
    url_2 = "https://baike.baidu.com/api/wikisecond/playurl?secondId=" + secondId
    r_2 = requests.get(url_2, headers = headers)
    movie_url = re.search(r'{"mp4Url":"(.*)?",', r_2.text)
    if movie_url != None :
        movie_url = movie_url.group(1)
    else :
        return ""
    movie_url = re.sub(r'\\', "", movie_url)
    return movie_url
    # req = requests.get(movie_url, headers=headers, stream=True)
    # with(open(movie_name+'.mp4', 'wb')) as f:
    #     for chunk in req.iter_content(chunk_size=10000):  
            # if chunk:
                # f.write(chunk)


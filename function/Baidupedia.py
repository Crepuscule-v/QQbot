import re
import asyncio
import requests
import bs4
import time
from fuzzywuzzy import fuzz

headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
        "Cookie": "BIDUPSID=91A1503D5D79FE71F78910CD28127214; PSTM=1604569164; BAIDUID=91A1503D5D79FE715477842ED026ADF5:FG=1; __yjs_duid=1_fca8a7300c7e9a3fecb7e7152a9546761608821539130; BDUSS=kNRU0RTVHctYVZHOWZ0Z3BoVWJTb3BLc21KdzVXaFhUV014R2dVMnhuSXBaeVZnRVFBQUFBJCQAAAAAAQAAAAEAAAAVPnMcd2VfY29vcGVyYXRlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACna~V8p2v1fY; BDUSS_BFESS=kNRU0RTVHctYVZHOWZ0Z3BoVWJTb3BLc21KdzVXaFhUV014R2dVMnhuSXBaeVZnRVFBQUFBJCQAAAAAAQAAAAEAAAAVPnMcd2VfY29vcGVyYXRlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACna~V8p2v1fY; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; H_PS_PSSID=33423_33359_33273_31660_33287_26350_33268; delPer=0; PSINO=5; BAIDUID_BFESS=91A1503D5D79FE715477842ED026ADF5:FG=1; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; BA_HECTOR=al850l25818gak2gee1g036ar0r; ab_sr=1.0.0_NGMyZmY5ZmRhZDJmNGM3NjlmNjM5ZmJjZTJjZGI3MTk1ZTcxZTJlYTMyMDY5MWM1NWE2Y2U3YzFlMDcwNDFlZTlkZWY5OGNiZGU3NTBmMTE2MTllNTAyNTMyNWY4Y2ZiYzU3ZTc3ZWNlNTM1NGQ3MTFlNDg2YjY3MWJiNzI2OTI=",
    }

async def QueryPedia(first_keyword : str, second_keyword : str = None) -> str:
    url_1 = "https://baike.baidu.com/item/" + first_keyword
    r = requests.get(url_1, headers = headers)
    r.encoding = "utf-8"
    soup = bs4.BeautifulSoup(r.text, features="html.parser")
    best_matched_url = url_1
        # 先找 ul标签， 再找其中包含 <li class = >的标签
    if second_keyword != None:
        temp = soup.find_all(name="li", class_ = re.compile(r'.+'))
        related_terms_list = []
        for item in temp:
            if item.find(href = re.compile("item"), title = re.compile(".+")) is not None:
                related_terms_list.append(item.find(href = re.compile("item"), title = re.compile(".+")))
            elif item.find(class_ = "selected") is not None:
                extra_item = item.find(class_ = "selected")
        # 利用 fuzz 进行模糊匹配， 找出相关性最强的那一条， 然后找出它对应的url
        if related_terms_list.__len__() != 0:
            max_match_rate = fuzz.partial_ratio(related_terms_list[0]["title"], second_keyword)
            corresponding_idx = 0
            temp_idx = 0
            for term in related_terms_list:
                temp_rate = fuzz.partial_ratio(related_terms_list[temp_idx]["title"], second_keyword)
                if temp_rate > max_match_rate:
                    corresponding_idx = temp_idx
                    max_match_rate = temp_rate
                temp_idx += 1
            extra_str = extra_item.string
            # extra_item 为最开始搜到的东西, 需额外判断
            if max_match_rate == 100:
                best_matched_url = "https://baike.baidu.com" + related_terms_list[corresponding_idx]["href"]
            else:
                if max(fuzz.partial_ratio(extra_str, first_keyword), fuzz.partial_ratio(extra_str, second_keyword)) >= max_match_rate:
                    best_matched_url = url_1
                else:
                    best_matched_url = "https://baike.baidu.com" + related_terms_list[corresponding_idx]["href"]
            # 找 introdution
            r = requests.get(best_matched_url, headers = headers)
            r.encoding = "utf-8"
            soup = bs4.BeautifulSoup(r.text, features="html.parser")
    lemma_summary = soup.find("div", class_ = "lemma-summary")
    if lemma_summary == None:
        return "您查询的内容不存在哦~"
    para = lemma_summary.find_all("div", class_ = "para")
    brief_introduction = ""
    for item in para:
        brief_introduction += item.get_text()
    brief_introduction = re.sub(r'\[.*\]|\s', '', brief_introduction)
    movie_url = await get_movie(best_matched_url)
    ans = [brief_introduction, movie_url]
    return ans

async def get_movie(url_1 : str) -> str:
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

if __name__ == "__main__":
    print(asyncio.run(QueryPedia("张丹", "中科院")))
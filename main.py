#--*-- coding: utf-8 --*--

from urllib import request, parse
from http.cookiejar import CookieJar
import re
from PIL import Image
from download import Downloader

def getCaptcha(captchaURL):
    '''
        人工识别验证码
    '''
    response = request.urlopen(captchaURL)
    fp = open("captcha.jpeg", 'wb')
    fp.write(response.read())
    fp.close()
    img = Image.open("captcha.jpeg")
    img.show()
    strCaptcha = input("验证码：")
    return strCaptcha
    

def login():
    '''
        login and get cookie.
    '''
    #安装cookie_support
    cookie_support = request.HTTPCookieProcessor(CookieJar())
    opener = request.build_opener(cookie_support)
    request.install_opener(opener)
    
    #访问http://douban.com/，获得验证码id
    req = request.Request("http://douban.com/")
    response = request.urlopen(req)
    content = response.read().decode('utf-8')
    #print(content)
    #有可能没有验证码
    res = re.search(r'''"captcha-id" value="(.*)"''', content)
    try:
        captchaID = res.group(1)
        res = re.search('''src="(.*)" alt="captcha"''', content)
        captchaURL = res.group(1)
        strCaptcha = getCaptcha(captchaURL)
    except Exception:
        captchaID = ''
        strCaptcha = ''
    
    #登陆验证https://douban.com/accounts/login，获取cookie
    headers = {"cookie": '''ue="479021795@qq.com"''',
               "User-Agent": '''Mozilla/5.0 (Windows NT 6.1; rv:26.0) Gecko/20100101 Firefox/26.0''',
               "Referer": "http://www.douban.com/",
               "Connection": "keep-alive"}
    rawData = {
        "source": "index_nav",
        "form_email": "479021795@qq.com",
        "form_password": "wang52675281",}
    if captchaID:
        rawData["captcha-id"] = captchaID
        rawData["captcha-solution"] = strCaptcha
    #print(rawData)
    data = parse.urlencode(rawData).encode('utf-8')
    req = request.Request("https://www.douban.com/accounts/login", data = data, headers = headers)
    request.urlopen(req)
    
    #验证是否登陆成功
    response = request.urlopen("http://www.douban.com")
    content = response.read().decode('utf-8')
    res = re.search(r"我的豆瓣", content)
    if res:
        print("Login successfully.")
    else:
        print("Login fail.")
        

def getSongsFromInternet():
    '''
    登陆之后从网上获取歌曲列表
    '''
    response = request.urlopen("http://site.douban.com/msr/room/609573/")
    content = response.read().decode('utf-8')
    #print(content)
    
    res = re.findall(r'''href="([^ ]*)" target="_blank">(\d\d\d)～''', content)
    resURL = []
    for item in res:
        if int(item[1]) > 140:
            resURL.append(item[0])
    #print(resURL)
    
    songsList = []
    for url in resURL:
        response = request.urlopen(url)
        content = response.read().decode('utf-8')
        #print(content)
        prog = re.findall(r"http://site.douban.com/msr/widget/playlist/\d+/download\?song_id=\d+", content)
        songsList += prog
        #print(prog)
        print(url)
        
    return songsList
    

def getSongsFromLocalarea(filename):
    '''
    从本地文件读取歌曲列表
    '''
    fp = open(filename, 'r', encoding='utf-8')
    songsList = [line.strip() for line in fp]
    fp.close()
    return songsList
    

def partition(songsList):
    '''
    将所有歌曲均分到三个文件里
    '''
    fp1 = open("songsList1.txt", 'w', encoding='utf-8')
    fp2 = open("songsList2.txt", 'w', encoding='utf-8')
    fp3 = open("songsList3.txt", 'w', encoding='utf-8')
    for i in range(len(songsList)):
        if i % 3 == 0:
            fp1.write(songsList[i] + '\n')
        elif i % 3 == 1:
            fp2.write(songsList[i] + '\n')
        else:
            fp3.write(songsList[i] + '\n')
    fp1.close()
    fp2.close()
    fp3.close()
    

def main():
    login()
    #songsList = getSongsFromInternet()
    songsList = getSongsFromLocalarea("songsList.txt")
    #partition(songsList)
    downloader = Downloader(songsList)
    downloader.download(3, threadNum=10)
    #print(songsList)
    print("done.")
    

if __name__ == "__main__":
    main()
    
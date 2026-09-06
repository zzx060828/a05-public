import requests
from bs4 import BeautifulSoup
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 SLBrowser/9.0.7.12231 SLBChan/115 SLBVPV/64-bit"}
for start_num in range(0,250,25):
    response = requests.get(f"https://movie.douban.com/top250?start={start_num}",headers=headers)
    response.encoding = 'utf-8'
    print(response.status_code)
    html=response.text
    #======查看状态码的链接：developer.mozilla.org/zh-CN/docs/Web/HTTP/Status/填你的状态码======
    soup = BeautifulSoup(html,"html.parser")
    all_titles=soup.find_all("span",attrs={"class":"title"})
    for title in all_titles:
        title_string=title.string
        if "/"not in title_string:
            print(title_string)


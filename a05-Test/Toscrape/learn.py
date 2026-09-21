import requests
#======修改请求头里面的信息，将爬虫程序伪装成浏览器======
head = {"User-Agent":"Mozilla/5.0(Windows NT 10.0; Win64; x64)"}
response = requests.get("https://books.toscrape.com/")
if response.ok:
    print(response.text)
else:
    print("请求失败")
from bs4 import BeautifulSoup
import requests
content = requests.get('http://books.toscrape.com/').text
soup = BeautifulSoup(content, 'html.parser')
all_prices = soup.findAll("p",attrs={"class":"price_color"})
for price in all_prices:
    print(price.string[2:])
all_tuitles = soup.findAll("h3")
for tittle in all_tuitles:
    
    all_links = tittle.findAll("a")
    for link in all_links:
        print(link.string)
    #或者
    #link = tittle.find("a")
    #print(link.string)
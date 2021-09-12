import pandas as pd
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests

start = time.time()

headers = {
    'authority': 'scrapeme.live',
    'dnt': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'none',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
}

driver = webdriver.Chrome(
    executable_path=r"/home/paritosh/PycharmProjects/zomato/chromedriver")  # this might need a change since i am working in pycharm you might need to import os

driver.get(
    "https://www.zomato.com/bangalore/restoran")  # url of the website of particular cities you want to scrap.

time.sleep(2)  # Allow 2 seconds for the web page to (open depends on you)
scroll_pause_time = 3  # You can set your own pause time. dont slow too slow that might not able to load more data
screen_height = driver.execute_script("return window.screen.height;")  # get the screen height of the web
i = 1

while True:
    # scroll one screen height each time
    driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))
    i += 1
    time.sleep(scroll_pause_time)
    # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
    scroll_height = driver.execute_script("return document.body.scrollHeight;")
    # Break the loop when the height we need to scroll to is larger than the total scroll height
    if (screen_height) * i > scroll_height:
        break

# creating soup
soup = BeautifulSoup(driver.page_source, "html.parser")
divs = soup.findAll('div', class_='jumbo-tracker')

# create all the list here according to data needs
urls = []
rest_name = []
ratings = []
price = []
crusine = []
for parent in divs:  # zomato is very anti-scrapping website it changes class of the data dynamically (jumbo tracker is the only fixed things i can find)

    #  links of the restaurants are in a tags hence we are using it find and then getting href where links are stored
    link_tag = parent.find("a")

    #  name of the restaurant is stored in the h4 tags and luckily it was unique in main class
    name_tag = parent.find("h4")

    base = "https://www.zomato.com"  # since we don not get whole link https attached we need to join the link with base
    try:
        if 'href' in link_tag.attrs:
            link = link_tag.get('href')
    except:
        pass
    url = urljoin(base, link)
    urls.append(url)
    # appending the url to list urls after joining it with the base

for div in divs:
    rating_tag = div.div.a.next_sibling.div.div.div.div.div.div.div.text
    price_tag = div.div.a.next_sibling.p.next_sibling.text
    crusine_tag = div.div.a.next_sibling.p.text
    ratings.append(rating_tag)
    price.append(price_tag)
    crusine.append(crusine_tag)


out_df2 = pd.DataFrame(
    {'links': urls, 'names': rest_name, 'ratings': ratings, 'price for one': price, 'crusine': crusine})
# we need to create a data frame to neatly view the data in csv format, just add the lists below

# noinspection PyTypeChecker
out_df2.to_csv("Bangalore_restaurants1.csv")
#  creating csv for information

driver.close()
zomato = pd.read_csv('Bangalore_restaurants1.csv')
resmenu = []
m1 = []
m2 = []
must_try_final = []
chef_sp_final = []
links = []
for i in range(940):
    veg = []
    print(zomato['links'][i])
    try:
        link = zomato['links'][i]
        links.append(link)
        linkpage = requests.get(link, headers=headers)
        # print(i,".",link)
        soup = BeautifulSoup(linkpage.text, 'lxml')
        sideCol = soup.find_all('p', class_='sc-1hez2tp-0')
        # print(sideCol)
        dc = {}
        for i in sideCol:
            val = ""
            if '(' in i.text:
                s1 = len(i.text)
                s = i.text
                for x in range(s1 - 2, 0, -1):
                    if (s[x] == '('):
                        break
                    val = s[x] + val
                dc[((s.split('('))[0]).rstrip()] = int(val)
        resmenu.append(dc)
        # print(dc)
        count = 0
        menuVEG = {}
        menuNONVEG = {}
        menuL = soup.find_all('div', class_='sc-1s0saks-17')
        num = 0
        l = {}
        for k in dc:
            # print(k,dc[k])
            key = []
            veg = {}
            nonveg = {}
            for j in range(dc[k]):
                # print(count)
                # print(menuL[count].text)
                # print(veg)
                key = []
                item_name = menuL[count].find('h4', class_='sc-1s0saks-15 iSmBPS')
                must_try = menuL[count].find('div', class_='sc-2gamf4-0 cRxPpO')
                chef_sp = menuL[count].find('div', class_='sc-2gamf4-0 fQRUpA')
                VEG = menuL[count].find('div', class_='sc-1tx3445-1')
                if (must_try != None):
                    key.append(1)
                else:
                    key.append(0)
                if (chef_sp != None):
                    key.append(1)
                else:
                    key.append(0)
                if (k == 'Recommended'):
                    key.append(1)
                    l[item_name.text] = key
                else:
                    if (VEG['type'] == 'veg' and item_name.text in l.keys()):
                        veg[item_name.text] = l[item_name.text]
                    elif (VEG['type'] == 'veg'):
                        key.append(0)
                        veg[item_name.text] = key
                    if (VEG['type'] == 'non-veg' and item_name.text in l.keys()):
                        nonveg[item_name.text] = l[item_name.text]
                    elif (VEG['type'] == 'non-veg'):
                        key.append(0)
                        nonveg[item_name.text] = key
                    if (VEG['type'] == 'egg' and item_name.text in l.keys()):
                        nonveg[item_name.text] = l[item_name.text]
                    elif (VEG['type'] == 'egg'):
                        key.append(0)
                        nonveg[item_name.text] = key
                count += 1
            menuVEG[k] = veg
            menuNONVEG[k] = nonveg
        m1.append(menuVEG)
        m2.append(menuNONVEG)
        print(len(m1), len(m2))
    except:
        m1.append({})
        m2.append({})
        print("ERROR" + "=" * 100)

df = pd.DataFrame({'links': links, 'Veg_menu': m1, 'Non_veg_menu': m2, })

z = zomato.merge(df, how='inner', on='links')

z.to_json(r'paritosh.json')
df1 = pd.read_json("paritosh.json")

end = time.time()

print(start - end)
# time taken to run the program

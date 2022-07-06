from bs4 import BeautifulSoup
import requests
from datetime import date
import calendar

today = date.today()

start_date = date(2021, 9, 10)
end_date = date(2021, 12, 9)

if today >= date(2021, 12, 10) and today < date(2022, 3, 11):
    start_date = date(2021, 12, 10)
    end_date = date(2022, 3, 10)

if today >= date(2022, 3, 11) and today < date(2022, 6, 10):
    start_date = date(2022, 3, 11)
    end_date = date(2022, 6, 9)

if today >= date(2022, 6, 10) and today < date(2022, 9, 9):
    start_date = date(2022, 6, 10)
    end_date = date(2022, 9, 8)

if today >= date(2022, 9, 9) and today < date(2022, 12, 9):
    start_date = date(2022, 9, 9)
    end_date = date(2022, 12, 8)

if today >= date(2022, 12, 9):
    start_date = date(2022, 12, 9)
    end_date = date(2023, 3, 9)

yy = start_date.year
mm = start_date.month
dd = start_date.day

def price_data():
    url = "http://225navi.com/data/"
    r = requests.get(url)
    html_content = r.content
    soup = BeautifulSoup(html_content, "html.parser")
    soup.prettify()

    container = soup.find(class_="sc_table")
    table = container.find("table")

    value = []
    flag = False
    for td in table.find_all("tr"):
        for i in td:
            try:
                if i.text.strip() == f"{yy}/{mm}/{dd-1}":
                    flag = True
                    break
                else:
                    p = i.text.strip()
                    p = p.replace('\n', '')
                    value.append(p)
            except:
                pass
        if flag == True:
            break

    price = []
    for i in value:
        if i == "" or "/" in i:
            pass
        else:
            price.append(i)
    price = price[14:]
    price = price[0:-1:8]
    main_price = list(map(int, price))
    main_price = main_price[::-1]

    return main_price


def price_data_7to10():
    url = "http://225navi.com/data/data5/"
    r = requests.get(url)
    html_content = r.content
    soup = BeautifulSoup(html_content, "html.parser")
    soup.prettify()

    container = soup.find(class_="sc_table")
    table = container.find("table")

    value = []
    flag = False
    for td in table.find_all("tr"):
        for i in td:
            try:
                if i.text.strip() == f"{yy}/{mm}/{dd-1}":
                    flag = True
                    break
                else:
                    p = i.text.strip()
                    p = p.replace('\n', '')
                    value.append(p)
            except:
                pass
        if flag == True:
            break

    price = []
    for i in value:
        if i == "" or "/" in i:
            pass
        else:
            price.append(i)
    price = price[14:]
    price = price[0:-1:8]
    main_price = list(map(float, price))
    main_price = main_price[::-1]

    return main_price

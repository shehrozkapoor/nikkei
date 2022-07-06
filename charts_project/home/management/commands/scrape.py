from datetime import datetime,date
import requests
import pandas as pd
from bs4 import BeautifulSoup
import urllib.request
import os
import calendar
from collections import OrderedDict
from django.core.management.base import BaseCommand
from ...models import daily_data
from datetime import timedelta

def second_friday(y, m):
    c = calendar.Calendar(firstweekday=calendar.SUNDAY)
    year = int(y)
    month = int(m)
    monthcal = c.monthdatescalendar(year, month)
    Fridays = []
    for week in monthcal:
        for day in week:
            if day.weekday() == calendar.FRIDAY and day.month == month:
                Fridays.append(day)
    return Fridays[1]

today = date.today()
month_list = [3, 6, 9, 12]
friday_list = []
pairs = []
today_str = today.strftime("%Y-%m-%d")
dates = ["2021-9-21", today_str]
start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
dates = OrderedDict(((start + timedelta(_)).strftime(r"%Y-%m"), None)
                    for _ in range((end - start).days)).keys()
for i in dates:
    if int(i[5:]) in month_list:
        friday_list.append(second_friday(i[0:4], i[5:]))

if friday_list[-1] <= today:
    start_date = friday_list[-1]
else:
    start_date = friday_list[-2]

temp_month = start_date.month
temp_year = start_date.year

if temp_month == 12:
    end_date = second_friday(temp_year+1, 3)
else:
    end_date = second_friday(temp_year, temp_month+3)

start_m = start_date.strftime("%B") + str(start_date.year)
end_m = end_date.strftime("%B") + str(end_date.year)

end_year = str(end_date.year)
end_month = str(end_date.month)
end_day = str(end_date.day)

if len(end_month) == 1:
    end_month = f'0{end_month}'

if len(end_day) == 1:
    end_day = f'0{end_day}'

url_end_date = list(end_year+end_month+end_day)
if len(url_end_date) == 3:
    url_end_date.insert(2, '0')
url_end_date = "".join(url_end_date)


start_year = str(start_date.year)
start_month = str(start_date.month)
start_day = str(start_date.day)

if len(start_month) == 1:
    start_month = f'0{start_month}'

if len(start_day) == 1:
    start_day = f'0{start_day}'

url_start_date = list(start_year+start_month+start_day)
if len(url_start_date) == 3:
    url_start_date.insert(2, '0')
url_start_date = "".join(url_start_date)

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        url_list = []
        url = "https://www.jpx.co.jp/markets/derivatives/participant-volume/index.html"
        agent = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
        page = requests.get(url,  headers=agent)
        page = page.text
        soup = BeautifulSoup(page, "html.parser")

        current_month = int(datetime.today().strftime("%m"))
        dates_list = soup.find(
            'select', {'class': 'backnumber'}).find_all('option')
        url_list_new = []
        for x in dates_list:
            try:
                temp = {"month": int(x.getText()[7:9]),
                        "url": "https://www.jpx.co.jp"+x.get("value")}
            except:
                temp = {"month": int(x.getText()[7:8]),
                        "url": "https://www.jpx.co.jp"+x.get("value")}
            url_list_new.append(temp)

        main_urls_list = []
        if(current_month >= 5 and current_month <= 8):
            main_urls_list = [x['url'] for x in url_list_new if (
                x['month'] >= 5 and x['month'] <= 8)]
        elif(current_month >= 9 and current_month <= 12):
            main_urls_list = [x['url'] for x in url_list_new if (
                x['month'] >= 9 and x['month'] <= 12)]
        else:
            main_urls_list = [x['url'] for x in url_list_new if (
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 4))]

        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})

            url_list = []
            url_list_jnet = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day.xlsx") != -1):
                        url_list.append("https://www.jpx.co.jp"+k.get('href'))

                    if((k.get('href')).find("by_participant_whole_day_J-NET.xlsx") != -1):
                        url_list_jnet.append(
                            "https://www.jpx.co.jp"+k.get('href'))
                            
            for url in url_list:
                temp1 = url.split('/')
                temp2 = temp1[-1].split("_")
                if int(temp2[0]) >= int(url_start_date) and int(temp2[0]) <= int(url_end_date):
                    data = pd.read_excel(url, header=None, names=[
                        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'])
                    data = data.replace("－", 0)
                    date = (data.iloc[[4]]["c"]).to_string(index=False)
                    main_date = str(date)[:4]+"-" + \
                        str(date)[4:6]+"-"+str(date)[6:]
                    
                    if os.path.isfile(f"{temp2[0]}.xlsx"):
                        pass
                    else:
                        urllib.request.urlretrieve(url, f"{temp2[0]}.xlsx")
                        data = data.iloc[8:, :]
                        for index, row in data.iterrows():
                            entry = daily_data(date=main_date, jpx_code=row["b"], company_id=row["e"], description=row["c"], name_jpn=row["f"],
                                               name_eng=row["g"], left_val=row["h"], company_id_right=row['j'], right_val=row["m"], label="whole_day")
                            entry.save()

            for url in url_list_jnet:
                temp3 = url.split('/')
                temp4 = temp3[-1].split("_")
                if int(temp4[0]) >= int(url_start_date) and int(temp4[0]) <= int(url_end_date):
                    data = pd.read_excel(url, header=None, names=[
                        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'])
                    data = data.replace("－", 0)
                    date = (data.iloc[[4]]["c"]).to_string(index=False)
                    main_date = str(date)[:4]+"-" + \
                        str(date)[4:6]+"-"+str(date)[6:]

                    if os.path.isfile(f"{temp4[0]+temp4[-1][0:5]}.xlsx"):
                        pass
                    else:
                        urllib.request.urlretrieve(
                            url, f"{temp4[0]+temp4[-1][0:5]}.xlsx")
                        data = data.iloc[8:, :]
                        for index, row in data.iterrows():
                            entry = daily_data(date=main_date, jpx_code=row["b"], company_id=row["e"], description=row["c"], name_jpn=row["f"],
                                               name_eng=row["g"], left_val=row["h"], company_id_right=row['j'], right_val=row["m"], label="whole_day_jnet")
                            entry.save()
        self.stdout.write("end")

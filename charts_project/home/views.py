from rest_framework.decorators import api_view
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.response import Response
from datetime import datetime, date, timedelta
import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import io
import numpy as np
import sqlite3
import locale
import os
import calendar
from collections import OrderedDict
import operator
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from .price import price_data, price_data_7to10

# locale.setlocale(locale.LC_CTYPE, "Japanese_Japan.932")
locale.setlocale(locale.LC_CTYPE, "ja_JP")


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except:
        print("couldn't connect to database")

    return conn

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

for_month = []
for_month_friday = []
start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

temp_dates = [start_date_str, end_date_str]
a, b = [datetime.strptime(_, "%Y-%m-%d") for _ in temp_dates]
temp_dates = OrderedDict(((a + timedelta(_)).strftime(r"%Y-%m"), None)
                         for _ in range((b - a).days)).keys()

for i in temp_dates:
    for_month_friday.append(second_friday(i[0:4], i[5:]))

temp = []
for i in for_month_friday:
    if i <= today:
        temp.append(i)

if temp[-1].month == 12:
    raw_month_data = f"{temp[-1].year+1}{int(1)}"
else:
    raw_month_data = f"{temp[-1].year}{temp[-1].month+1}"

month_data = str(raw_month_data)[2:]

if len(month_data)==3:
    month_data = f"{month_data[0:2]}0{month_data[-1]}"
else:
    month_data=month_data

four_month_data = f"{str(end_date.year)[2:]}{end_date.month}"

if len(four_month_data)==3:
    four_month_data = f"{four_month_data[0:2]}0{four_month_data[-1]}"
else:
    four_month_data=four_month_data

for i in range(len(for_month_friday)):
    if today >= for_month_friday[i]:
        start_date_ = for_month_friday[i]
        end_date_ = for_month_friday[i+1]

FUTURES_GRAPHS_METADATA = [
    ([12479, 11788, 12410, 11746, 11635, 12176, 12428, 11560, 11714,
     12800, 12792], [f'NIKKEI 225 FUT {four_month_data}'], '日経225ラージ先物外資系手口'),
    ([11635], [f'NIKKEI 225 FUT {four_month_data}'], '日経225ラージ先物クレディスイス手口'),
    ([11560], [f'NIKKEI 225 FUT {four_month_data}'], '日経225ラージ先物ゴールドマンサックス手口'),
    ([12800], [f'NIKKEI 225 FUT {four_month_data}'], '日経225ラージ先物モルガンスタンレー手口'),
    ([11256, 12330, 12057, 12560, 11727], [
     f'NIKKEI 225 FUT {four_month_data}'], '日経225先物国内ネット系証券手口'),
    ([11256, 12330, 12057, 12560, 11727], [
     f'MINI NK225 FUT {four_month_data}'], '日経225mini先物国内ネット系証券手口'),
]

TOPIX_FUTURES_GRAPHS_METADATA = [
    ([12479, 11788, 12410, 11746, 11635, 12176, 12428, 11560,
     11714, 12800, 12792], [f'TOPIX FUT {four_month_data}'], 'TOPIX先物外資系手口'),
    ([11635], [f'TOPIX FUT {four_month_data}'], 'TOPIX先物クレディスイス手口'),
    ([11560], [f'TOPIX FUT {four_month_data}'], 'TOPIX先物ゴールドマンサックス手口'),
    ([12800], [f'TOPIX FUT {four_month_data}'], 'TOPIX先物モルガンスタンレー手口'),
]

OPTIONS_GRAPHS_METADATA = [
    ([11560], [f'NIKKEI 225 OOP C{month_data}-'],
     '日経225オプションゴールドマンサックスのコール手口'),
    ([11560], [f'NIKKEI 225 OOP P{month_data}-'],
     '日経225オプションゴールドマンサックスのプット手口'),
    ([12479], [f'NIKKEI 225 OOP C{month_data}-'], '日経225オプションABNアムロのコール手口'),
    ([12479], [f'NIKKEI 225 OOP P{month_data}-'], '日経225オプションABNアムロのプット手口'),
    ([11714], [f'NIKKEI 225 OOP C{month_data}-'], '日経225オプションJPモルガンのコール手口'),
    ([11714], [f'NIKKEI 225 OOP P{month_data}-'], '日経225オプションJPモルガンのプット手口'),
    ([12800], [f'NIKKEI 225 OOP C{month_data}-'],
     '日経225オプションモルガンスタンレーのコール手口'),
    ([12800], [f'NIKKEI 225 OOP P{month_data}-'],
     '日経225オプションモルガンスタンレーのプット手口'),
    ([11256, 12330, 12057, 12560, 11727], [
     f'NIKKEI 225 OOP C{month_data}-'], '日経225オプション国内ネット系証券のコール手口'),
    ([11256, 12330, 12057, 12560, 11727], [
     f'NIKKEI 225 OOP P{month_data}-'], '日経225オプション国内ネット系証券のプット手口'),
]


def index(request):
    return render(request, 'charts_temp.html')


def Charts2(request):
    return render(request, 'charts2.html')


def Charts3(request):
    return render(request, 'charts3.html')


def Charts4(request):
    return render(request, 'charts4.html')


def Charts5(request):
    return render(request, 'charts5.html')


def Charts6(request):
    return render(request, 'charts6.html')


class getChart1Data(APIView):
    def get(self, request):
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]

        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})

            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day.xlsx") != -1):
                        url_list.append("https://www.jpx.co.jp"+k.get('href'))

            for url in url_list:
                data = pd.read_excel(url, header=None, names=[
                                     'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'])
                date = (data.iloc[[4]]["c"]).to_string(index=False)
                main_date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]

                l = [12479, 11788, 12410, 11746, 11635,
                     12176, 12428, 11560, 11714, 12800, 12792]
                rows = data[data["c"].str.contains("NIKKEI 225 FUT", na=False)]

                sum_sell = 0
                sum_buy = 0
                main_volume = 0

                for i in l:
                    sell_data = (rows["h"][rows["e"] == f"{i}"])
                    buy_data = (rows["m"][rows["j"] == f"{i}"])

                    for j in sell_data:
                        sum_sell += j

                    for k in buy_data:
                        sum_buy += k

                main_volume += sum_buy-sum_sell

                result_json[main_date] = main_volume

        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)
        return Response(responseData)


class getChart1DataJnet(APIView):
    def get(self, request):
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]

        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})

            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("by_participant_whole_day_J-NET.xlsx") != -1):
                        url_list.append("https://www.jpx.co.jp"+k.get('href'))

            for url in url_list:
                data = pd.read_excel(url, header=None, names=[
                                     'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'])
                date = (data.iloc[[4]]["c"]).to_string(index=False)
                main_date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]

                l = [12479, 11788, 12410, 11746, 11635,
                     12176, 12428, 11560, 11714, 12800, 12792]
                rows = data[data["c"].str.contains("NIKKEI 225 FUT", na=False)]

                sum_sell = 0
                sum_buy = 0
                main_volume = 0

                for i in l:
                    sell_data = (rows["h"][rows["e"] == f"{i}"])
                    buy_data = (rows["m"][rows["j"] == f"{i}"])

                    for j in sell_data:
                        sum_sell += j

                    for k in buy_data:
                        sum_buy += k

                main_volume += sum_buy-sum_sell

                result_json[main_date] = main_volume

        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)
        return Response(responseData)


class getChart2Data(APIView):
    def get(self, request):
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]

        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})

            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day.xlsx") != -1):
                        url_list.append("https://www.jpx.co.jp"+k.get('href'))

            for url in url_list:
                data = pd.read_excel(url, header=None, names=[
                                     'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'])
                date = (data.iloc[[4]]["c"]).to_string(index=False)
                main_date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                rows = data[data["c"].str.contains(
                    "NIKKEI 225 FUT 2112", na=False)]

                sell_data = (rows["h"][rows["e"] == "11635"])
                buy_data = (rows["m"][rows["j"] == "11635"])

                sum_sell = 0
                for i in sell_data:
                    sum_sell += i

                sum_buy = 0
                for i in buy_data:
                    sum_buy += i

                main_volume = sum_buy-sum_sell

                result_json[main_date] = main_volume

        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)
        return Response(responseData)


class getChart2DataJnet(APIView):
    def get(self, request):
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]

        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})

            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("by_participant_whole_day_J-NET.xlsx") != -1):
                        url_list.append("https://www.jpx.co.jp"+k.get('href'))

            for url in url_list:
                data = pd.read_excel(url, header=None, names=[
                                     'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'])
                date = (data.iloc[[4]]["c"]).to_string(index=False)
                rows = data[data["c"].str.contains(
                    "NIKKEI 225 FUT 2112", na=False)]

                sell_data = (rows["h"][rows["e"] == "11635"])
                buy_data = (rows["m"][rows["j"] == "11635"])

                sum_sell = 0
                for i in sell_data:
                    sum_sell += i

                sum_buy = 0
                for i in buy_data:
                    sum_buy += i

                main_volume = sum_buy-sum_sell

                main_date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[main_date] = main_volume

        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)
        return Response(responseData)


class getChart3Data(APIView):
    def get(self, request):
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]

        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})

            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day.xlsx") != -1):
                        url_list.append("https://www.jpx.co.jp"+k.get('href'))

            for url in url_list:
                data = pd.read_excel(url, header=None, names=[
                                     'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'])
                date = (data.iloc[[4]]["c"]).to_string(index=False)
                rows = data[data["c"].str.contains(
                    "NIKKEI 225 FUT 2112", na=False)]

                sell_data = (rows["h"][rows["e"] == "11560"])
                buy_data = (rows["m"][rows["j"] == "11560"])

                sum_sell = 0
                for i in sell_data:
                    sum_sell += i

                sum_buy = 0
                for i in buy_data:
                    sum_buy += i

                main_volume = sum_buy-sum_sell

                main_date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[main_date] = main_volume
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)
        return Response(responseData)


class getChart3DataJnet(APIView):
    def get(self, request):
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]

        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})

            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day_J-NET.xlsx") != -1):
                        url_list.append("https://www.jpx.co.jp"+k.get('href'))

            for url in url_list:
                data = pd.read_excel(url, header=None, names=[
                                     'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'])
                date = (data.iloc[[4]]["c"]).to_string(index=False)
                rows = data[data["c"].str.contains(
                    "NIKKEI 225 FUT 2112", na=False)]

                sell_data = (rows["h"][rows["e"] == "11560"])
                buy_data = (rows["m"][rows["j"] == "11560"])

                sum_sell = 0
                for i in sell_data:
                    sum_sell += i

                sum_buy = 0
                for i in buy_data:
                    sum_buy += i

                main_volume = sum_buy-sum_sell

                main_date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[main_date] = main_volume
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)
        return Response(responseData)


class getChart4Data(APIView):
    def get(self, request):
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]

        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})

            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day.xlsx") != -1):
                        url_list.append("https://www.jpx.co.jp"+k.get('href'))

            for url in url_list:
                data = pd.read_excel(url, header=None, names=[
                                     'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'])
                date = (data.iloc[[4]]["c"]).to_string(index=False)
                rows = data[data["c"].str.contains(
                    "NIKKEI 225 FUT 2112", na=False)]

                sell_data = (rows["h"][rows["e"] == "12800"])
                buy_data = (rows["m"][rows["j"] == "12800"])

                sum_sell = 0
                for i in sell_data:
                    sum_sell += i

                sum_buy = 0
                for i in buy_data:
                    sum_buy += i

                main_volume = sum_buy-sum_sell

                main_date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[main_date] = main_volume

        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)
        return Response(responseData)


class getChart4DataJnet(APIView):
    def get(self, request):
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]

        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})

            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day_J-NET.xlsx") != -1):
                        url_list.append("https://www.jpx.co.jp"+k.get('href'))

            for url in url_list:
                data = pd.read_excel(url, header=None, names=[
                                     'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'])
                date = (data.iloc[[4]]["c"]).to_string(index=False)
                rows = data[data["c"].str.contains(
                    "NIKKEI 225 FUT 2112", na=False)]

                sell_data = (rows["h"][rows["e"] == "12800"])
                buy_data = (rows["m"][rows["j"] == "12800"])

                sum_sell = 0
                for i in sell_data:
                    sum_sell += i

                sum_buy = 0
                for i in buy_data:
                    sum_buy += i

                main_volume = sum_buy-sum_sell

                main_date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[main_date] = main_volume
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)
        return Response(responseData)


class getChart5Data(APIView):
    def get(self, request):
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]

        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})

            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day.xlsx") != -1):
                        url_list.append("https://www.jpx.co.jp"+k.get('href'))

            for url in url_list:
                data = pd.read_excel(url, header=None, names=[
                                     'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'])
                date = (data.iloc[[4]]["c"]).to_string(index=False)
                main_date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]

                l = [11256, 12330, 12057, 12560, 11727]
                rows = data[data["c"].str.contains(
                    "NIKKEI 225 FUT 2112", na=False)]

                sum_sell = 0
                sum_buy = 0
                main_volume = 0

                for i in l:
                    sell_data = (rows["h"][rows["e"] == f"{i}"])
                    buy_data = (rows["m"][rows["j"] == f"{i}"])

                    for j in sell_data:
                        sum_sell += j

                    for k in buy_data:
                        sum_buy += k

                main_volume += sum_buy-sum_sell

                result_json[main_date] = main_volume

        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)
        return Response(responseData)


class getChart5DataJnet(APIView):
    def get(self, request):
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]

        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})

            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("by_participant_whole_day_J-NET.xlsx") != -1):
                        url_list.append("https://www.jpx.co.jp"+k.get('href'))

            for url in url_list:
                data = pd.read_excel(url, header=None, names=[
                                     'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'])
                date = (data.iloc[[4]]["c"]).to_string(index=False)
                main_date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]

                l = [11256, 12330, 12057, 12560, 11727]
                rows = data[data["c"].str.contains("NIKKEI 225 FUT", na=False)]

                sum_sell = 0
                sum_buy = 0
                main_volume = 0

                for i in l:
                    sell_data = (rows["h"][rows["e"] == f"{i}"])
                    buy_data = (rows["m"][rows["j"] == f"{i}"])

                    for j in sell_data:
                        sum_sell += j

                    for k in buy_data:
                        sum_buy += k

                main_volume += sum_buy-sum_sell

                result_json[main_date] = main_volume

        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)
        return Response(responseData)


class getChart6Data(APIView):
    def get(self, request):
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]

        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})

            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day.xlsx") != -1):
                        url_list.append("https://www.jpx.co.jp"+k.get('href'))

            for url in url_list:
                data = pd.read_excel(url, header=None, names=[
                                     'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'])
                date = (data.iloc[[4]]["c"]).to_string(index=False)
                main_date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]

                l = [11256, 12330, 12057, 12560, 11727]
                rows = data[data["c"].str.contains("MINI NK225 FUT", na=False)]

                sum_sell = 0
                sum_buy = 0
                main_volume = 0

                for i in l:
                    sell_data = (rows["h"][rows["e"] == f"{i}"])
                    buy_data = (rows["m"][rows["j"] == f"{i}"])

                    for j in sell_data:
                        sum_sell += j

                    for k in buy_data:
                        sum_buy += k

                main_volume += sum_buy-sum_sell

                result_json[main_date] = main_volume

        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)
        return Response(responseData)


class getChart6DataJnet(APIView):
    def get(self, request):
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]

        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})

            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day_J-NET.xlsx") != -1):
                        url_list.append("https://www.jpx.co.jp"+k.get('href'))

            for url in url_list:
                data = pd.read_excel(url, header=None, names=[
                                     'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'])
                date = (data.iloc[[4]]["c"]).to_string(index=False)
                main_date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]

                l = [11256, 12330, 12057, 12560, 11727]
                rows = data[data["c"].str.contains(
                    "MINI NK225 FUT 2112", na=False)]

                sum_sell = 0
                sum_buy = 0
                main_volume = 0

                for i in l:
                    sell_data = (rows["h"][rows["e"] == f"{i}"])
                    buy_data = (rows["m"][rows["j"] == f"{i}"])

                    for j in sell_data:
                        sum_sell += j

                    for k in buy_data:
                        sum_buy += k

                main_volume += sum_buy-sum_sell

                result_json[main_date] = main_volume

        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)
        return Response(responseData)


class getChart7Data(APIView):
    def get(self, request):
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]

        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})

            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day.xlsx") != -1):
                        url_list.append("https://www.jpx.co.jp"+k.get('href'))

            for url in url_list:
                data = pd.read_excel(url, header=None, names=[
                                     'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'])
                date = (data.iloc[[4]]["c"]).to_string(index=False)
                main_date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]

                l = [12479, 11788, 12410, 11746, 11635,
                     12176, 12428, 11560, 11714, 12800, 12792]
                rows = data[data["c"].str.contains("TOPIX FUT 2112", na=False)]

                sum_sell = 0
                sum_buy = 0
                main_volume = 0

                for i in l:
                    sell_data = (rows["h"][rows["e"] == f"{i}"])
                    buy_data = (rows["m"][rows["j"] == f"{i}"])

                    for j in sell_data:
                        sum_sell += j

                    for k in buy_data:
                        sum_buy += k

                main_volume += sum_buy-sum_sell

                result_json[main_date] = main_volume

        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)
        return Response(responseData)


class getChart7DataJnet(APIView):
    def get(self, request):
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]

        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})

            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day_J-NET.xlsx") != -1):
                        url_list.append("https://www.jpx.co.jp"+k.get('href'))

            for url in url_list:
                data = pd.read_excel(url, header=None, names=[
                                     'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'])
                date = (data.iloc[[4]]["c"]).to_string(index=False)
                main_date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]

                l = [12479, 11788, 12410, 11746, 11635,
                     12176, 12428, 11560, 11714, 12800, 12792]
                rows = data[data["c"].str.contains("TOPIX FUT 2112", na=False)]

                sum_sell = 0
                sum_buy = 0
                main_volume = 0

                for i in l:
                    sell_data = (rows["h"][rows["e"] == f"{i}"])
                    buy_data = (rows["m"][rows["j"] == f"{i}"])

                    for j in sell_data:
                        sum_sell += j

                    for k in buy_data:
                        sum_buy += k

                main_volume += sum_buy-sum_sell

                result_json[main_date] = main_volume

        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)
        return Response(responseData)


class getChart8Data(APIView):
    def get(self, request):
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]

        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})

            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day.xlsx") != -1):
                        url_list.append("https://www.jpx.co.jp"+k.get('href'))

            for url in url_list:
                data = pd.read_excel(url, header=None, names=[
                                     'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'])
                date = (data.iloc[[4]]["c"]).to_string(index=False)
                main_date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                rows = data[data["c"].str.contains("TOPIX FUT 2112", na=False)]

                sell_data = (rows["h"][rows["e"] == "11635"])
                buy_data = (rows["m"][rows["j"] == "11635"])

                sum_sell = 0
                for i in sell_data:
                    sum_sell += i

                sum_buy = 0
                for i in buy_data:
                    sum_buy += i

                main_volume = sum_buy-sum_sell

                result_json[main_date] = main_volume

        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)
        return Response(responseData)


class getChart8DataJnet(APIView):
    def get(self, request):
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]

        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})

            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("by_participant_whole_day_J-NET.xlsx") != -1):
                        url_list.append("https://www.jpx.co.jp"+k.get('href'))

            for url in url_list:
                data = pd.read_excel(url, header=None, names=[
                                     'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'])
                date = (data.iloc[[4]]["c"]).to_string(index=False)
                rows = data[data["c"].str.contains("TOPIX FUT 2112", na=False)]

                sell_data = (rows["h"][rows["e"] == "11635"])
                buy_data = (rows["m"][rows["j"] == "11635"])

                sum_sell = 0
                for i in sell_data:
                    sum_sell += i

                sum_buy = 0
                for i in buy_data:
                    sum_buy += i

                main_volume = sum_buy-sum_sell

                main_date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[main_date] = main_volume

        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)
        return Response(responseData)


class getChart9Data(APIView):
    def get(self, request):
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]

        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})

            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day.xlsx") != -1):
                        url_list.append("https://www.jpx.co.jp"+k.get('href'))

            for url in url_list:
                data = pd.read_excel(url, header=None, names=[
                                     'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'])
                date = (data.iloc[[4]]["c"]).to_string(index=False)
                rows = data[data["c"].str.contains("TOPIX FUT 2112", na=False)]

                sell_data = (rows["h"][rows["e"] == "11560"])
                buy_data = (rows["m"][rows["j"] == "11560"])

                sum_sell = 0
                for i in sell_data:
                    sum_sell += i

                sum_buy = 0
                for i in buy_data:
                    sum_buy += i

                main_volume = sum_buy-sum_sell

                main_date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[main_date] = main_volume
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)
        return Response(responseData)


class getChart9DataJnet(APIView):
    def get(self, request):
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]

        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})

            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day_J-NET.xlsx") != -1):
                        url_list.append("https://www.jpx.co.jp"+k.get('href'))

            for url in url_list:
                data = pd.read_excel(url, header=None, names=[
                                     'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'])
                date = (data.iloc[[4]]["c"]).to_string(index=False)
                rows = data[data["c"].str.contains("TOPIX FUT 2112", na=False)]

                sell_data = (rows["h"][rows["e"] == "11560"])
                buy_data = (rows["m"][rows["j"] == "11560"])

                sum_sell = 0
                for i in sell_data:
                    sum_sell += i

                sum_buy = 0
                for i in buy_data:
                    sum_buy += i

                main_volume = sum_buy-sum_sell

                main_date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[main_date] = main_volume
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)
        return Response(responseData)


class getChart10Data(APIView):
    def get(self, request):
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]

        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})

            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day.xlsx") != -1):
                        url_list.append("https://www.jpx.co.jp"+k.get('href'))

            for url in url_list:
                data = pd.read_excel(url, header=None, names=[
                                     'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'])
                date = (data.iloc[[4]]["c"]).to_string(index=False)
                rows = data[data["c"].str.contains("TOPIX FUT 2112", na=False)]

                sell_data = (rows["h"][rows["e"] == "12800"])
                buy_data = (rows["m"][rows["j"] == "12800"])

                sum_sell = 0
                for i in sell_data:
                    sum_sell += i

                sum_buy = 0
                for i in buy_data:
                    sum_buy += i

                main_volume = sum_buy-sum_sell

                main_date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[main_date] = main_volume

        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)
        return Response(responseData)


class getChart10DataJnet(APIView):
    def get(self, request):
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]

        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})

            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day_J-NET.xlsx") != -1):
                        url_list.append("https://www.jpx.co.jp"+k.get('href'))

            for url in url_list:
                data = pd.read_excel(url, header=None, names=[
                                     'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'])
                date = (data.iloc[[4]]["c"]).to_string(index=False)
                rows = data[data["c"].str.contains("TOPIX FUT 2112", na=False)]

                sell_data = (rows["h"][rows["e"] == "12800"])
                buy_data = (rows["m"][rows["j"] == "12800"])

                sum_sell = 0
                for i in sell_data:
                    sum_sell += i

                sum_buy = 0
                for i in buy_data:
                    sum_buy += i

                main_volume = sum_buy-sum_sell

                main_date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[main_date] = main_volume
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)
        return Response(responseData)


class getChart11Data(APIView):
    def get(self, request):
        url_list = []
        csv_file = "charts.csv"
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]
        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})
            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day.csv") != -1):
                        url_list.append("https://www.jpx.co.jp/"+k.get('href'))
            for url in url_list:
                s = requests.get(url).content
                data = pd.read_csv(io.StringIO(s.decode(
                    'utf-8')), header=None, names=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
                date = data['d'].loc[0]
                nuk_rows = list(
                    data[data['b'].str.contains("CAL_NK225_")].index.values)
                instrument_rows = list(
                    data[data['a'].str.contains("Instrument", na=False)].index.values)
                final_df_minus = pd.DataFrame()
                final_df_plus = pd.DataFrame()
                result_value = 0
                for x in nuk_rows:
                    result = 0
                    nuk_index_begin = instrument_rows.index(x)
                    nuk_index_ends = instrument_rows.index(x)+1
                    if(nuk_index_ends >= len(instrument_rows)):
                        temp_df = data[instrument_rows[nuk_index_begin] +
                                       1:instrument_rows[len(instrument_rows)-1]]
                    else:
                        temp_df = data[instrument_rows[nuk_index_begin] +
                                       1:instrument_rows[nuk_index_ends]-1]
                    try:
                        if(temp_df[temp_df['a'] == "11560"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "11560"])
                            result -= (temp_df[temp_df['a'] ==
                                       "11560"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "11560"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "11560"])
                            result += (temp_df[temp_df['e'] ==
                                       "11560"]['h'].astype(int).item())
                    except:
                        pass
                    result_value += result
                date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[date] = result_value
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)

        return Response(responseData)


class getChart11DataJnet(APIView):
    def get(self, request):
        url_list = []
        csv_file = "charts.csv"
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]
        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})
            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("by_participant_whole_day_J-NET.csv") != -1):
                        url_list.append("https://www.jpx.co.jp/"+k.get('href'))
            for url in url_list:
                s = requests.get(url).content
                data = pd.read_csv(io.StringIO(s.decode(
                    'utf-8')), header=None, names=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
                date = data['d'].loc[0]
                nuk_rows = list(
                    data[data['b'].str.contains("CAL_NK225_")].index.values)
                instrument_rows = list(
                    data[data['a'].str.contains("Instrument", na=False)].index.values)
                final_df_minus = pd.DataFrame()
                final_df_plus = pd.DataFrame()
                result_value = 0
                for x in nuk_rows:
                    result = 0
                    nuk_index_begin = instrument_rows.index(x)
                    nuk_index_ends = instrument_rows.index(x)+1
                    if(nuk_index_ends >= len(instrument_rows)):
                        temp_df = data[instrument_rows[nuk_index_begin] +
                                       1:instrument_rows[len(instrument_rows)-1]]
                    else:
                        temp_df = data[instrument_rows[nuk_index_begin] +
                                       1:instrument_rows[nuk_index_ends]-1]
                    try:
                        if(temp_df[temp_df['a'] == "11560"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "11560"])
                            result -= (temp_df[temp_df['a'] ==
                                       "11560"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "11560"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "11560"])
                            result += (temp_df[temp_df['e'] ==
                                       "11560"]['h'].astype(int).item())
                    except:
                        pass
                    result_value += result
                date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[date] = result_value
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)

        return Response(responseData)


class getChart12Data(APIView):
    def get(self, request):
        url_list = []
        csv_file = "charts.csv"
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]
        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})
            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day.csv") != -1):
                        url_list.append("https://www.jpx.co.jp/"+k.get('href'))
            for url in url_list:
                s = requests.get(url).content
                data = pd.read_csv(io.StringIO(s.decode(
                    'utf-8')), header=None, names=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
                date = data['d'].loc[0]
                nuk_rows = list(
                    data[data['b'].str.contains("PUT_NK225_")].index.values)
                instrument_rows = list(
                    data[data['a'].str.contains("Instrument", na=False)].index.values)
                final_df_minus = pd.DataFrame()
                final_df_plus = pd.DataFrame()
                result_value = 0
                for x in nuk_rows:
                    result = 0
                    nuk_index_begin = instrument_rows.index(x)
                    nuk_index_ends = instrument_rows.index(x)+1
                    temp_df = data[instrument_rows[nuk_index_begin] +
                                   1:instrument_rows[nuk_index_ends]-1]
                    try:
                        if(temp_df[temp_df['a'] == "11560"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "11560"])
                            result -= (temp_df[temp_df['a'] ==
                                       "11560"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "11560"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "11560"])
                            result += (temp_df[temp_df['e'] ==
                                       "11560"]['h'].astype(int).item())
                    except:
                        pass
                    result_value += result
                date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[date] = result_value
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)

        return Response(responseData)


class getChart12DataJnet(APIView):
    def get(self, request):
        url_list = []
        csv_file = "charts.csv"
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]
        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})
            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("by_participant_whole_day_J-NET.csv") != -1):
                        url_list.append("https://www.jpx.co.jp/"+k.get('href'))
            for url in url_list:
                s = requests.get(url).content
                data = pd.read_csv(io.StringIO(s.decode(
                    'utf-8')), header=None, names=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
                date = data['d'].loc[0]
                nuk_rows = list(
                    data[data['b'].str.contains("PUT_NK225_")].index.values)
                instrument_rows = list(
                    data[data['a'].str.contains("Instrument", na=False)].index.values)
                final_df_minus = pd.DataFrame()
                final_df_plus = pd.DataFrame()
                result_value = 0
                for x in nuk_rows:
                    result = 0
                    nuk_index_begin = instrument_rows.index(x)
                    nuk_index_ends = instrument_rows.index(x)+1
                    temp_df = data[instrument_rows[nuk_index_begin] +
                                   1:instrument_rows[nuk_index_ends]-1]
                    try:
                        if(temp_df[temp_df['a'] == "11560"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "11560"])
                            result -= (temp_df[temp_df['a'] ==
                                       "11560"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "11560"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "11560"])
                            result += (temp_df[temp_df['e'] ==
                                       "11560"]['h'].astype(int).item())
                    except:
                        pass
                    result_value += result
                date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[date] = result_value
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)

        return Response(responseData)


class getChart13Data(APIView):
    def get(self, request):
        url_list = []
        csv_file = "charts.csv"
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]
        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})
            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day.csv") != -1):
                        url_list.append("https://www.jpx.co.jp/"+k.get('href'))
            for url in url_list:
                s = requests.get(url).content
                data = pd.read_csv(io.StringIO(s.decode(
                    'utf-8')), header=None, names=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
                date = data['d'].loc[0]
                nuk_rows = list(
                    data[data['b'].str.contains("CAL_NK225_")].index.values)
                instrument_rows = list(
                    data[data['a'].str.contains("Instrument", na=False)].index.values)
                final_df_minus = pd.DataFrame()
                final_df_plus = pd.DataFrame()
                result_value = 0
                for x in nuk_rows:
                    result = 0
                    nuk_index_begin = instrument_rows.index(x)
                    nuk_index_ends = instrument_rows.index(x)+1
                    if(nuk_index_ends >= len(instrument_rows)):
                        temp_df = data[instrument_rows[nuk_index_begin] +
                                       1:instrument_rows[len(instrument_rows)-1]]
                    else:
                        temp_df = data[instrument_rows[nuk_index_begin] +
                                       1:instrument_rows[nuk_index_ends]-1]
                    try:
                        if(temp_df[temp_df['a'] == "12479"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "12479"])
                            result -= (temp_df[temp_df['a'] ==
                                       "12479"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "12479"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "12479"])
                            result += (temp_df[temp_df['e'] ==
                                       "12479"]['h'].astype(int).item())
                    except:
                        pass
                    result_value += result
                date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[date] = result_value
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)

        return Response(responseData)


class getChart13DataJnet(APIView):
    def get(self, request):
        url_list = []
        csv_file = "charts.csv"
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]
        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})
            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("by_participant_whole_day_J-NET.csv") != -1):
                        url_list.append("https://www.jpx.co.jp/"+k.get('href'))
            for url in url_list:
                s = requests.get(url).content
                data = pd.read_csv(io.StringIO(s.decode(
                    'utf-8')), header=None, names=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
                date = data['d'].loc[0]
                nuk_rows = list(
                    data[data['b'].str.contains("CAL_NK225_")].index.values)
                instrument_rows = list(
                    data[data['a'].str.contains("Instrument", na=False)].index.values)
                final_df_minus = pd.DataFrame()
                final_df_plus = pd.DataFrame()
                result_value = 0
                for x in nuk_rows:
                    result = 0
                    nuk_index_begin = instrument_rows.index(x)
                    nuk_index_ends = instrument_rows.index(x)+1
                    if(nuk_index_ends >= len(instrument_rows)):
                        temp_df = data[instrument_rows[nuk_index_begin] +
                                       1:instrument_rows[len(instrument_rows)-1]]
                    else:
                        temp_df = data[instrument_rows[nuk_index_begin] +
                                       1:instrument_rows[nuk_index_ends]-1]
                    try:
                        if(temp_df[temp_df['a'] == "12479"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "12479"])
                            result -= (temp_df[temp_df['a'] ==
                                       "12479"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "12479"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "12479"])
                            result += (temp_df[temp_df['e'] ==
                                       "12479"]['h'].astype(int).item())
                    except:
                        pass
                    result_value += result
                date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[date] = result_value
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)

        return Response(responseData)


class getChart14Data(APIView):
    def get(self, request):
        url_list = []
        csv_file = "charts.csv"
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]
        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})
            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day.csv") != -1):
                        url_list.append("https://www.jpx.co.jp/"+k.get('href'))
            for url in url_list:
                s = requests.get(url).content
                data = pd.read_csv(io.StringIO(s.decode(
                    'utf-8')), header=None, names=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
                date = data['d'].loc[0]
                nuk_rows = list(
                    data[data['b'].str.contains("PUT_NK225_")].index.values)
                instrument_rows = list(
                    data[data['a'].str.contains("Instrument", na=False)].index.values)
                final_df_minus = pd.DataFrame()
                final_df_plus = pd.DataFrame()
                result_value = 0
                for x in nuk_rows:
                    result = 0
                    nuk_index_begin = instrument_rows.index(x)
                    nuk_index_ends = instrument_rows.index(x)+1
                    temp_df = data[instrument_rows[nuk_index_begin] +
                                   1:instrument_rows[nuk_index_ends]-1]
                    try:
                        if(temp_df[temp_df['a'] == "12479"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "12479"])
                            result -= (temp_df[temp_df['a'] ==
                                       "12479"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "12479"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "12479"])
                            result += (temp_df[temp_df['e'] ==
                                       "12479"]['h'].astype(int).item())
                    except:
                        pass
                    result_value += result
                date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[date] = result_value
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)

        return Response(responseData)


class getChart14DataJnet(APIView):
    def get(self, request):
        url_list = []
        csv_file = "charts.csv"
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]
        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})
            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("by_participant_whole_day_J-NET.csv") != -1):
                        url_list.append("https://www.jpx.co.jp/"+k.get('href'))
            for url in url_list:
                s = requests.get(url).content
                data = pd.read_csv(io.StringIO(s.decode(
                    'utf-8')), header=None, names=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
                date = data['d'].loc[0]
                nuk_rows = list(
                    data[data['b'].str.contains("PUT_NK225_")].index.values)
                instrument_rows = list(
                    data[data['a'].str.contains("Instrument", na=False)].index.values)
                final_df_minus = pd.DataFrame()
                final_df_plus = pd.DataFrame()
                result_value = 0
                for x in nuk_rows:
                    result = 0
                    nuk_index_begin = instrument_rows.index(x)
                    nuk_index_ends = instrument_rows.index(x)+1
                    temp_df = data[instrument_rows[nuk_index_begin] +
                                   1:instrument_rows[nuk_index_ends]-1]
                    try:
                        if(temp_df[temp_df['a'] == "12479"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "12479"])
                            result -= (temp_df[temp_df['a'] ==
                                       "12479"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "12479"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "12479"])
                            result += (temp_df[temp_df['e'] ==
                                       "12479"]['h'].astype(int).item())
                    except:
                        pass
                    result_value += result
                date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[date] = result_value
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)

        return Response(responseData)


class getChart15Data(APIView):
    def get(self, request):
        url_list = []
        csv_file = "charts.csv"
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]
        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})
            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day.csv") != -1):
                        url_list.append("https://www.jpx.co.jp/"+k.get('href'))
            for url in url_list:
                s = requests.get(url).content
                data = pd.read_csv(io.StringIO(s.decode(
                    'utf-8')), header=None, names=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
                date = data['d'].loc[0]
                nuk_rows = list(
                    data[data['b'].str.contains("CAL_NK225_")].index.values)
                instrument_rows = list(
                    data[data['a'].str.contains("Instrument", na=False)].index.values)
                final_df_minus = pd.DataFrame()
                final_df_plus = pd.DataFrame()
                result_value = 0
                for x in nuk_rows:
                    result = 0
                    nuk_index_begin = instrument_rows.index(x)
                    nuk_index_ends = instrument_rows.index(x)+1
                    if(nuk_index_ends >= len(instrument_rows)):
                        temp_df = data[instrument_rows[nuk_index_begin] +
                                       1:instrument_rows[len(instrument_rows)-1]]
                    else:
                        temp_df = data[instrument_rows[nuk_index_begin] +
                                       1:instrument_rows[nuk_index_ends]-1]
                    try:
                        if(temp_df[temp_df['a'] == "11714"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "11714"])
                            result -= (temp_df[temp_df['a'] ==
                                       "11714"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "11714"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "11714"])
                            result += (temp_df[temp_df['e'] ==
                                       "11714"]['h'].astype(int).item())
                    except:
                        pass
                    result_value += result
                date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[date] = result_value
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)

        return Response(responseData)


class getChart15DataJnet(APIView):
    def get(self, request):
        url_list = []
        csv_file = "charts.csv"
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]
        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})
            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("by_participant_whole_day_J-NET.csv") != -1):
                        url_list.append("https://www.jpx.co.jp/"+k.get('href'))
            for url in url_list:
                s = requests.get(url).content
                data = pd.read_csv(io.StringIO(s.decode(
                    'utf-8')), header=None, names=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
                date = data['d'].loc[0]
                nuk_rows = list(
                    data[data['b'].str.contains("CAL_NK225_")].index.values)
                instrument_rows = list(
                    data[data['a'].str.contains("Instrument", na=False)].index.values)
                final_df_minus = pd.DataFrame()
                final_df_plus = pd.DataFrame()
                result_value = 0
                for x in nuk_rows:
                    result = 0
                    nuk_index_begin = instrument_rows.index(x)
                    nuk_index_ends = instrument_rows.index(x)+1
                    if(nuk_index_ends >= len(instrument_rows)):
                        temp_df = data[instrument_rows[nuk_index_begin] +
                                       1:instrument_rows[len(instrument_rows)-1]]
                    else:
                        temp_df = data[instrument_rows[nuk_index_begin] +
                                       1:instrument_rows[nuk_index_ends]-1]
                    try:
                        if(temp_df[temp_df['a'] == "11714"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "11714"])
                            result -= (temp_df[temp_df['a'] ==
                                       "11714"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "11714"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "11714"])
                            result += (temp_df[temp_df['e'] ==
                                       "11714"]['h'].astype(int).item())
                    except:
                        pass
                    result_value += result
                date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[date] = result_value
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)

        return Response(responseData)


class getChart16Data(APIView):
    def get(self, request):
        url_list = []
        csv_file = "charts.csv"
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]
        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})
            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day.csv") != -1):
                        url_list.append("https://www.jpx.co.jp/"+k.get('href'))
            for url in url_list:
                s = requests.get(url).content
                data = pd.read_csv(io.StringIO(s.decode(
                    'utf-8')), header=None, names=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
                date = data['d'].loc[0]
                nuk_rows = list(
                    data[data['b'].str.contains("PUT_NK225_")].index.values)
                instrument_rows = list(
                    data[data['a'].str.contains("Instrument", na=False)].index.values)
                final_df_minus = pd.DataFrame()
                final_df_plus = pd.DataFrame()
                result_value = 0
                for x in nuk_rows:
                    result = 0
                    nuk_index_begin = instrument_rows.index(x)
                    nuk_index_ends = instrument_rows.index(x)+1
                    temp_df = data[instrument_rows[nuk_index_begin] +
                                   1:instrument_rows[nuk_index_ends]-1]
                    try:
                        if(temp_df[temp_df['a'] == "11714"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "11714"])
                            result -= (temp_df[temp_df['a'] ==
                                       "11714"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "11714"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "11714"])
                            result += (temp_df[temp_df['e'] ==
                                       "11714"]['h'].astype(int).item())
                    except:
                        pass
                    result_value += result
                date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[date] = result_value
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)

        return Response(responseData)


class getChart16DataJnet(APIView):
    def get(self, request):
        url_list = []
        csv_file = "charts.csv"
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]
        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})
            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("by_participant_whole_day_J-NET.csv") != -1):
                        url_list.append("https://www.jpx.co.jp/"+k.get('href'))
            for url in url_list:
                s = requests.get(url).content
                data = pd.read_csv(io.StringIO(s.decode(
                    'utf-8')), header=None, names=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
                date = data['d'].loc[0]
                nuk_rows = list(
                    data[data['b'].str.contains("PUT_NK225_")].index.values)
                instrument_rows = list(
                    data[data['a'].str.contains("Instrument", na=False)].index.values)
                final_df_minus = pd.DataFrame()
                final_df_plus = pd.DataFrame()
                result_value = 0
                for x in nuk_rows:
                    result = 0
                    nuk_index_begin = instrument_rows.index(x)
                    nuk_index_ends = instrument_rows.index(x)+1
                    temp_df = data[instrument_rows[nuk_index_begin] +
                                   1:instrument_rows[nuk_index_ends]-1]
                    try:
                        if(temp_df[temp_df['a'] == "11714"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "11714"])
                            result -= (temp_df[temp_df['a'] ==
                                       "11714"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "11714"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "11714"])
                            result += (temp_df[temp_df['e'] ==
                                       "11714"]['h'].astype(int).item())
                    except:
                        pass
                    result_value += result
                date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[date] = result_value
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)

        return Response(responseData)


class getChart17Data(APIView):
    def get(self, request):
        url_list = []
        csv_file = "charts.csv"
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]
        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})
            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day.csv") != -1):
                        url_list.append("https://www.jpx.co.jp/"+k.get('href'))
            for url in url_list:
                s = requests.get(url).content
                data = pd.read_csv(io.StringIO(s.decode(
                    'utf-8')), header=None, names=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
                date = data['d'].loc[0]
                nuk_rows = list(
                    data[data['b'].str.contains("CAL_NK225_")].index.values)
                instrument_rows = list(
                    data[data['a'].str.contains("Instrument", na=False)].index.values)
                final_df_minus = pd.DataFrame()
                final_df_plus = pd.DataFrame()
                result_value = 0
                for x in nuk_rows:
                    result = 0
                    nuk_index_begin = instrument_rows.index(x)
                    nuk_index_ends = instrument_rows.index(x)+1
                    if(nuk_index_ends >= len(instrument_rows)):
                        temp_df = data[instrument_rows[nuk_index_begin] +
                                       1:instrument_rows[len(instrument_rows)-1]]
                    else:
                        temp_df = data[instrument_rows[nuk_index_begin] +
                                       1:instrument_rows[nuk_index_ends]-1]
                    try:
                        if(temp_df[temp_df['a'] == "12800"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "12800"])
                            result -= (temp_df[temp_df['a'] ==
                                       "12800"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "12800"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "12800"])
                            result += (temp_df[temp_df['e'] ==
                                       "12800"]['h'].astype(int).item())
                    except:
                        pass
                    result_value += result
                date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[date] = result_value
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)

        return Response(responseData)


class getChart17DataJnet(APIView):
    def get(self, request):
        url_list = []
        csv_file = "charts.csv"
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]
        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})
            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("by_participant_whole_day_J-NET.csv") != -1):
                        url_list.append("https://www.jpx.co.jp/"+k.get('href'))
            for url in url_list:
                s = requests.get(url).content
                data = pd.read_csv(io.StringIO(s.decode(
                    'utf-8')), header=None, names=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
                date = data['d'].loc[0]
                nuk_rows = list(
                    data[data['b'].str.contains("CAL_NK225_")].index.values)
                instrument_rows = list(
                    data[data['a'].str.contains("Instrument", na=False)].index.values)
                final_df_minus = pd.DataFrame()
                final_df_plus = pd.DataFrame()
                result_value = 0
                for x in nuk_rows:
                    result = 0
                    nuk_index_begin = instrument_rows.index(x)
                    nuk_index_ends = instrument_rows.index(x)+1
                    if(nuk_index_ends >= len(instrument_rows)):
                        temp_df = data[instrument_rows[nuk_index_begin] +
                                       1:instrument_rows[len(instrument_rows)-1]]
                    else:
                        temp_df = data[instrument_rows[nuk_index_begin] +
                                       1:instrument_rows[nuk_index_ends]-1]
                    try:
                        if(temp_df[temp_df['a'] == "12800"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "12800"])
                            result -= (temp_df[temp_df['a'] ==
                                       "12800"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "12800"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "12800"])
                            result += (temp_df[temp_df['e'] ==
                                       "12800"]['h'].astype(int).item())
                    except:
                        pass
                    result_value += result
                date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[date] = result_value
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)

        return Response(responseData)


class getChart18Data(APIView):
    def get(self, request):
        url_list = []
        csv_file = "charts.csv"
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]
        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})
            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day.csv") != -1):
                        url_list.append("https://www.jpx.co.jp/"+k.get('href'))
            for url in url_list:
                s = requests.get(url).content
                data = pd.read_csv(io.StringIO(s.decode(
                    'utf-8')), header=None, names=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
                date = data['d'].loc[0]
                nuk_rows = list(
                    data[data['b'].str.contains("PUT_NK225_")].index.values)
                instrument_rows = list(
                    data[data['a'].str.contains("Instrument", na=False)].index.values)
                final_df_minus = pd.DataFrame()
                final_df_plus = pd.DataFrame()
                result_value = 0
                for x in nuk_rows:
                    result = 0
                    nuk_index_begin = instrument_rows.index(x)
                    nuk_index_ends = instrument_rows.index(x)+1
                    temp_df = data[instrument_rows[nuk_index_begin] +
                                   1:instrument_rows[nuk_index_ends]-1]
                    try:
                        if(temp_df[temp_df['a'] == "12800"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "12800"])
                            result -= (temp_df[temp_df['a'] ==
                                       "12800"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "12800"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "12800"])
                            result += (temp_df[temp_df['e'] ==
                                       "12800"]['h'].astype(int).item())
                    except:
                        pass
                    result_value += result
                date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[date] = result_value
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)

        return Response(responseData)


class getChart18DataJnet(APIView):
    def get(self, request):
        url_list = []
        csv_file = "charts.csv"
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]
        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})
            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("by_participant_whole_day_J-NET.csv") != -1):
                        url_list.append("https://www.jpx.co.jp/"+k.get('href'))
            for url in url_list:
                s = requests.get(url).content
                data = pd.read_csv(io.StringIO(s.decode(
                    'utf-8')), header=None, names=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
                date = data['d'].loc[0]
                nuk_rows = list(
                    data[data['b'].str.contains("PUT_NK225_")].index.values)
                instrument_rows = list(
                    data[data['a'].str.contains("Instrument", na=False)].index.values)
                final_df_minus = pd.DataFrame()
                final_df_plus = pd.DataFrame()
                result_value = 0
                for x in nuk_rows:
                    result = 0
                    nuk_index_begin = instrument_rows.index(x)
                    nuk_index_ends = instrument_rows.index(x)+1
                    temp_df = data[instrument_rows[nuk_index_begin] +
                                   1:instrument_rows[nuk_index_ends]-1]
                    try:
                        if(temp_df[temp_df['a'] == "12800"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "12800"])
                            result -= (temp_df[temp_df['a'] ==
                                       "12800"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "12800"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "12800"])
                            result += (temp_df[temp_df['e'] ==
                                       "12800"]['h'].astype(int).item())
                    except:
                        pass
                    result_value += result
                date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[date] = result_value
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)

        return Response(responseData)


class getChart19Data(APIView):
    def get(self, request):
        url_list = []
        csv_file = "charts.csv"
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]
        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})
            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day.csv") != -1):
                        url_list.append("https://www.jpx.co.jp/"+k.get('href'))
            for url in url_list:
                s = requests.get(url).content
                data = pd.read_csv(io.StringIO(s.decode(
                    'utf-8')), header=None, names=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
                date = data['d'].loc[0]
                nuk_rows = list(
                    data[data['b'].str.contains("CAL_NK225_")].index.values)
                instrument_rows = list(
                    data[data['a'].str.contains("Instrument", na=False)].index.values)
                final_df_minus = pd.DataFrame()
                final_df_plus = pd.DataFrame()
                result_value = 0
                for x in nuk_rows:
                    result = 0
                    nuk_index_begin = instrument_rows.index(x)
                    nuk_index_ends = instrument_rows.index(x)+1
                    if(nuk_index_ends >= len(instrument_rows)):
                        temp_df = data[instrument_rows[nuk_index_begin] +
                                       1:instrument_rows[len(instrument_rows)-1]]
                    else:
                        temp_df = data[instrument_rows[nuk_index_begin] +
                                       1:instrument_rows[nuk_index_ends]-1]
                    try:
                        if(temp_df[temp_df['a'] == "11256"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "11256"])
                            result -= (temp_df[temp_df['a'] ==
                                       "11256"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "11256"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "11256"])
                            result += (temp_df[temp_df['e'] ==
                                       "11256"]['h'].astype(int).item())

                        if(temp_df[temp_df['a'] == "12330"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "12330"])
                            result -= (temp_df[temp_df['a'] ==
                                       "12330"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "12330"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "12330"])
                            result += (temp_df[temp_df['e'] ==
                                       "12330"]['h'].astype(int).item())

                        if(temp_df[temp_df['a'] == "12057"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "12057"])
                            result -= (temp_df[temp_df['a'] ==
                                       "12057"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "12057"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "12057"])
                            result += (temp_df[temp_df['e'] ==
                                       "12057"]['h'].astype(int).item())

                        if(temp_df[temp_df['a'] == "12560"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "12560"])
                            result -= (temp_df[temp_df['a'] ==
                                       "12560"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "12560"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "12560"])
                            result += (temp_df[temp_df['e'] ==
                                       "12560"]['h'].astype(int).item())

                        if(temp_df[temp_df['a'] == "11727"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "11727"])
                            result -= (temp_df[temp_df['a'] ==
                                       "11727"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "11727"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "11727"])
                            result += (temp_df[temp_df['e'] ==
                                       "11727"]['h'].astype(int).item())
                    except:
                        pass
                    result_value += result
                date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[date] = result_value
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)

        return Response(responseData)


class getChart19DataJnet(APIView):
    def get(self, request):
        url_list = []
        csv_file = "charts.csv"
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]
        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})
            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("by_participant_whole_day_J-NET.csv") != -1):
                        url_list.append("https://www.jpx.co.jp/"+k.get('href'))
            for url in url_list:
                s = requests.get(url).content
                data = pd.read_csv(io.StringIO(s.decode(
                    'utf-8')), header=None, names=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
                date = data['d'].loc[0]
                nuk_rows = list(
                    data[data['b'].str.contains("CAL_NK225_")].index.values)
                instrument_rows = list(
                    data[data['a'].str.contains("Instrument", na=False)].index.values)
                final_df_minus = pd.DataFrame()
                final_df_plus = pd.DataFrame()
                result_value = 0
                for x in nuk_rows:
                    result = 0
                    nuk_index_begin = instrument_rows.index(x)
                    nuk_index_ends = instrument_rows.index(x)+1
                    if(nuk_index_ends >= len(instrument_rows)):
                        temp_df = data[instrument_rows[nuk_index_begin] +
                                       1:instrument_rows[len(instrument_rows)-1]]
                    else:
                        temp_df = data[instrument_rows[nuk_index_begin] +
                                       1:instrument_rows[nuk_index_ends]-1]
                    try:
                        if(temp_df[temp_df['a'] == "11256"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "11256"])
                            result -= (temp_df[temp_df['a'] ==
                                       "11256"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "11256"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "11256"])
                            result += (temp_df[temp_df['e'] ==
                                       "11256"]['h'].astype(int).item())

                        if(temp_df[temp_df['a'] == "12330"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "12330"])
                            result -= (temp_df[temp_df['a'] ==
                                       "12330"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "12330"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "12330"])
                            result += (temp_df[temp_df['e'] ==
                                       "12330"]['h'].astype(int).item())

                        if(temp_df[temp_df['a'] == "12057"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "12057"])
                            result -= (temp_df[temp_df['a'] ==
                                       "12057"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "12057"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "12057"])
                            result += (temp_df[temp_df['e'] ==
                                       "12057"]['h'].astype(int).item())

                        if(temp_df[temp_df['a'] == "12560"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "12560"])
                            result -= (temp_df[temp_df['a'] ==
                                       "12560"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "12560"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "12560"])
                            result += (temp_df[temp_df['e'] ==
                                       "12560"]['h'].astype(int).item())

                        if(temp_df[temp_df['a'] == "11727"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "11727"])
                            result -= (temp_df[temp_df['a'] ==
                                       "11727"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "11727"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "11727"])
                            result += (temp_df[temp_df['e'] ==
                                       "11727"]['h'].astype(int).item())
                    except:
                        pass
                    result_value += result
                date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[date] = result_value
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)

        return Response(responseData)


class getChart20Data(APIView):
    def get(self, request):
        url_list = []
        csv_file = "charts.csv"
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]
        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})
            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("_by_participant_whole_day.csv") != -1):
                        url_list.append("https://www.jpx.co.jp/"+k.get('href'))
            for url in url_list:
                s = requests.get(url).content
                data = pd.read_csv(io.StringIO(s.decode(
                    'utf-8')), header=None, names=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
                date = data['d'].loc[0]
                nuk_rows = list(
                    data[data['b'].str.contains("PUT_NK225_")].index.values)
                instrument_rows = list(
                    data[data['a'].str.contains("Instrument", na=False)].index.values)
                final_df_minus = pd.DataFrame()
                final_df_plus = pd.DataFrame()
                result_value = 0
                for x in nuk_rows:
                    result = 0
                    nuk_index_begin = instrument_rows.index(x)
                    nuk_index_ends = instrument_rows.index(x)+1
                    temp_df = data[instrument_rows[nuk_index_begin] +
                                   1:instrument_rows[nuk_index_ends]-1]
                    try:
                        if(temp_df[temp_df['a'] == "11256"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "11256"])
                            result -= (temp_df[temp_df['a'] ==
                                       "11256"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "11256"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "11256"])
                            result += (temp_df[temp_df['e'] ==
                                       "11256"]['h'].astype(int).item())

                        if(temp_df[temp_df['a'] == "12330"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "12330"])
                            result -= (temp_df[temp_df['a'] ==
                                       "12330"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "12330"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "12330"])
                            result += (temp_df[temp_df['e'] ==
                                       "12330"]['h'].astype(int).item())

                        if(temp_df[temp_df['a'] == "12057"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "12057"])
                            result -= (temp_df[temp_df['a'] ==
                                       "12057"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "12057"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "12057"])
                            result += (temp_df[temp_df['e'] ==
                                       "12057"]['h'].astype(int).item())

                        if(temp_df[temp_df['a'] == "12560"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "12560"])
                            result -= (temp_df[temp_df['a'] ==
                                       "12560"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "12560"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "12560"])
                            result += (temp_df[temp_df['e'] ==
                                       "12560"]['h'].astype(int).item())

                        if(temp_df[temp_df['a'] == "11727"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "11727"])
                            result -= (temp_df[temp_df['a'] ==
                                       "11727"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "11727"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "11727"])
                            result += (temp_df[temp_df['e'] ==
                                       "11727"]['h'].astype(int).item())
                    except:
                        pass
                    result_value += result
                date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[date] = result_value
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)

        return Response(responseData)


class getChart20DataJnet(APIView):
    def get(self, request):
        url_list = []
        csv_file = "charts.csv"
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
                x['month'] == 12 or (x['month'] >= 1 and x['month'] <= 3))]
        result_json = {}
        for k in main_urls_list:
            url = k
            agent = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
            page = requests.get(url,  headers=agent)
            page = page.text
            soup = BeautifulSoup(page, "html.parser")
            services = soup.findAll('td', {'class': 'a-center'})
            url_list = []
            for x in services:
                temp = x.findAll('a')
                for k in temp:
                    if((k.get('href')).find("by_participant_whole_day_J-NET.csv") != -1):
                        url_list.append("https://www.jpx.co.jp/"+k.get('href'))
            for url in url_list:
                s = requests.get(url).content
                data = pd.read_csv(io.StringIO(s.decode(
                    'utf-8')), header=None, names=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
                date = data['d'].loc[0]
                nuk_rows = list(
                    data[data['b'].str.contains("PUT_NK225_")].index.values)
                instrument_rows = list(
                    data[data['a'].str.contains("Instrument", na=False)].index.values)
                final_df_minus = pd.DataFrame()
                final_df_plus = pd.DataFrame()
                result_value = 0
                for x in nuk_rows:
                    result = 0
                    nuk_index_begin = instrument_rows.index(x)
                    nuk_index_ends = instrument_rows.index(x)+1
                    temp_df = data[instrument_rows[nuk_index_begin] +
                                   1:instrument_rows[nuk_index_ends]-1]
                    try:
                        if(temp_df[temp_df['a'] == "11256"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "11256"])
                            result -= (temp_df[temp_df['a'] ==
                                       "11256"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "11256"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "11256"])
                            result += (temp_df[temp_df['e'] ==
                                       "11256"]['h'].astype(int).item())

                        if(temp_df[temp_df['a'] == "12330"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "12330"])
                            result -= (temp_df[temp_df['a'] ==
                                       "12330"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "12330"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "12330"])
                            result += (temp_df[temp_df['e'] ==
                                       "12330"]['h'].astype(int).item())

                        if(temp_df[temp_df['a'] == "12057"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "12057"])
                            result -= (temp_df[temp_df['a'] ==
                                       "12057"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "12057"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "12057"])
                            result += (temp_df[temp_df['e'] ==
                                       "12057"]['h'].astype(int).item())

                        if(temp_df[temp_df['a'] == "12560"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "12560"])
                            result -= (temp_df[temp_df['a'] ==
                                       "12560"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "12560"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "12560"])
                            result += (temp_df[temp_df['e'] ==
                                       "12560"]['h'].astype(int).item())

                        if(temp_df[temp_df['a'] == "11727"].empty is False):
                            final_df_minus = final_df_minus.append(
                                temp_df[temp_df['a'] == "11727"])
                            result -= (temp_df[temp_df['a'] ==
                                       "11727"]['d'].astype(int).item())
                        if(temp_df[temp_df['e'] == "11727"].empty is False):
                            final_df_plus = final_df_plus.append(
                                temp_df[temp_df['e'] == "11727"])
                            result += (temp_df[temp_df['e'] ==
                                       "11727"]['h'].astype(int).item())
                    except:
                        pass
                    result_value += result
                date = str(date)[:4]+"-"+str(date)[4:6]+"-"+str(date)[6:]
                result_json[date] = result_value
        responseData = []
        for k in result_json:
            if(result_json[k] >= 0):
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#ef553b"}
            else:
                temp = {"x": k[:10], "volume": result_json[k],
                        "stroke": "#636efa"}
            responseData.append(temp)

        return Response(responseData)


def archive_price_data(s, e):
    start_date_obj = datetime.strptime(s, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(e, "%Y-%m-%d").date()

    yy = start_date_obj.year
    mm = start_date_obj.month
    dd = start_date_obj.day

    url = "http://225navi.com/data/"
    r = requests.get(url)
    html_content = r.content
    soup = BeautifulSoup(html_content, "html.parser")
    soup.prettify()

    container = soup.find(class_="sc_table")
    table = container.find("table")

    dates = []
    flag = False
    for td in table.find_all("tr"):
        for i in td:
            try:
                if datetime.strptime(i.text.strip(), '%Y/%m/%d').date() > start_date_obj and datetime.strptime(i.text.strip(), '%Y/%m/%d').date() < end_date_obj:
                    p = i.text.strip()
                    p = p.replace('\n', '')
                    dates.append(p)
            except:
                pass
        if flag == True:
            break

    price = []
    for i in dates:
        if i == "" or "/" in i:
            pass
        else:
            price.append(i)

    limit = len(dates)

    value = []
    flag = False
    for td in table.find_all("tr"):
        for i in td:
            try:
                if i.text.strip() == f"{yy}/{mm}/{dd}":
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

    res = []
    for i in value:
        if i == "" or "/" in i:
            pass
        else:
            res.append(i)
    res = res[14:]
    res = res[0:-1:8]
    main_res = list(map(int, res))
    main_res = main_res[::-1]
    main_res = main_res[:limit+1]

    return main_res


def archive_price_data_7to10(s, e):
    start_date_obj = datetime.strptime(s, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(e, "%Y-%m-%d").date()

    yy = start_date_obj.year
    mm = start_date_obj.month
    dd = start_date_obj.day

    url = "http://225navi.com/data/data5/"
    r = requests.get(url)
    html_content = r.content
    soup = BeautifulSoup(html_content, "html.parser")
    soup.prettify()

    container = soup.find(class_="sc_table")
    table = container.find("table")

    dates = []
    flag = False
    for td in table.find_all("tr"):
        for i in td:
            try:
                if datetime.strptime(i.text.strip(), '%Y/%m/%d').date() > start_date_obj and datetime.strptime(i.text.strip(), '%Y/%m/%d').date() < end_date_obj:
                    p = i.text.strip()
                    p = p.replace('\n', '')
                    dates.append(p)
            except:
                pass
        if flag == True:
            break

    price = []
    for i in dates:
        if i == "" or "/" in i:
            pass
        else:
            price.append(i)

    limit = len(dates)

    value = []
    flag = False
    for td in table.find_all("tr"):
        for i in td:
            try:
                if i.text.strip() == f"{yy}/{mm}/{dd}":
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

    res = []
    for i in value:
        if i == "" or "/" in i:
            pass
        else:
            res.append(i)
    res = res[14:]
    res = res[0:-1:8]
    main_res = list(map(float, res))
    main_res = main_res[::-1]
    main_res = main_res[:limit+1]

    return main_res

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(BASE_DIR)
conn = create_connection(f'/Users/shehrozkapoor/Desktop/graph_project/chart_nikkei/charts_project/db.sqlite3')
# conn = create_connection('/home/ubuntu/chart_nikkei/charts_project/db.sqlite3')
cur = conn.cursor()


def select_futures_data(conn, start_date, end_date, companies, descriptions):
    # conn = create_connection('D:\JPX\chart_nikkei\charts_project\db.sqlite3')
    conn = create_connection('/home/ubuntu/chart_nikkei/charts_project/db.sqlite3')
    cur = conn.cursor()

    query = f"SELECT date, sum(left_val) from home_daily_data WHERE company_id IN ({','.join(str(_) for _ in companies)}) AND description IN ('{','.join(str(_) for _ in descriptions)}') AND date BETWEEN '{start_date}' AND '{end_date}' GROUP by date ORDER by date"

    query_right = f"SELECT date, sum(right_val) from home_daily_data WHERE company_id_right IN ({','.join(str(_) for _ in companies)}) AND description IN ('{','.join(str(_) for _ in descriptions)}') AND date BETWEEN '{start_date}' AND '{end_date}' GROUP by date ORDER by date"

    cur.execute(query)
    data = cur.fetchall()
    cur.execute(query_right)
    data_right = cur.fetchall()
    
    dates = []
    for i in data:
        dates.append(i[0])

    dates_right = []
    for i in data_right:
        dates_right.append(i[0])

    def l_func(x, y): return list((set(x) - set(y))) + list((set(y) - set(x)))

    if len(dates) > len(dates_right):
        non_match = l_func(dates, dates_right)

        first_non_match = []
        second_non_match = []
        for i in dates:
            if i not in dates_right:
                first_non_match.append(i)
        for i in dates_right:
            if i not in dates:
                second_non_match.append(i)

        if len(first_non_match)>0 and len(second_non_match)>0:

            first_non_match_index = []
            for i in second_non_match:
                if i in dates_right:
                    first_non_match_index.append(dates_right.index(i))

            for i in first_non_match_index:
                data.insert(i, str(0))

            for i in range(len(data)):
                if data[i] == '0':
                    data[i] = (data_right[i][0], 0)


            second_non_match_index = []
            for i in first_non_match:
                if i in dates:
                    second_non_match_index.append(dates.index(i))

            for i in second_non_match_index:
                data_right.insert(i+1, str(0))

            for i in range(len(data_right)):
                if data_right[i] == '0':
                    data_right[i] = (data[i][0], 0)

            rows = []
            for i in range(len(data)):
                rows.append((data_right[i][0], data[i][1], data_right[i][1]))    
            return rows

        else:

            non_match_index = []
            for i in non_match:
                if i in dates:
                    non_match_index.append(dates.index(i))

            for i in non_match_index:
                data_right.insert(i, str(0))

            rows = []
            for i in range(len(data_right)):
                if data_right[i] == str(0):
                    rows.append((data[i][0], data[i][1], 0))
                elif data_right[i][0] == data[i][0]:
                    rows.append((data[i][0], data[i][1], data_right[i][1]))

            return rows

    elif len(dates) < len(dates_right):
        non_match = l_func(dates, dates_right)

        first_non_match = []
        second_non_match = []
        for i in dates:
            if i not in dates_right:
                first_non_match.append(i)
        for i in dates_right:
            if i not in dates:
                second_non_match.append(i)

        if len(first_non_match)>0 and len(second_non_match)>0:

            first_non_match_index = []
            for i in second_non_match:
                if i in dates_right:
                    first_non_match_index.append(dates_right.index(i))

            for i in first_non_match_index:
                data.insert(i, str(0))

            for i in range(len(data)):
                if data[i] == '0':
                    data[i] = (data_right[i][0], 0)


            second_non_match_index = []
            for i in first_non_match:
                if i in dates:
                    second_non_match_index.append(dates.index(i))

            for i in second_non_match_index:
                data_right.insert(i+1, str(0))

            for i in range(len(data_right)):
                if data_right[i] == '0':
                    data_right[i] = (data[i][0], 0)

            rows = []
            for i in range(len(data)):
                rows.append((data_right[i][0], data[i][1], data_right[i][1]))    
            return rows

        else:
            non_match_index = []
            for i in non_match:
                if i in dates_right:
                    non_match_index.append(dates_right.index(i))

            for i in non_match_index:
                data.insert(i, str(0))

            rows = []
            for i in range(len(data)):
                if data[i] == str(0):
                    rows.append((data_right[i][0], 0, data_right[i][1]))
                elif data[i][0] == data[i][0]:
                    rows.append((data_right[i][0], data[i][1], data_right[i][1]))

            return rows

    else:
        non_match = l_func(dates, dates_right)
        if len(non_match)>1:
            non_match_index = []
            for i in non_match:
                if i in dates:
                    non_match_index.append(dates.index(i))

            non_match_element = []
            for i in non_match_index:
                temp = list(data[i])
                temp.insert(1,0)
                non_match_element.append(tuple(temp))

            for i in range(len(non_match_index)):
                data_right.insert(non_match_index[i]+1,non_match_element[i])

            dates_next = []
            dates_right_next = []
            for i in data:
                dates_next.append(i[0])
            for i in data_right:
                dates_right_next.append(i[0])

            non_match_next = l_func(dates, dates_right)

            non_match_index_next = []
            for i in non_match_next:
                if i in dates:
                    non_match_index_next.append(dates.index(i))

                if len(dates_next) > len(dates_right_next):
                    non_match = l_func(dates_next, dates_right_next)

                    non_match_index = []
                    for i in non_match:
                        if i in dates_next:
                            non_match_index.append(dates_next.index(i))

                    for i in non_match_index:
                        data_right.insert(i, str(0))

                    rows = []
                    for i in range(len(data_right)):
                        if data_right[i] == str(0):
                            rows.append((data[i][0], data[i][1], 0))
                        elif data_right[i][0] == data[i][0]:
                            rows.append((data[i][0], data[i][1], data_right[i][1]))

                    return rows

                elif len(dates_next) < len(dates_right_next):
                    non_match = l_func(dates_next, dates_right_next)

                    non_match_index = []
                    for i in non_match:
                        if i in dates_right_next:
                            non_match_index.append(dates_right_next.index(i))

                    for i in non_match_index:
                        data.insert(i, str(0))

                    rows = []
                    for i in range(len(data)):
                        if data[i] == str(0):
                            rows.append((data_right[i][0], 0, data_right[i][1]))
                        elif data[i][0] == data[i][0]:
                            rows.append((data_right[i][0], data[i][1], data_right[i][1]))
                    return rows
        else:
            rows = []
            for i in range(len(data)):
                if data[i] == str(0):
                    rows.append((data_right[i][0], data_right[i][1], 0))
                elif data[i][0] == data[i][0]:
                    rows.append((data_right[i][0], data_right[i][1], data[i][1]))
            return rows

def first(companies, descriptions, title, start_date=start_date, end_date=end_date):
    # conn = create_connection('D:\JPX\chart_nikkei\charts_project\db.sqlite3')
    conn = create_connection('/home/ubuntu/chart_nikkei/charts_project/db.sqlite3')
    cur = conn.cursor()

    raw_data = select_futures_data(
        conn, start_date, end_date, companies, descriptions)
    return raw_data


@api_view(['GET'])
def get_futures_figure(request, graphid):
    # conn = create_connection('D:\JPX\chart_nikkei\charts_project\db.sqlite3')
    conn = create_connection('/home/ubuntu/chart_nikkei/charts_project/db.sqlite3')
    cur = conn.cursor()

    modal_title = ""
    raw_data = None
    line = None
    if graphid >= 0 and graphid <= 5:
        for idx, metadata in enumerate(FUTURES_GRAPHS_METADATA):
            if idx == int(graphid):
                raw_data = first(*metadata)
                modal_title = metadata[2]
        line = price_data()

    if graphid >= 6 and graphid <= 9:
        for idx, metadata in enumerate(TOPIX_FUTURES_GRAPHS_METADATA):
            if idx+6 == int(graphid):
                raw_data = first(*metadata)
                modal_title = metadata[2]
        line = price_data_7to10()

    graph_dates_range = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in
                         range((end_date - start_date).days)]
    graph_data = {'Dates': [], 'Diff': [], 'color': []}

    l1 = []

    for date1, left_val, right_val in raw_data:
        if date1 in graph_dates_range:
            l1.append(date1)
            graph_data['Diff'].append(right_val - left_val)
            if right_val - left_val < 0:
                graph_data['color'].append('#ff5252')
            else:
                graph_data['color'].append('#636efa')

    for i in l1:
        def create(y, m, d):
            graph_data['Dates'].append(date(y, m, d).strftime("%m月%d日"))
        create(y=int(i[0:4]), m=int(i[5:7]), d=int(i[8:10]))

    return Response({'data': graph_data,  'line': line, 'modal_title': modal_title})


def select_options_data(conn, start_date, end_date, companies, descriptions):
    # conn = create_connection('D:\JPX\chart_nikkei\charts_project\db.sqlite3')
    conn = create_connection('/home/ubuntu/chart_nikkei/charts_project/db.sqlite3')
    cur = conn.cursor()

    query = ("SELECT date, SUM(left_val) * -1 as left_val, SUM(right_val)  as right_val FROM home_daily_data "
             "WHERE company_id IN ({}) AND description LIKE '{}%' AND date BETWEEN '{}' AND '{}' "
             "GROUP BY date".format(','.join(str(_) for _ in companies), descriptions[0], start_date, end_date))

    query1 = ("SELECT date, SUM(left_val) * -1 as left_val, SUM(right_val)  as right_val FROM home_daily_data "
              "WHERE company_id_right IN ({}) AND description LIKE '{}%' AND date BETWEEN '{}' AND '{}' "
              "GROUP BY date".format(','.join(str(_) for _ in companies), descriptions[0], start_date, end_date))

    cur.execute(query)
    left = cur.fetchall()

    cur.execute(query1)
    right = cur.fetchall()

    # total_desc = []
    # for i in left:
    #     total_desc.append(i[0])
    # for i in right:
    #     if i[0] not in total_desc:
    #         total_desc.append(i[0])

    # row = []
    # for i in total_desc:
    #     for j in left:
    #         if i == j[0]:
    #             row.append((i, j[1]))

    # zero = []
    # for i in total_desc:
    #     for j in row:
    #         if j[0] not in total_desc:
    #             pass
    #     else:
    #         zero.append((i, 0))

    # zero = zero[len(row):]

    # for i in zero:
    #     row.append(i)

    # rows = []
    # for i in row:
    #     for j in right:
    #         if i[0] == j[0]:
    #             rows.append((i[0], i[1], j[2]))

    # print(rows)
    # return rows

    total = []
    for i in left:
        total.append([i[0], 0, 0])

    for i in right:
        if i[0] not in total:
            total.append([i[0], 0, 0])

    for i in total:
        for j in left:
            if i[0] == j[0]:
                i[1] = j[1]

    for i in total:
        for j in right:
            if i[0] == j[0]:
                i[2] = j[2]

    row = []
    for i in total:
        row.append(tuple(i))

    row = list(set(row))

    return row


def last(companies, descriptions, title, start_date=start_date_, end_date=end_date_):
    # conn = create_connection('D:\JPX\chart_nikkei\charts_project\db.sqlite3')
    conn = create_connection('/home/ubuntu/chart_nikkei/charts_project/db.sqlite3')
    cur = conn.cursor()

    raw_data = select_options_data(
        conn, start_date , end_date, companies, descriptions)
    return raw_data


def date_():
    query = f'SELECT date from home_daily_data WHERE date BETWEEN "{start_date}" and "{end_date}" order by date'
    data = cur.execute(query)
    dates = []
    for row in data:
        if row[0] not in dates:
            dates.append(row[0])

    global date_x
    date_x = []

    for i in dates:
        def create(y, m, d):
            date_x.append(date(y, m, d).strftime("%m月%d日"))
        create(y=int(i[0:4]), m=int(i[5:7]), d=int(i[8:10]))

    return date_x


date_()


@api_view(['GET'])
def get_options_figure(request, graphid):
    # conn = create_connection('D:\JPX\chart_nikkei\charts_project\db.sqlite3')
    conn = create_connection('/home/ubuntu/chart_nikkei/charts_project/db.sqlite3')
    cur = conn.cursor()
    modal_title = ""
    raw_data = None
    if graphid >= 10 and graphid <= 19:
        for idx, metadata in enumerate(OPTIONS_GRAPHS_METADATA):
            if idx+10 == int(graphid):
                raw_data = last(*metadata)
                modal_title = metadata[2]

    sorted_data = sorted([(d, l, r)
                    for d, l, r in raw_data], key=lambda tup: tup[0])

    graph_data = {'Date': [], 'put': [], 'call': []}
    Temp_date = []
    for d, left_val, right_val in sorted_data:
        Temp_date.append(str(d))
        graph_data['put'].append(left_val)
        graph_data['call'].append(right_val)

    for i in Temp_date:
        def create(y, m, d):
            graph_data['Date'].append(date(y, m, d).strftime("%m月%d日"))
        create(y=int(i[0:4]), m=int(i[5:7]), d=int(i[8:10]))

    return Response({'data': graph_data, 'modal_title': modal_title, 'date_x': date_x})


def company_profile(request):
    if request.session.has_key('user'):
        return render(request, "company_profile.html")
    else:
        return redirect('login')


def risk_description(request):
    if request.session.has_key('user'):
        return render(request, "risk.html")
    else:
        return redirect('login')


def disclaimer(request):
    if request.session.has_key('user'):
        return render(request, "disclaimer.html")
    else:
        return redirect('login')

# --------------------------------------------------------==----------------------------------------------
# --------------------------------------------------------==----------------------------------------------
# --------------------------------------------------------==----------------------------------------------
# --------------------------------------------------------==----------------------------------------------


def archive(request):
    if request.session.has_key('user'):
        return render(request, "archive.html")
    else:
        return redirect('login')


@api_view(['GET'])
def eachchart(request, chartid):
    if request.session.has_key('user'):

        month_list = [3, 6, 9, 12]
        friday_list = []
        pairs = []
        charts = {}

        today_str = today.strftime("%Y-%m-%d")
        dates = ["2021-9-21", today_str]
        start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
        dates = OrderedDict(((start + timedelta(_)).strftime(r"%Y-%m"), None)
                            for _ in range((end - start).days)).keys()
        c = 0
        for i in dates:
            if int(i[5:]) in month_list:
                friday_list.append(second_friday(i[0:4], i[5:]))

        for i in range(len(friday_list)-1):
            pairs.append(f"{friday_list[i]} - {friday_list[i+1]}")

        if int(pairs[-1][18:20])==today.month and int(pairs[-1][21:])>today.day:
            pairs.remove(pairs[-1])

        for i in pairs:
            if int(i[5:7]) == 9 and int(i[0:4])==2021:
                start_date = '2021-09-17'
                end_date = i[13:]
            else:
                start_date = i[0:10]
                end_date = i[13:]

            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

            def select_futures_data(conn, start_date, end_date, companies, descriptions):
                # conn = create_connection('D:\JPX\chart_nikkei\charts_project\db.sqlite3')
                conn = create_connection('/home/ubuntu/chart_nikkei/charts_project/db.sqlite3')
                cur = conn.cursor()

                query = f"SELECT date, sum(left_val) from home_daily_data WHERE company_id IN ({','.join(str(_) for _ in companies)}) AND description IN ('{','.join(str(_) for _ in descriptions)}') AND date BETWEEN '{start_date}' AND '{end_date}' GROUP by date ORDER by date"

                query_right = f"SELECT date, sum(right_val) from home_daily_data WHERE company_id_right IN ({','.join(str(_) for _ in companies)}) AND description IN ('{','.join(str(_) for _ in descriptions)}') AND date BETWEEN '{start_date}' AND '{end_date}' GROUP by date ORDER by date"

                cur.execute(query)
                data = cur.fetchall()
                cur.execute(query_right)
                data_right = cur.fetchall()
                
                dates = []
                for i in data:
                    dates.append(i[0])

                dates_right = []
                for i in data_right:
                    dates_right.append(i[0])

                def l_func(x, y): return list((set(x) - set(y))) + list((set(y) - set(x)))

                if len(dates) > len(dates_right):
                    non_match = l_func(dates, dates_right)

                    first_non_match = []
                    second_non_match = []
                    for i in dates:
                        if i not in dates_right:
                            first_non_match.append(i)
                    for i in dates_right:
                        if i not in dates:
                            second_non_match.append(i)

                    if len(first_non_match)>0 and len(second_non_match)>0:

                        first_non_match_index = []
                        for i in second_non_match:
                            if i in dates_right:
                                first_non_match_index.append(dates_right.index(i))

                        for i in first_non_match_index:
                            data.insert(i, str(0))

                        for i in range(len(data)):
                            if data[i] == '0':
                                data[i] = (data_right[i][0], 0)


                        second_non_match_index = []
                        for i in first_non_match:
                            if i in dates:
                                second_non_match_index.append(dates.index(i))

                        for i in second_non_match_index:
                            data_right.insert(i+1, str(0))

                        for i in range(len(data_right)):
                            if data_right[i] == '0':
                                data_right[i] = (data[i][0], 0)

                        rows = []
                        for i in range(len(data)):
                            rows.append((data_right[i][0], data[i][1], data_right[i][1]))    
                        return rows

                    else:

                        non_match_index = []
                        for i in non_match:
                            if i in dates:
                                non_match_index.append(dates.index(i))

                        for i in non_match_index:
                            data_right.insert(i, str(0))

                        rows = []
                        for i in range(len(data_right)):
                            if data_right[i] == str(0):
                                rows.append((data[i][0], data[i][1], 0))
                            elif data_right[i][0] == data[i][0]:
                                rows.append((data[i][0], data[i][1], data_right[i][1]))

                        return rows

                elif len(dates) < len(dates_right):
                    non_match = l_func(dates, dates_right)

                    first_non_match = []
                    second_non_match = []
                    for i in dates:
                        if i not in dates_right:
                            first_non_match.append(i)
                    for i in dates_right:
                        if i not in dates:
                            second_non_match.append(i)

                    if len(first_non_match)>0 and len(second_non_match)>0:

                        first_non_match_index = []
                        for i in second_non_match:
                            if i in dates_right:
                                first_non_match_index.append(dates_right.index(i))

                        for i in first_non_match_index:
                            data.insert(i, str(0))

                        for i in range(len(data)):
                            if data[i] == '0':
                                data[i] = (data_right[i][0], 0)


                        second_non_match_index = []
                        for i in first_non_match:
                            if i in dates:
                                second_non_match_index.append(dates.index(i))

                        for i in second_non_match_index:
                            data_right.insert(i+1, str(0))

                        for i in range(len(data_right)):
                            if data_right[i] == '0':
                                data_right[i] = (data[i][0], 0)

                        rows = []
                        for i in range(len(data)):
                            rows.append((data_right[i][0], data[i][1], data_right[i][1]))    
                        return rows

                    else:
                        non_match_index = []
                        for i in non_match:
                            if i in dates_right:
                                non_match_index.append(dates_right.index(i))

                        for i in non_match_index:
                            data.insert(i, str(0))

                        rows = []
                        for i in range(len(data)):
                            if data[i] == str(0):
                                rows.append((data_right[i][0], 0, data_right[i][1]))
                            elif data[i][0] == data[i][0]:
                                rows.append((data_right[i][0], data[i][1], data_right[i][1]))

                        return rows

                else:
                    non_match = l_func(dates, dates_right)
                    if len(non_match)>1:
                        non_match_index = []
                        for i in non_match:
                            if i in dates:
                                non_match_index.append(dates.index(i))

                        non_match_element = []
                        for i in non_match_index:
                            temp = list(data[i])
                            temp.insert(1,0)
                            non_match_element.append(tuple(temp))

                        for i in range(len(non_match_index)):
                            data_right.insert(non_match_index[i]+1,non_match_element[i])

                        dates_next = []
                        dates_right_next = []
                        for i in data:
                            dates_next.append(i[0])
                        for i in data_right:
                            dates_right_next.append(i[0])

                        non_match_next = l_func(dates, dates_right)

                        non_match_index_next = []
                        for i in non_match_next:
                            if i in dates:
                                non_match_index_next.append(dates.index(i))

                            if len(dates_next) > len(dates_right_next):
                                non_match = l_func(dates_next, dates_right_next)

                                non_match_index = []
                                for i in non_match:
                                    if i in dates_next:
                                        non_match_index.append(dates_next.index(i))

                                for i in non_match_index:
                                    data_right.insert(i, str(0))

                                rows = []
                                for i in range(len(data_right)):
                                    if data_right[i] == str(0):
                                        rows.append((data[i][0], data[i][1], 0))
                                    elif data_right[i][0] == data[i][0]:
                                        rows.append((data[i][0], data[i][1], data_right[i][1]))

                                return rows

                            elif len(dates_next) < len(dates_right_next):
                                non_match = l_func(dates_next, dates_right_next)

                                non_match_index = []
                                for i in non_match:
                                    if i in dates_right_next:
                                        non_match_index.append(dates_right_next.index(i))

                                for i in non_match_index:
                                    data.insert(i, str(0))

                                rows = []
                                for i in range(len(data)):
                                    if data[i] == str(0):
                                        rows.append((data_right[i][0], 0, data_right[i][1]))
                                    elif data[i][0] == data[i][0]:
                                        rows.append((data_right[i][0], data[i][1], data_right[i][1]))
                                return rows
                    else:
                        rows = []
                        for i in range(len(data)):
                            if data[i] == str(0):
                                rows.append((data_right[i][0], data_right[i][1], 0))
                            elif data[i][0] == data[i][0]:
                                rows.append((data_right[i][0], data_right[i][1], data[i][1]))
                        return rows

            def first(companies, descriptions, title, start_date=start_date, end_date=end_date):
                # conn = create_connection('D:\JPX\chart_nikkei\charts_project\db.sqlite3')
                conn = create_connection('/home/ubuntu/chart_nikkei/charts_project/db.sqlite3')
                cur = conn.cursor()

                raw_data = select_futures_data(
                    conn, start_date, end_date, companies, descriptions)
                return raw_data

            FUTURES_GRAPHS_METADATA_ARCHIVE = [
                ([12479, 11788, 12410, 11746, 11635, 12176, 12428, 11560, 11714,
                  12800, 12792], [f'NIKKEI 225 FUT {i[15:17]}{i[18:20]}'], '日経225ラージ先物外資系手口'),
                ([11635], [
                 f'NIKKEI 225 FUT {i[15:17]}{i[18:20]}'], '日経225ラージ先物クレディスイス手口'),
                ([11560], [
                 f'NIKKEI 225 FUT {i[15:17]}{i[18:20]}'], '日経225ラージ先物ゴールドマンサックス手口'),
                ([12800], [
                 f'NIKKEI 225 FUT {i[15:17]}{i[18:20]}'], '日経225ラージ先物モルガンスタンレー手口'),
                ([11256, 12330, 12057, 12560, 11727], [
                    f'NIKKEI 225 FUT {i[15:17]}{i[18:20]}'], '日経225先物国内ネット系証券手口'),
                ([11256, 12330, 12057, 12560, 11727], [
                    f'MINI NK225 FUT {i[15:17]}{i[18:20]}'], '日経225mini先物国内ネット系証券手口'),
            ]

            TOPIX_FUTURES_GRAPHS_METADATA_ARCHIVE = [
                ([12479, 11788, 12410, 11746, 11635, 12176, 12428, 11560,
                  11714, 12800, 12792], [f'TOPIX FUT {i[15:17]}{i[18:20]}'], 'TOPIX先物外資系手口'),
                ([11635], [
                 f'TOPIX FUT {i[15:17]}{i[18:20]}'], 'TOPIX先物クレディスイス手口'),
                ([11560], [
                 f'TOPIX FUT {i[15:17]}{i[18:20]}'], 'TOPIX先物ゴールドマンサックス手口'),
                ([12800], [
                 f'TOPIX FUT {i[15:17]}{i[18:20]}'], 'TOPIX先物モルガンスタンレー手口'),
            ]

            chart_title = ""
            raw_data = None
            chart_line = None
            if chartid >= 0 and chartid <= 5:
                for idx, metadata in enumerate(FUTURES_GRAPHS_METADATA_ARCHIVE):
                    if idx == int(chartid):
                        raw_data = first(*metadata)
                        chart_title = f'{metadata[2]}       {i[0:4]} {i[5:7]} - {i[13:17]} {i[18:20]}'
                chart_line = archive_price_data(start_date, end_date)

            if chartid >= 6 and chartid <= 9:
                for idx, metadata in enumerate(TOPIX_FUTURES_GRAPHS_METADATA_ARCHIVE):
                    if idx+6 == int(chartid):
                        raw_data = first(*metadata)
                        chart_title = f'{metadata[2]}       {i[0:4]} {i[5:7]} - {i[13:17]} {i[18:20]}'
                chart_line = archive_price_data_7to10(start_date, end_date)

            graph_dates_range = [(start_date_obj + timedelta(days=i)).strftime('%Y-%m-%d') for i in
                                 range((end_date_obj - start_date_obj).days)]
            chart_data = {'Dates': [], 'Diff': [], 'color': []}

            l1 = []

            for date1, left_val, right_val in raw_data:
                if date1 in graph_dates_range:
                    l1.append(date1)
                    chart_data['Diff'].append(right_val - left_val)
                    if right_val - left_val < 0:
                        chart_data['color'].append('#ff5252')
                    else:
                        chart_data['color'].append('#636efa')

            for i in l1:
                def create(y, m, d):
                    chart_data['Dates'].append(
                        date(y, m, d).strftime("%m月%d日"))
                create(y=int(i[0:4]), m=int(i[5:7]), d=int(i[8:10]))

            charts[f'charts{c}'] = {'data': chart_data,
                                    'chart_line': chart_line, 'chart_title': chart_title}
            c += 1

        return Response({'charts': charts})


@api_view(['GET'])
def eachchart_options(request, chartid):
    if request.session.has_key('user'):
        months = []
        pairs = []
        friday_pairs = []
        charts_options = {}

        today_str = today.strftime("%Y-%m-%d")
        dates = ["2021-9-21", today_str]
        start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
        dates = OrderedDict(((start + timedelta(_)).strftime(r"%Y-%m"), None)
                            for _ in range((end - start).days)).keys()
        for i in dates:
            months.append(i)

        for i in range(len(months)-1):
            pairs.append(f'{months[i]} - {months[i+1]}')

        for i in pairs:
            friday_pairs.append(
                f'{second_friday(i[0:4],i[5:7])} - {second_friday(i[10:14],i[15:17])}')

        c = 10
        if int(friday_pairs[-1][18:20])==today.month and int(friday_pairs[-1][21:])>today.day:
            friday_pairs.remove(friday_pairs[-1])

        for i in friday_pairs:
            start_date_archive = i[0:10]
            end_date_archive = i[13:]

            start_date_obj = datetime.strptime(start_date_archive, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(end_date_archive, "%Y-%m-%d").date()
            end_date_obj = end_date_obj - timedelta(days=1)

            end_date_archive = end_date_obj.strftime("%Y-%m-%d")

            def date_():
                # conn = create_connection('D:\JPX\chart_nikkei\charts_project\db.sqlite3')
                conn = create_connection('/home/ubuntu/chart_nikkei/charts_project/db.sqlite3')
                cur = conn.cursor()
                query = f'SELECT date from home_daily_data WHERE date BETWEEN "{start_date_archive}" and "{end_date_archive}" order by date'
                data = cur.execute(query)
                dates = []
                for row in data:
                    if row[0] not in dates:
                        dates.append(row[0])

                date_archive = []

                for i in dates:
                    def create(y, m, d):
                        date_archive.append(date(y, m, d).strftime("%m月%d日"))
                    create(y=int(i[0:4]), m=int(i[5:7]), d=int(i[8:10]))

                return date_archive

            def select_options_data(conn, start_date_archive, end_date_archive, companies, descriptions):
                # conn = create_connection('D:\JPX\chart_nikkei\charts_project\db.sqlite3')
                conn = create_connection('/home/ubuntu/chart_nikkei/charts_project/db.sqlite3')
                cur = conn.cursor()

                query = ("SELECT date, SUM(left_val) * -1 as left_val, SUM(right_val) as right_val FROM home_daily_data "
                         "WHERE company_id IN ({}) AND description LIKE '{}%' AND date BETWEEN '{}' AND '{}' "
                         "GROUP BY date".format(','.join(str(_) for _ in companies), descriptions[0], start_date_archive, end_date_archive))

                query1 = ("SELECT date, SUM(left_val) * -1 as left_val, SUM(right_val) as right_val FROM home_daily_data "
                          "WHERE company_id_right IN ({}) AND description LIKE '{}%' AND date BETWEEN '{}' AND '{}' "
                          "GROUP BY date".format(','.join(str(_) for _ in companies), descriptions[0], start_date_archive, end_date_archive))

                cur.execute(query)
                left = cur.fetchall()

                cur.execute(query1)
                right = cur.fetchall()

                total = []
                for i in left:
                    total.append([i[0], 0, 0])

                for i in right:
                    if i[0] not in total:
                        total.append([i[0], 0, 0])

                for i in total:
                    for j in left:
                        if i[0] == j[0]:
                            i[1] = j[1]

                for i in total:
                    for j in right:
                        if i[0] == j[0]:
                            i[2] = j[2]

                row = []
                for i in total:
                    row.append(tuple(i))
                row = list(set(row))

                return row
            def last(companies, descriptions, title, start_date_archive=start_date_archive, end_date_archive=end_date_archive):
                # conn = create_connection('D:\JPX\chart_nikkei\charts_project\db.sqlite3')
                conn = create_connection('/home/ubuntu/chart_nikkei/charts_project/db.sqlite3')
                cur = conn.cursor()

                raw_data = select_options_data(
                    conn, start_date_archive, end_date_archive, companies, descriptions)
                return raw_data

            OPTIONS_GRAPHS_METADATA_ARCHIVE = [
                ([11560], [f'NIKKEI 225 OOP C{i[15:17]}{i[18:20]}-'],
                 '日経225オプションゴールドマンサックスのコール手口'),
                ([11560], [f'NIKKEI 225 OOP P{i[15:17]}{i[18:20]}-'],
                 '日経225オプションゴールドマンサックスのプット手口'),
                ([12479], [
                 f'NIKKEI 225 OOP C{i[15:17]}{i[18:20]}-'], '日経225オプションABNアムロのコール手口'),
                ([12479], [
                 f'NIKKEI 225 OOP P{i[15:17]}{i[18:20]}-'], '日経225オプションABNアムロのプット手口'),
                ([11714], [
                 f'NIKKEI 225 OOP C{i[15:17]}{i[18:20]}-'], '日経225オプションJPモルガンのコール手口'),
                ([11714], [
                 f'NIKKEI 225 OOP P{i[15:17]}{i[18:20]}-'], '日経225オプションJPモルガンのプット手口'),
                ([12800], [f'NIKKEI 225 OOP C{i[15:17]}{i[18:20]}-'],
                 '日経225オプションモルガンスタンレーのコール手口'),
                ([12800], [f'NIKKEI 225 OOP P{i[15:17]}{i[18:20]}-'],
                 '日経225オプションモルガンスタンレーのプット手口'),
                ([11256, 12330, 12057, 12560, 11727], [
                    f'NIKKEI 225 OOP C{i[15:17]}{i[18:20]}-'], '日経225オプション国内ネット系証券のコール手口'),
                ([11256, 12330, 12057, 12560, 11727], [
                    f'NIKKEI 225 OOP P{i[15:17]}{i[18:20]}-'], '日経225オプション国内ネット系証券のプット手口'),
            ]

            modal_title = ""
            raw_data = None
            if chartid >= 10 and chartid <= 19:
                for idx, metadata in enumerate(OPTIONS_GRAPHS_METADATA_ARCHIVE):
                    if idx+10 == int(chartid):
                        raw_data = last(*metadata)
                        modal_title = f'{metadata[2]}       {i[13:17]} {i[18:20]}'

            sorted_data = sorted([(d, l, r)
                                for d, l, r in raw_data], key=lambda tup: tup[0])

            graph_data = {'Date': [], 'put': [], 'call': []}
            Temp_date = []
            for d, left_val, right_val in sorted_data:
                Temp_date.append(str(d))
                graph_data['put'].append(left_val)
                graph_data['call'].append(right_val)

            for i in Temp_date:
                def create(y, m, d):
                    graph_data['Date'].append(date(y, m, d).strftime("%m月%d日"))
                create(y=int(i[0:4]), m=int(i[5:7]), d=int(i[8:10]))


            charts_options[f'charts{c}'] = {
                'data': graph_data, 'modal_title': modal_title, 'date_archive': date_()}
            c += 1

    sorted_dict = dict(sorted(charts_options.items(),
                       key=operator.itemgetter(0), reverse=True))
    return Response({'charts_options': sorted_dict})


def login(request):
    if request.POST:
        key = request.POST['key']
        if key == 'njpw':
            request.session['user'] = 'user_data'
            return redirect("/")
        else:
            return redirect('login')
    return render(request, 'login.html')


def logout(request):
    del request.session['user']
    return redirect('login')

@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def home(request):
    if request.session.has_key('user'):
        main_data = {}
        main_data_last_ten = {}

        modal_title = ""
        raw_data = None
        line = None
        counter = 0
        line = price_data()
        line1 = price_data_7to10()
        for idx, metadata in enumerate(FUTURES_GRAPHS_METADATA):
            raw_data = first(*metadata)
            modal_title = metadata[2]

            graph_dates_range = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in
                         range((end_date - start_date).days)]
            graph_data = {'Dates': [], 'Diff': [], 'color': []}

            l1 = []

            for date1, left_val, right_val in raw_data:
                if date1 in graph_dates_range:
                    l1.append(date1)
                    graph_data['Diff'].append(right_val - left_val)
                    if right_val - left_val < 0:
                        graph_data['color'].append('#ff5252')
                    else:
                        graph_data['color'].append('#636efa')

            for i in l1:
                def create(y, m, d):
                    graph_data['Dates'].append(date(y, m, d).strftime("%m月%d日"))
                create(y=int(i[0:4]), m=int(i[5:7]), d=int(i[8:10]))

            main_data[f'chart{counter}'] = {'data': graph_data, 'modal_title': modal_title}
            counter+=1

        for idx, metadata in enumerate(TOPIX_FUTURES_GRAPHS_METADATA):
            raw_data = first(*metadata)
            modal_title = metadata[2]

            graph_dates_range = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in
                         range((end_date - start_date).days)]
            graph_data = {'Dates': [], 'Diff': [], 'color': []}

            l1 = []

            for date1, left_val, right_val in raw_data:
                if date1 in graph_dates_range:
                    l1.append(date1)
                    graph_data['Diff'].append(right_val - left_val)
                    if right_val - left_val < 0:
                        graph_data['color'].append('#ff5252')
                    else:
                        graph_data['color'].append('#636efa')

            for i in l1:
                def create(y, m, d):
                    graph_data['Dates'].append(date(y, m, d).strftime("%m月%d日"))
                create(y=int(i[0:4]), m=int(i[5:7]), d=int(i[8:10]))

            main_data[f'chart{counter}'] = {'data': graph_data, 'modal_title': modal_title}
            counter+=1

        for idx, metadata in enumerate(OPTIONS_GRAPHS_METADATA):
            raw_data = last(*metadata)
            modal_title = metadata[2]

            sorted_data = sorted([(d, l, r)
                                for d, l, r in raw_data], key=lambda tup: tup[0])

            graph_data = {'Date': [], 'put': [], 'call': []}
            Temp_date = []
            for d, left_val, right_val in sorted_data:
                Temp_date.append(str(d))
                graph_data['put'].append(left_val)
                graph_data['call'].append(right_val)

            for i in Temp_date:
                def create(y, m, d):
                    graph_data['Date'].append(date(y, m, d).strftime("%m月%d日"))
                create(y=int(i[0:4]), m=int(i[5:7]), d=int(i[8:10]))

            main_data_last_ten[f'chart{counter}'] = {'data': graph_data, 'modal_title': modal_title}
            counter+=1

        return Response({"data":main_data, "main_data_last_ten":main_data_last_ten, 'line': line, 'line1': line1, 'date_x': date_x},template_name="home.html")

    else:
        return redirect('login')

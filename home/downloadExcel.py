from bs4 import BeautifulSoup
import requests
from time import sleep
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime
import os
from django.conf import settings

"""
this function will download 2 excel files daily from the below link..
and then read that file store data into the database
if you want to download all files from 2021-09-21 to current date comment the line 55-63 and uncomment 65-66
-----------------------------------------------------------------------
https://www.jpx.co.jp/markets/derivatives/participant-volume/index.html
------------------------------------------------------------------------
NOTE** you can use this in case you want to get all excel files from the website.
"""

def DownloadExcel():
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    url_list = []
    url = "https://www.jpx.co.jp/markets/derivatives/participant-volume/index.html"
    agent = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    page = requests.get(url,  headers=agent)
    page = page.text
    soup = BeautifulSoup(page, "html.parser")


    current_month=int(datetime.now().date().strftime('%m'))

    dates_list = soup.find('select', {'class': 'backnumber'}).find_all('option')


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
    
    # for url in url_list_new:
    #     main_urls_list.append(url['url'])
        
    downloaded_files=[]
    
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
            split_url = url.split('/')[-1].split('_')[0]
            if os.path.exists(settings.BASE_DIR+f'/media/excels/{split_url}.xlsx'):
                print('file_already exist')
                break
            else:
                resp = session.get(url)
                output = open(settings.BASE_DIR+f'/media/excels/{split_url}.xlsx', 'wb')
                print(f"file downloaded {split_url}.xlsx")
                downloaded_files.append(f"{split_url}.xlsx")
                output.write(resp.content)
                output.close()
            
        for url in url_list_jnet:
            split_url = url.split('/')[-1].split('_')[0]
            if os.path.exists(settings.BASE_DIR+f'/media/excels/{split_url}J-NET.xlsx'):
                print('file_already exist')
                break
            else:
                resp = session.get(url)
                output = open(settings.BASE_DIR+f'/media/excels/{split_url}J-NET.xlsx', 'wb')
                print(f"file downloaded {split_url}J-NET.xlsx")
                downloaded_files.append(f"{split_url}J-NET.xlsx")
                output.write(resp.content)
                output.close()
                
    return downloaded_files
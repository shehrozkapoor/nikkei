import json
from .models import DailyData,DailyDataJnet
import pandas as pd
from django.conf import settings
from datetime import datetime, timedelta, tzinfo


"""
this function is not performing any role in the API...
this function is created just get all dates between two date
e.g
date_range(datetime(2022,9,9),datetime(2022,9,11))
this is will return [datetime.datetime(2022, 9, 9, 0, 0), datetime.datetime(2022, 9, 10, 0, 0), datetime.datetime(2022, 9, 11, 0, 0)]
"""
def date_range(start, end):
    delta = end - start  # as timedelta
    days = [start + timedelta(days=i) for i in range(delta.days + 1)]
    return days



"""
this function is not performing any role in the API...
this function is created just get read excel file from the specific date range and store all J-NET files data to DailyDataJnet model
"""
def storeJnet(file_name):
    try:
        data = pd.read_excel(settings.BASE_DIR+f'/media/excels/{file_name}', header=None, names=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'],engine='openpyxl')
        data = data.replace("－", 0)
        date = (data.iloc[[4]]["c"]).to_string(index=False)
        main_date = str(date)[:4]+"-" + str(date)[4:6]+"-"+str(date)[6:]
        main_date = datetime.strptime(main_date,'%Y-%m-%d').date()
        data = data.iloc[8:, :]
        for index, row in data.iterrows():
            brand_code=row['b']
            contract = row['c']
            company_id = row['e']
            name_jpn = row['f']
            name_eng = row['g']
            sell = row['h']
            try:
                entry = DailyDataJnet.objects.get(date=main_date, brand_code=brand_code, company_id=company_id, contract_issue=contract, name_jpn=name_jpn,name_eng=name_eng,sell=sell)
                entry.sell=sell
                entry.save()
                print(f"JNET --sell--ALREADY SAVED----{date}")
            except:
                print(f"JNET --sell---NEW SAVED----{date}")
                entry = DailyDataJnet(date=main_date, brand_code=brand_code, company_id=company_id, contract_issue=contract, name_jpn=name_jpn,name_eng=name_eng,sell=sell,buy=0)
                entry.save()
        for index, row in data.iterrows():
            brand_code=row['b']
            contract = row['c']
            company_id = row['j']
            name_jpn = row['k']
            name_eng = row['l']
            buy = row['m']
            try:
                entry = DailyDataJnet.objects.get(date=main_date, brand_code=brand_code, company_id=company_id, contract_issue=contract, name_jpn=name_jpn,name_eng=name_eng)
                entry.buy=buy
                entry.save()
                print(f"JNET --buy--ALREADY SAVED----{date}")
            except:
                print(f"JNET --buy---NEW SAVED----{date}")
                entry = DailyDataJnet(date=main_date, brand_code=brand_code, company_id=company_id, contract_issue=contract, name_jpn=name_jpn,name_eng=name_eng,sell=0,buy=buy)
                entry.save()
    except:
        print(f"except run on{date}")
    return 'stored'
    
    
    
"""
this function is not performing any role in the API...
this function is created just to read excel file from the specific date range and store all daily_data files data to DailyData model
"""    
def store(file_name):
    try:
        data = pd.read_excel(settings.BASE_DIR+f'/media/excels/{file_name}', header=None, names=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'],engine='openpyxl')
        data = data.replace("－", 0)
        date = (data.iloc[[4]]["c"]).to_string(index=False)
        main_date = str(date)[:4]+"-" + str(date)[4:6]+"-"+str(date)[6:]
        main_date = datetime.strptime(main_date,'%Y-%m-%d').date()
        data = data.iloc[8:, :]
        for index, row in data.iterrows():
            brand_code=row['b']
            contract = row['c']
            company_id = row['e']
            name_jpn = row['f']
            name_eng = row['g']
            sell = row['h']
            try:
                entry = DailyData.objects.get(date=main_date, brand_code=brand_code, company_id=company_id, contract_issue=contract, name_jpn=name_jpn,name_eng=name_eng,sell=sell)
                entry.sell=sell
                entry.save()
                print(f"DAILY_DATA --sell---ALREADY SAVED----{date}")
            except:
                print(f"DAILY_DATA --sell---NEW SAVED----{date}")
                entry = DailyData(date=main_date, brand_code=brand_code, company_id=company_id, contract_issue=contract, name_jpn=name_jpn,name_eng=name_eng,sell=sell,buy=0)
                entry.save()
        for index, row in data.iterrows():
            brand_code=row['b']
            contract = row['c']
            company_id = row['j']
            name_jpn = row['k']
            name_eng = row['l']
            buy = row['m']
            try:
                entry = DailyData.objects.get(date=main_date, brand_code=brand_code, company_id=company_id, contract_issue=contract, name_jpn=name_jpn,name_eng=name_eng)
                entry.buy=buy
                entry.save()
                print(f"DAILY_DATA --buy---ALREADY SAVED----{date}")
            except:
                print(f"DAILY_DATA --buy---NEW SAVED----{date}")
                entry = DailyData(date=main_date, brand_code=brand_code, company_id=company_id, contract_issue=contract, name_jpn=name_jpn,name_eng=name_eng,sell=0,buy=buy)
                entry.save()
    except:
        print(f"except run on{date}")
    return 'stored'


"""
this function is not performing any role in the API...
this function is created just to combine all above function as one
"""
def save_data(files):
    for file in files:
        if file.find('J-NET') == -1:
            store(file)
        else:
            storeJnet(file)
    return 'done'


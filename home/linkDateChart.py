import calendar
from datetime import timedelta
from .models import *

def second_friday(year, month):
    cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
    monthcal = cal.monthdatescalendar(year, month)
    Fridays = []
    for week in monthcal:
        for day in week:
            if day.weekday() == calendar.FRIDAY and day.month == month:
                Fridays.append(day)
    return Fridays[1]

FUTURES_GRAPHS_METADATA = [
    ([12479, 11788, 12410, 11746, 11635, 12176, 12428, 11560, 11714,12800, 12792], 'NIKKEI 225 FUT', '日経225ラージ先物外資系手口'),
    ([11635],'NIKKEI 225 FUT', '日経225ラージ先物クレディスイス手口'),
    ([11560],'NIKKEI 225 FUT', '日経225ラージ先物ゴールドマンサックス手口'),
    ([12800],'NIKKEI 225 FUT', '日経225ラージ先物モルガンスタンレー手口'),
    ([11256, 12330, 12057, 12560, 11727], 'NIKKEI 225 FUT', '日経225先物国内ネット系証券手口'),
    ([11256, 12330, 12057, 12560, 11727], 'MINI NK225 FUT', '日経225mini先物国内ネット系証券手口'),
]


TOPIX_FUTURES_GRAPHS_METADATA = [
    ([12479, 11788, 12410, 11746, 11635, 12176, 12428, 11560,
     11714, 12800, 12792], 'TOPIX FUT', 'TOPIX先物外資系手口'),
    ([11635], 'TOPIX FUT', 'TOPIX先物クレディスイス手口'),
    ([11560], 'TOPIX FUT', 'TOPIX先物ゴールドマンサックス手口'),
    ([12800], 'TOPIX FUT', 'TOPIX先物モルガンスタンレー手口'),
]

OPTIONS_GRAPHS_METADATA = [
    ([11560], 'NIKKEI 225 OOP C','日経225オプションゴールドマンサックスのコール手口'),
    ([11560], 'NIKKEI 225 OOP P','日経225オプションゴールドマンサックスのプット手口'),
    ([12479], 'NIKKEI 225 OOP C', '日経225オプションABNアムロのコール手口'),
    ([12479], 'NIKKEI 225 OOP P', '日経225オプションABNアムロのプット手口'),
    ([11714], 'NIKKEI 225 OOP C', '日経225オプションJPモルガンのコール手口'),
    ([11714], 'NIKKEI 225 OOP P', '日経225オプションJPモルガンのプット手口'),
    ([12800], 'NIKKEI 225 OOP C','日経225オプションモルガンスタンレーのコール手口'),
    ([12800], 'NIKKEI 225 OOP P','日経225オプションモルガンスタンレーのプット手口'),
    ([11256, 12330, 12057, 12560, 11727], 'NIKKEI 225 OOP C', '日経225オプション国内ネット系証券のコール手口'),
    ([11256, 12330, 12057, 12560, 11727], 'NIKKEI 225 OOP P', '日経225オプション国内ネット系証券のプット手口'),
]

"""
this function is not performing any role in the API...
this function was created just to retrieve the previous data from the previous quater from 2021-09 for graph 1-6
"""
def saveChartData1to6(input_date):
    start_date = input_date-timedelta(days=1)
    for i in range(0,6):
        
        chart_data = ChartData.objects.get(chart_id=i+1,archive=False)
        
        daily_data = DailyData.objects.filter(date__gt=start_date,date__lt=chart_data.end_date,company_id__in=FUTURES_GRAPHS_METADATA[i][0],contract_issue__startswith=FUTURES_GRAPHS_METADATA[i][1]).order_by('date')
        
        daily_data_jnet = DailyDataJnet.objects.filter(date__gt=start_date,date__lt=chart_data.end_date,company_id__in=FUTURES_GRAPHS_METADATA[i][0],contract_issue__startswith=FUTURES_GRAPHS_METADATA[i][1]).order_by('date')

        
        for data in daily_data:
            print(f"DAILY DATA saved on {data.date}")
            chart_data.daily_data.add(data)
        
        for data in daily_data_jnet:
            print(f"JNET saved on {data.date}")
            chart_data.daily_data_jnet.add(data)
            
    return 'done'

"""
this function is not performing any role in the API...
this function was created just to retrieve the previous data from the previous quater from 2021-09 for graph 7-10
"""
def saveChartData7to10(input_date):
    start_date = input_date-timedelta(days=1)

    for i in range(0,4):
        
        chart_data = ChartData.objects.get(chart_id=i+7,archive=False)
        
        daily_data = DailyData.objects.filter(date__gt=start_date,date__lt=chart_data.end_date,company_id__in=TOPIX_FUTURES_GRAPHS_METADATA[i][0],contract_issue__startswith=TOPIX_FUTURES_GRAPHS_METADATA[i][1]).order_by('date')
        
        daily_data_jnet = DailyDataJnet.objects.filter(date__gt=start_date,date__lt=chart_data.end_date,company_id__in=TOPIX_FUTURES_GRAPHS_METADATA[i][0],contract_issue__startswith=TOPIX_FUTURES_GRAPHS_METADATA[i][1]).order_by('date')
        
        
        
        for data in daily_data:
            print(f"DAILY DATA saved on {data.date}")
            chart_data.daily_data.add(data)
        
        for data in daily_data_jnet:
            print(f"JNET saved on {data.date}")
            chart_data.daily_data_jnet.add(data)
    return 'done'


"""
this function is not performing any role in the API...
this function was created just to retrieve the previous data from the previous quater from 2021-09 for graph 11-20
"""
def saveChartData11to20(input_date):
    start_date = input_date-timedelta(days=1)
    for i in range(0,10):
        
        chart_data = ChartData.objects.get(chart_id=i+11,archive=False)
        
        daily_data = DailyData.objects.filter(date__gt=start_date,date__lt=chart_data.end_date,company_id__in=OPTIONS_GRAPHS_METADATA[i][0],contract_issue__startswith=OPTIONS_GRAPHS_METADATA[i][1]).order_by('date')
        
        daily_data_jnet = DailyDataJnet.objects.filter(date__gt=start_date,date__lt=chart_data.end_date,company_id__in=OPTIONS_GRAPHS_METADATA[i][0],contract_issue__startswith=OPTIONS_GRAPHS_METADATA[i][1]).order_by('date')
        
        
        
        
        for data in daily_data:
            print(f"DAILY DATA saved on {data.date}")
            chart_data.daily_data.add(data)
        
        for data in daily_data_jnet:
            print(f"DAILY DATA saved on {data.date}")
            chart_data.daily_data_jnet.add(data)
    return 'done'


        
"""
this function is not performing any role in the API...
this function was created just to combine all above function.
"""
def save_chart_data_daily(input_date):
    saveChartData1to6(input_date)
    saveChartData7to10(input_date)
    saveChartData11to20(input_date)    
    return 'done'
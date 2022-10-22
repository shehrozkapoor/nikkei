from celery import shared_task
from celery.utils.log import get_task_logger
from .downloadExcel import DownloadExcel
from .saveData import save_data
from .linkDateChart import save_chart_data_daily
from datetime import datetime, timedelta
from .line_data import line_data,line_data_7to10
from .models import *
from .linkDateChart import second_friday

logger = get_task_logger(__name__)

@shared_task(bind=True)
def dailyDataUpdate(self):
    input_date = datetime.now().date()
    files = DownloadExcel()
    print(f'these are the files {files}')
    if len(files)!=0:
        response = save_data(files)
        resp = save_chart_data_daily(input_date)
    logger.info('Data updated today')

@shared_task(bind=True)
def dailyLineDataUpdate(self):
    input_date = datetime.now().date()
    line_data(end_date=input_date)
    line_data_7to10(end_date=input_date)
    logger.info('Line Data updated today')

@shared_task(bind=True)
def updateChart11to20Every2ndFriday(self):
    current_date = datetime.now()
    current_month = current_date.month
    next_month = current_month+1
    year = current_date.year
    if current_month == 12:
        year+=1
        next_month=1
    next_month_friday = second_friday(year,next_month)
    next_month_friday-=timedelta(days=1)
    
    get_charts_11_to_20 = ChartData.objects.filter(chart_id__gt=10,chart_id__lte=20,archive=False).order_by('id')
    
    for chart in get_charts_11_to_20:
        chart.archive=True
        chart.save()
        ChartData.objects.create(chart_id=chart.chart_id,start_date=current_date.date(),end_date=next_month_friday,archive=False)
    
    logger.info('every second friday charts updated Successfully')

@shared_task(bind=True)
def updateChart1to10EveryQuater2ndFriday(self):
    current_date = datetime.now()
    current_month = current_date.month
    next_month = current_month+3
    year = current_date.year
    if current_month == 12:
        year+=1
        next_month=3
    next_month_friday = second_friday(year,next_month)
    next_month_friday-=timedelta(days=1)
    
    get_charts_1_to_10 = ChartData.objects.filter(chart_id__gte=1,chart_id__lte=10,archive=False).order_by('id')
    
    for chart in get_charts_1_to_10:
        chart.archive=True
        chart.save()
        ChartData.objects.create(chart_id=chart.chart_id,start_date=current_date.date(),end_date=next_month_friday,archive=False)
    
    logger.info('every second friday charts updated Successfully')
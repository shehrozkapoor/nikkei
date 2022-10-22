from time import time
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render,redirect
from .models import *
from django.db.models import Sum
from rest_framework import status
from .linkDateChart import FUTURES_GRAPHS_METADATA,TOPIX_FUTURES_GRAPHS_METADATA,OPTIONS_GRAPHS_METADATA
from datetime import datetime, timedelta

def get_non_match_dates_daily_date(daily_date, daily_jnet_date): return list((set(daily_date) - set(daily_jnet_date)))
def get_non_match_dates_daily_date_jnet(daily_date, daily_jnet_date): return list((set(daily_jnet_date) - set(daily_date)))
def get_non_match_dates_from_final_result(line_dates,diff_dates): return list((set(line_dates) - set(diff_dates)))

def addMissingDateSum(dates,diff):
    new_diff=[]
    for date in diff:
        new_diff.append(date['x'])
    result = get_non_match_dates_from_final_result(dates,new_diff)
    
    for date in result:
        diff.append({'x':date,'y':'N/A'})
    diff.sort(key = lambda x:x['x'])
    return diff

def sortDailyData(daily_data,daily_data_jnet):
    daily_data.sort(key = lambda x:x['date'])
    daily_data_jnet.sort(key = lambda x:x['date'])
    


def getTitle(chart_id=None,chart_pk=None):
    if chart_pk != None:
        chart = ChartData.objects.get(pk=chart_pk)
        chart_id=chart.chart_id
    else:
        chart_id=int(chart_id)
    if chart_id <=6:
        return FUTURES_GRAPHS_METADATA[chart_id-1][2]
    elif chart_id >6 and chart_id<=10:
        return TOPIX_FUTURES_GRAPHS_METADATA[chart_id-7][2]
    else:
        return OPTIONS_GRAPHS_METADATA[chart_id-11][2]
    

def getLineChart(chart_id):
    chart_id=int(chart_id)
    chart = ChartData.objects.get(chart_id=chart_id,archive=False)
    start_date = chart.start_date
    end_date = chart.end_date
    if chart_id < 7 or chart_id >10:
        line = LineData.objects.filter(date__gte=start_date,date__lte=end_date,is_topix=False).order_by('date')
    else:
        line = LineData.objects.filter(date__gte=start_date,date__lte=end_date,is_topix=True).order_by('date')
    
    dates = [i.date.strftime("%m月%d日") for i in line]
    return dates,[i.line_num for i in line]

def getArchiveLineChart(chart_pk):
    chart = ChartData.objects.get(pk=chart_pk)
    start_date = chart.start_date
    end_date = chart.end_date
    if chart.chart_id < 7 or chart.chart_id >10:
        line = LineData.objects.filter(date__gte=start_date,date__lte=end_date,is_topix=False).order_by('date')
    else:
        line = LineData.objects.filter(date__gte=start_date,date__lte=end_date,is_topix=True).order_by('date')
    dates = [i.date.strftime("%m月%d日") for i in line]
    lines = [i.line_num for i in line]
    return lines,dates

def getChartStartEndDate(chart_pk):
    chart = ChartData.objects.get(pk=chart_pk)
    start_date = chart.start_date.strftime('%Y-%m')
    end_date = chart.end_date.strftime('%Y-%m')
    return f"{start_date} - {end_date}"

def getCookie(request):
    try:
        login_cookie = request.COOKIES['login'] 
    except:
        return False
    if login_cookie != "True":
        return False
    return True

def home(request):
    resp = getCookie(request)
    if resp == False:
        return redirect('login')
    return render(request,'home.html')

def archive(request):
    resp = getCookie(request)
    if resp == False:
        return redirect('login')
    return render(request,'archive.html')

def company_profile(request):
    resp = getCookie(request)
    if resp == False:
        return redirect('login')
    return render(request,'company_profile.html')

def risk_description(request):
    resp = getCookie(request)
    if resp == False:
        return redirect('login')
    return render(request,'risk.html')

def disclaimer(request):
    resp = getCookie(request)
    if resp == False:
        return redirect('login')
    return render(request,'disclaimer.html')

def login(request):
    if request.method == 'POST':
        password = request.POST.get('password',None)
        if password is None:
            return render(request,'login.html',{'message':'invalid Password'})
        else:
            try:
                LoginPass.objects.get(password=password)
            except:
                return render(request,'login.html',{'message':'invalid Password'}) 
            resp =  render(request,'home.html')
            resp.set_cookie('login',True)
            return resp
    return render(request,'login.html')

    

def logout(request):
    response = redirect('login')
    response.delete_cookie('login')
    return response


def calculateSum(daily_data,daily_data_jnet):
    sortDailyData(daily_data,daily_data_jnet)    
    diff=[]
    colors=[]
    for idx in range(0,len(daily_data)):
        sum = daily_data[idx]['sum']+daily_data_jnet[idx]['sum']
        date = daily_data[idx]['date']
        diff.append({'x':datetime.strptime(date,'%Y-%m-%d').strftime('%m月%d日'),'y':sum})
        colors.append('#ff8a8a' if sum<0 else '#636efa')
    return diff,colors
        


def CalculateData(chart_id=None,chart_pk=None):
    
    if chart_id != None:
        chart_data = ChartData.objects.get(chart_id=chart_id,archive=False)
    else:
        chart_data = ChartData.objects.get(pk=chart_pk)
    
    daily_data = chart_data.daily_data.all().values('date').order_by('date').annotate(sell_sum=Sum('sell'),buy_sum=Sum('buy'))
    daily_jnet_data = chart_data.daily_data_jnet.all().values('date').order_by('date').annotate(sell_sum=Sum('sell'),buy_sum=Sum('buy'))
    
    
    result_daily_date = []
    result_daily_date_jnet = []
    
    result_daily_data = []
    result_daily_data_jnet = []
    
    for data in daily_data:
        result_daily_date.append(data['date'].strftime('%Y-%m-%d'))
        result_daily_data.append({'date':data['date'].strftime('%Y-%m-%d'),'sum':data['buy_sum']-data['sell_sum']})
    
    for data in daily_jnet_data:
        result_daily_date_jnet.append(data['date'].strftime('%Y-%m-%d'))
        result_daily_data_jnet.append({'date':data['date'].strftime('%Y-%m-%d'),'sum':data['buy_sum']-data['sell_sum']})
    
    
    non_match_daily_date = get_non_match_dates_daily_date(result_daily_date,result_daily_date_jnet)
    non_match_daily_date_jnet = get_non_match_dates_daily_date_jnet(result_daily_date,result_daily_date_jnet)
    
    
    if len(non_match_daily_date) == 0 and len(non_match_daily_date_jnet) == 0:
        diff,colors = calculateSum(result_daily_data,result_daily_data_jnet)
        return diff,colors
    
    if len(non_match_daily_date) != 0:
        for data in non_match_daily_date:
            result_daily_data_jnet.append({'date':data,'sum':0})
    if len(non_match_daily_date_jnet) != 0:
        for data in non_match_daily_date_jnet:
            result_daily_data.append({'date':data,'sum':0})

    diff,colors = calculateSum(result_daily_data,result_daily_data_jnet)
    
    return diff,colors

@api_view(["GET"])
def getChartDataHome(request):
    chart_id = request.GET.get('chart_id',None)
    if chart_id is None:
        data={
        'status':'error',
        'message':'chart_id is required!!',
        }
        return Response(data=data,status=status.HTTP_404_NOT_FOUND)
    diff,colors = CalculateData(chart_id=chart_id)    
    dates,lines= getLineChart(chart_id)
    
    diff = addMissingDateSum(dates,diff)
    data={
        'status':'ok',
        'message':'Successfull',
        'data':{
            'dates':dates,
            'diff':diff,
            'colors':colors,
            'title':getTitle(chart_id=chart_id),
            'line':lines
        }
    }
    return Response(data=data,status=status.HTTP_200_OK)



@api_view(["GET"])
def getChartArchiveCount(request):
    chart_id = request.GET.get('chart_id',None)
    if chart_id is None:
        data={
        'status':'error',
        'message':'chart_id is required!!',
        }
        return Response(data=data,status=status.HTTP_404_NOT_FOUND)
    
    charts = ChartData.objects.filter(chart_id=chart_id,archive=True).order_by('start_date').reverse()
    
    charts_pk = [chart.id for chart in charts]
    
    data={
        'status':'ok',
        'message':'Successfull',
        'data':{
            'total_charts':charts.count(),
            'charts_id':charts_pk
        }
    }
    return Response(data=data,status=status.HTTP_200_OK)
    
    
@api_view(["GET"])
def getChartDataArchive(request):
    chart_pk = request.GET.get('chart_pk',None)
    if chart_pk is None:
        data={
        'status':'error',
        'message':'chart_pk is required!!',
        }
        return Response(data=data,status=status.HTTP_404_NOT_FOUND)
    diff,colors = CalculateData(chart_pk=chart_pk)
    lines,dates= getArchiveLineChart(chart_pk)
    
    diff = addMissingDateSum(dates,diff)
    data={
        'status':'ok',
        'message':'Successfull',
        'data':{
            'dates':dates,
            'diff':diff,
            'colors':colors,
            'title':getTitle(chart_pk=chart_pk),
            'line':lines,
            'graph_between':getChartStartEndDate(chart_pk)
        }
    }
    return Response(data=data,status=status.HTTP_200_OK)


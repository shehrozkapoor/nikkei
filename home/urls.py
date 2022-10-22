from django.urls import path
from .views import *

urlpatterns=[
    path('',home,name="index"),
    path('company-profile/',company_profile,name='company_profile'),
    path('risk-description/',risk_description,name='risk_description'),
    path('disclaimer/',disclaimer,name='disclaimer'),
    path('archive/',archive,name='archive'),
    path('login/',login,name='login'),
    path('logout/',logout,name='logout'),
    # API
    path('chart-data-home/',getChartDataHome,name="getChartDataHome"),
    path('get-archive-count/',getChartArchiveCount,name="getChartArchiveCount"),
    path('get-chart-data-archive/',getChartDataArchive,name="getChartDataArchive"),
]
"""charts_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from home import views as mv
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index',mv.index,name="index"),
    path('Charts2',mv.Charts2,name="Charts2"),
    path('Charts3',mv.Charts3,name="Charts3"),
    path('Charts4',mv.Charts4,name="Charts4"),
    path('Charts5',mv.Charts5,name="Charts5"),
    path('Charts6',mv.Charts6,name="Charts6"),
    path('getChart2Data',mv.getChart2Data.as_view(),name="getChart2Data"),
    path('getChart2DataJnet',mv.getChart2DataJnet.as_view(),name="getChart2DataJnet"),
    path('getChart3Data',mv.getChart3Data.as_view(),name="getChart3Data"),
    path('getChart3DataJnet',mv.getChart3DataJnet.as_view(),name="getChart3DataJnet"),
     path('getChart4Data',mv.getChart4Data.as_view(),name="getChart4Data"),
    path('getChart4DataJnet',mv.getChart4DataJnet.as_view(),name="getChart4DataJnet"),
    path('getChart1Data',mv.getChart1Data.as_view(),name="getChart1Data"),
    path('getChart1DataJnet',mv.getChart1DataJnet.as_view(),name="getChart1DataJnet"),
    path('getChart5Data',mv.getChart5Data.as_view(),name="getChart5Data"),
    path('getChart5DataJnet',mv.getChart5DataJnet.as_view(),name="getChart5DataJnet"),
    path('getChart6Data',mv.getChart6Data.as_view(),name="getChart6Data"),
    path('getChart6DataJnet',mv.getChart6DataJnet.as_view(),name="getChart6DataJnet"),
    path('getChart7Data',mv.getChart7Data.as_view(),name="getChart7Data"),
    path('getChart7DataJnet',mv.getChart7DataJnet.as_view(),name="getChart7DataJnet"),
    path('getChart8Data',mv.getChart8Data.as_view(),name="getChart8Data"),
    path('getChart8DataJnet',mv.getChart8DataJnet.as_view(),name="getChart8DataJnet"),
    path('getChart9Data',mv.getChart9Data.as_view(),name="getChart9Data"),
    path('getChart9DataJnet',mv.getChart9DataJnet.as_view(),name="getChart9DataJnet"),
     path('getChart10Data',mv.getChart10Data.as_view(),name="getChart10Data"),
    path('getChart10DataJnet',mv.getChart10DataJnet.as_view(),name="getChart10DataJnet"),
    path('getChart11Data',mv.getChart11Data.as_view(),name="getChart11Data"),
    path('getChart11DataJnet',mv.getChart11DataJnet.as_view(),name="getChart11DataJnet"),
    path('getChart12Data',mv.getChart12Data.as_view(),name="getChart12Data"),
    path('getChart12DataJnet',mv.getChart12DataJnet.as_view(),name="getChart12DataJnet"),
    path('getChart13Data',mv.getChart13Data.as_view(),name="getChart13Data"),
    path('getChart13DataJnet',mv.getChart13DataJnet.as_view(),name="getChart13DataJnet"),
    path('getChart14Data',mv.getChart14Data.as_view(),name="getChart14Data"),
    path('getChart14DataJnet',mv.getChart14DataJnet.as_view(),name="getChart14DataJnet"),
    path('getChart15Data',mv.getChart15Data.as_view(),name="getChart15Data"),
    path('getChart15DataJnet',mv.getChart15DataJnet.as_view(),name="getChart15DataJnet"),
    path('getChart16Data',mv.getChart16Data.as_view(),name="getChart16Data"),
    path('getChart16DataJnet',mv.getChart16DataJnet.as_view(),name="getChart16DataJnet"),
    path('getChart17Data',mv.getChart17Data.as_view(),name="getChart17Data"),
    path('getChart17DataJnet',mv.getChart17DataJnet.as_view(),name="getChart17DataJnet"),
    path('getChart18Data',mv.getChart18Data.as_view(),name="getChart18Data"),
    path('getChart18DataJnet',mv.getChart18DataJnet.as_view(),name="getChart18DataJnet"),
    path('getChart19Data',mv.getChart19Data.as_view(),name="getChart19Data"),
    path('getChart19DataJnet',mv.getChart19DataJnet.as_view(),name="getChart19DataJnet"),
    path('getChart20Data',mv.getChart20Data.as_view(),name="getChart20Data"),
    path('getChart20DataJnet',mv.getChart20DataJnet.as_view(),name="getChart20DataJnet"),
    path('get_futures_figure/<int:graphid>/',mv.get_futures_figure,name="get_futures_figure"),
    path('get_options_figure/<int:graphid>/',mv.get_options_figure,name="get_options_figure"),
    path('company-profile/',mv.company_profile,name='company_profile'),
    path('risk-description/',mv.risk_description,name='risk_description'),
    path('disclaimer/',mv.disclaimer,name='disclaimer'),
    path('archive/',mv.archive,name='archive'),
    path('',mv.home,name='home'),
    path('login/',mv.login,name='login'),
    path('logout/',mv.logout,name='logout'),
    path('eachchart/<int:chartid>/',mv.eachchart,name='eachchart'),
    path('eachchart_options/<int:chartid>/',mv.eachchart_options,name='eachchart_options'),
]
if(settings.DEBUG==True):
    urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
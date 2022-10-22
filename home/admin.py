from django.contrib import admin
from .models import ChartData, DailyData, DailyDataJnet,LoginPass

admin.site.register(DailyData)
admin.site.register(DailyDataJnet)
admin.site.register(ChartData)
admin.site.register(LoginPass)
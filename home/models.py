from django.db import models


# model to store DailyData
class DailyData(models.Model):
    date = models.DateField()
    brand_code = models.TextField()
    company_id = models.TextField()
    contract_issue = models.TextField()
    name_jpn = models.TextField()
    name_eng = models.TextField()
    sell = models.FloatField()
    buy = models.FloatField()

# model to store DailyDataJnet
class DailyDataJnet(models.Model):
    date = models.DateField()
    brand_code = models.TextField()
    company_id = models.TextField()
    contract_issue = models.TextField()
    name_jpn = models.TextField()
    name_eng = models.TextField()
    sell = models.FloatField()
    buy = models.FloatField()
    

# model to store ChartData from 1-20
class ChartData(models.Model):
    chart_id = models.IntegerField(null=True,blank=True)
    daily_data = models.ManyToManyField(DailyData,related_name="daily_data")
    daily_data_jnet = models.ManyToManyField(DailyDataJnet,related_name="daily_data_jnet")
    start_date = models.DateField(null=True,blank=True)
    end_date = models.DateField(null=True,blank=True)
    archive = models.BooleanField(default=False)
    

class LoginPass(models.Model):
    password = models.CharField(max_length=100,null=True,blank=True,default='njpw')
    


class LineData(models.Model):
    line_num = models.FloatField(null=True,blank=True)
    date = models.DateField(null=True,blank=True)
    is_topix = models.BooleanField(default=False)




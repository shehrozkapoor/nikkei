from django.test import TestCase
from ..models import *
from datetime import datetime


class DailyDataTestCase(TestCase):
    def setUp(self):
        DailyData.objects.create(date=datetime.now().date(),brand_code="23132321",company_id="2133232",contract_issue="NIKKIE TEST 1",name_jpn="test 1",name_eng="test 1",sell=120.0,buy=198.0)
        DailyData.objects.create(date=datetime.now().date(),brand_code="234332",company_id="21322332",contract_issue="NIKKIE TEST 2",name_jpn="test 2",name_eng="test 2",sell=99.0,buy=100.0)
        
    def test_DailyData(self):
        daily_data_1 = DailyData.objects.get(brand_code="23132321",company_id="2133232")
        daily_data_2 = DailyData.objects.get(brand_code="234332",company_id="21322332")
        
        self.assertEquals(daily_data_1.date,datetime.now().date())
        self.assertEquals(daily_data_2.date,datetime.now().date())
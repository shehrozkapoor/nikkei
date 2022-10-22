from django.test import SimpleTestCase
from django.urls import reverse,resolve
from ..views import *

class TestUrls(SimpleTestCase):
    
    def test_index_url_is_resolved(self):
        url = reverse('index')
        self.assertEquals(resolve(url).func,home)
    
    def test_company_profile_url_is_resolved(self):
        url = reverse('company_profile')
        self.assertEquals(resolve(url).func,company_profile)
    
    def test_risk_description_is_resolved(self):
        url = reverse('risk_description')
        self.assertEquals(resolve(url).func,risk_description)
    
    def test_disclaimer_is_resolved(self):
        url = reverse('disclaimer')
        self.assertEquals(resolve(url).func,disclaimer)
    
    def test_archive_is_resolved(self):
        url = reverse('archive')
        self.assertEquals(resolve(url).func,archive)
    
    def test_login_is_resolved(self):
        url = reverse('login')
        self.assertEquals(resolve(url).func,login)
    
    def test_logout_is_resolved(self):
        url = reverse('logout')
        self.assertEquals(resolve(url).func,logout)
    
    def test_logout_is_resolved(self):
        url = reverse('logout')
        self.assertEquals(resolve(url).func,logout)
    
    def test_getChartDataHome_is_resolved(self):
        url = reverse('getChartDataHome')
        self.assertEquals(resolve(url).func,getChartDataHome)
    
    def test_getChartArchiveCount_is_resolved(self):
        url = reverse('getChartArchiveCount')
        self.assertEquals(resolve(url).func,getChartArchiveCount)
    
    def test_getChartDataArchive_is_resolved(self):
        url = reverse('getChartDataArchive')
        self.assertEquals(resolve(url).func,getChartDataArchive)
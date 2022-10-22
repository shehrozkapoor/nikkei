from django.test import TestCase,Client
from home.models import *
from home.views import *
from django.urls import reverse,resolve


class TestViews(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.index_url = reverse('index')
    
    def test_index(self):
        response = self.client.get(self.index_url)
        
        self.assertEquals(response.status_code,302)
        self.assertTemplateUsed(response,'login.html')
        
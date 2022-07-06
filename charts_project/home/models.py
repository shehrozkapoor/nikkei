from django.db import models

# Create your models here.
class daily_data(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.TextField()
    jpx_code = models.TextField()
    company_id = models.TextField()
    description = models.TextField()
    name_jpn = models.TextField()
    name_eng = models.TextField()
    left_val = models.TextField()
    company_id_right = models.TextField(null=True, blank=True)
    right_val = models.TextField()
    label = models.TextField()

# Generated by Django 3.2.7 on 2021-11-18 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_daily_data_company_id_right'),
    ]

    operations = [
        migrations.AddField(
            model_name='daily_data',
            name='description_right',
            field=models.TextField(blank=True, null=True),
        ),
    ]
# Generated by Django 4.0.6 on 2022-08-13 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0012_alter_dailydata_date_alter_dailydatajnet_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailydata',
            name='date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='dailydatajnet',
            name='date',
            field=models.DateField(),
        ),
    ]
# Generated by Django 4.0.6 on 2022-08-13 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0010_alter_dailydata_buy_alter_dailydata_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailydata',
            name='buy',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='dailydata',
            name='sell',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='dailydatajnet',
            name='buy',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='dailydatajnet',
            name='sell',
            field=models.FloatField(),
        ),
    ]
# Generated by Django 4.0.6 on 2022-08-15 01:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0013_alter_dailydata_date_alter_dailydatajnet_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoginPass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(blank=True, default='njpw', max_length=100, null=True)),
            ],
        ),
    ]
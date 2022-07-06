# Generated by Django 3.2.7 on 2021-10-20 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_rename_data_daily'),
    ]

    operations = [
        migrations.CreateModel(
            name='daily_data',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.TextField()),
                ('jpx_code', models.TextField()),
                ('company_id', models.TextField()),
                ('description', models.TextField()),
                ('name_jpn', models.TextField()),
                ('name_eng', models.TextField()),
                ('left_val', models.TextField()),
                ('right_val', models.TextField()),
                ('label', models.TextField()),
            ],
        ),
        migrations.DeleteModel(
            name='daily',
        ),
    ]

# Generated by Django 2.1 on 2019-02-06 06:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0003_verifycode'),
    ]

    operations = [
        migrations.AddField(
            model_name='verifycode',
            name='expire_time',
            field=models.DateTimeField(default=datetime.datetime(2019, 2, 6, 7, 5, 27, 26474)),
        ),
    ]

# Generated by Django 2.1 on 2019-02-07 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0010_auto_20190207_1347'),
    ]

    operations = [
        migrations.AddField(
            model_name='websocketchannel',
            name='group_name',
            field=models.CharField(default='channel_group_order', max_length=20),
        ),
    ]
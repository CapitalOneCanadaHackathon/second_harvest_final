# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-24 00:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buyer',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='buyer',
            name='postal_code',
            field=models.CharField(max_length=7),
        ),
    ]

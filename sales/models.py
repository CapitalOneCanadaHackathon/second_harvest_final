from django.db import models
from django.contrib.auth.models import User
from .constants import *

# Create your models here.
class Campaign(models.Model):
    camp_id = models.CharField(max_length=3)
    start_date = models.DateField()
    end_date = models.DateField()
    fund_goal = models.DecimalField(max_digits=12, decimal_places=2)
    camp_name = models.CharField(max_length=255)
    tick_price1 = models.DecimalField(max_digits=6, decimal_places=2)
    tick_price3 = models.DecimalField(max_digits=6, decimal_places=2)
    tick_price10 = models.DecimalField(max_digits=6, decimal_places=2)


class Seller(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    phone = models.CharField(max_length=20)


class Buyer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    opt_out = models.BooleanField(default=False)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=50)
    province = models.CharField(max_length=2, choices=PROVINCES, default="ON")
    postal_code = models.CharField(max_length=7)


class Tickets(models.Model):
    tick_id = models.CharField(max_length=8)
    camp_id = models.ForeignKey('Campaign', on_delete=models.CASCADE)
    buyer_id = models.ForeignKey('Buyer')
    seller_id = models.ForeignKey(User)
    sale_date = models.DateField(blank=True)
    tick_type = models.SmallIntegerField(blank=True)

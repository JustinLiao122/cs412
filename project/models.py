

# Create your models here.
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
#[[-1,Meats,-1,-1,-1,dairy, -1],
# [-1,-1,pasta,asian,chips,-1, household],
# [-1,-1,-1,-1,candy,-1,-1],
# [-1,fruits, -1,-1,-1,-1,-1],
# [Main,-1,selfcheckout, -1,-1,-1,back]]


class Customer(models.Model):


    firstname = models.TextField(blank=True)
    lastname = models.TextField(blank= True)
    address = models.TextField(blank=True)
    email = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


    def __str__(self):

        return f'{self.firstname} {self.lastname}'
    

class Item(models.Model):

    name = models.TextField(blank=True)
    price = models.FloatField(blank=True)
    aisle = models.TextField(blank=True)
    store = models.ForeignKey("Store", on_delete=models.CASCADE)
    stock = models.IntegerField(blank=True)


    def __str__ (self):

        return f'{self.name} {self.price} {self.aisle} {self.store.name} {self.stock}'


class Store(models.Model):

    name = models.TextField(blank=True)
    address = models.TextField(blank=True)
    zipcode = models.TextField(blank=True)
    layout = models.JSONField(blank=True)


    def __str__(self):

        return f'{self.name} {self.address} {self.zipcode} {self.layout}'
    

class Cart(models.Model):

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):

        return f'{self.customer} {self.is_active}'

class CartItem(models.Model):

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):

        return f'{self.cart} {self.item} {self.quantity}'
    

class PastOrder(models.Model):

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    total_price = models.FloatField(blank=True)
    items = models.TextField(blank=True)


    def __str__(self):

        return f'{self.customer} {self.timestamp} {self.total_price} {self.items}'

class PastOrderItem(models.Model):

    past_order = models.ForeignKey(PastOrder, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=True)


    def __str__(self):

        return f'{self.past_order} {self.item} {self.quantity}'
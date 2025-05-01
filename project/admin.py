# File: project/admin.py
# Author: Justin Liao (liaoju@bu.edu), 4/16/2025
# Description: registers models with in the django admin framework where I can modify them


from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Customer)
admin.site.register(Item)
admin.site.register(Store)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(PastOrder)

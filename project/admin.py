from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Customer)
admin.site.register(Item)
admin.site.register(Store)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(PastOrder)


# File: mini_fb/admin.py
# Author: Justin Liao (liaoju@bu.edu), 3/4/2025
# Description: registers models with in the django admin framework where I can modify them

from django.contrib import admin

# Register your models here.
from .models import Profile , StatusMessage, Image, StatusImage , Friend
admin.site.register(Profile)
admin.site.register(StatusMessage)
admin.site.register(Image)
admin.site.register(StatusImage)
admin.site.register(Friend)
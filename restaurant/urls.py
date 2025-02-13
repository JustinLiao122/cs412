## restaurant/urls.py
## url patterns for the restaurant app

from django.urls import path
from django.conf import settings
from . import views


#url patterns for this app
urlpatterns = [ 
    path(r'',views.home_page, name= "home_page"),
    path(r'main',views.main, name= "main"),
    path(r'order',views.order, name= "order"),
    path(r'confirmation ',views.confirmation , name= "confirmation"),
]
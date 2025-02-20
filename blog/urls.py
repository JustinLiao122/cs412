## blog/urls.py
## url patterns for the restaurant app

from django.urls import path
from django.conf import settings
from .views import ShowAllView


#url patterns for this app
urlpatterns = [ 
     path('',ShowAllView.as_view(), name= "show_all"),
]
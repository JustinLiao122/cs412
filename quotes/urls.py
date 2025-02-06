from django.urls import path
from django.conf import settings
from . import views

urlpatterns = [ 
path(r'',views.home_page, name= "home_page"),
path(r'quote',views.quote, name= "quote"),
path(r'show',views.show, name= "show"),
path(r'about',views.aboutquotes, name= "aboutquotes"),
]
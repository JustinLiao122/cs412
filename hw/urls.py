from django.urls import path 
from django.conf import settings 
from . import views 

urlpatterns = [
    #path(r'', views.home, name="home"),
    path(r'',views.home_page, name= "home_page"),
    path(r'about', views.about, name= "about_page" )
]
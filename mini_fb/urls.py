## mini_fb/urls.py
## url patterns for the restaurant app

from django.urls import path
from django.conf import settings
from .views import ShowAllProfilesView
from .views import ShowProfilePageView
from .views import CreateProfileView ,CreateStatusMessageView



#url patterns for this app
urlpatterns = [ 
     path('',ShowAllProfilesView.as_view(), name= "show_all_profiles"),
     path('profile/<int:pk>', ShowProfilePageView.as_view() , name="show_profile"),
     path('create_profile', CreateProfileView.as_view(), name='create_profile'),
     path('profile/<int:pk>/create_status', CreateStatusMessageView.as_view(), name='create_status')

]    
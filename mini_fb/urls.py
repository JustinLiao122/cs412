# File: mini_fb/urls.py
# Author: Justin Liao (liaoju@bu.edu), 3/4/2025
# Description: url patterns for the restaurant app


from django.urls import path
from django.conf import settings
from .views import ShowAllProfilesView
from .views import ShowProfilePageView
from .views import CreateProfileView ,CreateStatusMessageView,UpdateProfileView, DeleteStatusMessageView , UpdateStatusMessageView, AddFriendView, ShowFriendSuggestionsView



#url patterns for this app
urlpatterns = [ 
     path('',ShowAllProfilesView.as_view(), name= "show_all_profiles"),
     path('profile/<int:pk>', ShowProfilePageView.as_view() , name="show_profile"),
     path('create_profile', CreateProfileView.as_view(), name='create_profile'),
     path('profile/<int:pk>/create_status', CreateStatusMessageView.as_view(), name='create_status'),
     path('profile/<int:pk>/update', UpdateProfileView.as_view(), name='update_profile'),
     path('status/<int:pk>/delete', DeleteStatusMessageView.as_view(), name='delete_status'),
     path('status/<int:pk>/update', UpdateStatusMessageView.as_view(), name='update_status'),
     path('profile/<int:pk>/add_friend/<int:other_pk>/', AddFriendView.as_view(), name='add_friend'),
     path('profile/<int:pk>/friend_suggestions', ShowFriendSuggestionsView.as_view(), name='friend_suggestions'),




]    
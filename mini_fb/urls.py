# File: mini_fb/urls.py
# Author: Justin Liao (liaoju@bu.edu), 3/4/2025
# Description: url patterns for the restaurant app


from django.urls import path
from django.conf import settings
from .views import ShowAllProfilesView
from .views import ShowProfilePageView
from .views import CreateProfileView ,CreateStatusMessageView,UpdateProfileView, DeleteStatusMessageView , UpdateStatusMessageView, AddFriendView, ShowFriendSuggestionsView, ShowNewsFeedView
from django.contrib.auth import views as auth_views


#url patterns for this app
urlpatterns = [ 
     path('',ShowAllProfilesView.as_view(), name= "show_all_profiles"),
     path('profile/<int:pk>', ShowProfilePageView.as_view() , name="show_profile"),
     path('create_profile', CreateProfileView.as_view(), name='create_profile'),
     path('profile/create_status', CreateStatusMessageView.as_view(), name='create_status'),
     path('profile/update', UpdateProfileView.as_view(), name='update_profile'),
     path('status/<int:pk>/delete', DeleteStatusMessageView.as_view(), name='delete_status'),
     path('status/<int:pk>/update', UpdateStatusMessageView.as_view(), name='update_status'),
     path('profile/add_friend/<int:other_pk>/', AddFriendView.as_view(), name='add_friend'),
     path('profile/friend_suggestions', ShowFriendSuggestionsView.as_view(), name='friend_suggestions'),
     path('profile/news_feed', ShowNewsFeedView.as_view(), name='news_feed'),
     path('login/', auth_views.LoginView.as_view(template_name='mini_fb/login.html'), name='login'), ## NEW
	path('logout/', auth_views.LogoutView.as_view(template_name='mini_fb/logged_out.html'), name='logout'), ## NEW




]    
# File: voter_analytics/urls.py
# Author: Justin Liao (liaoju@bu.edu), 4/3/2025
# Description: url patterns for the restaurant app

from django.urls import path
from django.conf import settings
from .import views

#url patterns for this app
urlpatterns = [ 
    path(r'', views.ShowAllVotersView.as_view(), name='home'),
    path(r'voters', views.ShowAllVotersView.as_view(), name='voters'),
    path(r'voter/<int:pk>', views.VoterDetailView.as_view(), name='voter'),
    path(r'graphs', views.GraphBetailView.as_view(), name='graph'),

]
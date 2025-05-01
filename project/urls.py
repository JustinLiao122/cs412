# File: project/urls.py
# Author: Justin Liao (liaoju@bu.edu), 4/26/2025
# Description: url patterns for the project app

from django.urls import path
from django.conf import settings
from .import views
from django.contrib.auth import views as auth_views
from .views import *


#url patterns for this app
urlpatterns = [ 
    path(r'', views.Shop.as_view(), name='shop'),
    path(r'item/<int:pk>/', views.SingleItem.as_view(), name='item'),
    path(r'cart/', views.ActiveCartDetailView.as_view(), name='Cart'),
    path(r'PastOrders/', views.PastOrders.as_view(), name='PastOrders'),
    path('login/', auth_views.LoginView.as_view(template_name='project/login.html'), name='Login'), 
	path('logout/', auth_views.LogoutView.as_view(template_name='project/logged_out.html'), name='Logout'),
    path(r'cart/add/<int:item_id>/', views.AddToCartView, name='AddToCart'),
    path('cart/switch/<int:cart_id>/', views.switch_to_cart, name='switch_to_cart'),
    path('cart/remove/<int:item_id>/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('orderDetail/<int:cart_id>/', views.orderDetail.as_view() , name= 'OrderDetail'),
    path('PastOrders/', views.PastOrders.as_view() , name= 'PastOrders'),
    path('CreateCart/', views.CreateCart.as_view() , name= 'CreateCart'),
    path('DeleteCart/<int:pk>/', views.DeleteCart.as_view() , name= 'DeleteCart'),
    path('PastOrder/<int:pk>/' , views.SinglePastOrder.as_view() , name= 'PastOrder'),
    path('PastOrder/<int:pk>/switchstart/', views.SinglePastOrder.as_view(), name='SwitchStart'),
    path("PastOrder/<int:pk>/SplitRoute/", views.SplitRouteView.as_view(), name="SplitRoute"),
    path('create_customer', views.CreateCustomerView.as_view(), name='create_customer'),
    path(r'cart/rename/<int:pk>/', views.RenameCartView.as_view(), name='RenameCart'),
    path('PastOrder/<int:pk>/reorder/', views.ReorderView.as_view(), name='reorder'),


]


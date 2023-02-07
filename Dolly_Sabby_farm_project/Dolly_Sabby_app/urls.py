from django.conf.urls import url
from django.urls import path
from Dolly_Sabby_app import views
from .views import *


app_name = 'Dolly_Sabby_app'

urlpatterns = [

#using functions
    # path('',views.index,name='index'),
    # path('product/',views.product,name='product'),
    # path('product_details/',views.product_details,name='product_details'),
    # path('Cart/',views.Cart,name='Cart'),

 #using classes
     path('',views.IndexView.as_view(),name='index'),


    path('product/',views.ProductView.as_view(),name='product'),
    path('product/<slug:slug>/',views.ProductDetailsView.as_view(),name='product_details'),

    path('add_to_cart/<int:pro_id>/',views.AddToCartView.as_view(),name='add_to_cart'),
    path('my_cart/',views.MyCartView.as_view(),name='my_cart'),
    path('manage_cart/<int:cp_id>/',views.ManageCartView.as_view(),name='manage_cart'),
    path('empty_cart/',views.EmptyCartView.as_view(),name='empty_cart'),

    path('checkout/',views.CheckoutView.as_view(),name='checkout'),

    path('khaltipayment/',views.KhaltiPaymentView.as_view(),name='khaltipayment'),
    path('paypal/',views.PaypalPaymentView.as_view(),name='paypal'),

    path('register/',views.CustomerRegistrationView.as_view(),name='register'),

    path('logout/',views.CustomerLogoutView.as_view(),name='logout'),
    path('login/',views.CustomerLoginView.as_view(),name='login'),

    path('profile/',views.CustomerProfileView.as_view(),name='profile'),
    path('profile/order-<int:pk>/',views.CustomerOrderDetailView.as_view(),name='customerorderdetail'),

    path('search/',views.SearchView.as_view(),name='search'),

#Admin side
    path('adminlogin/',views.AdminLoginView.as_view(),name='adminlogin'),
    path('adminhome/',views.AdminHomeView.as_view(),name='adminhome'),
    path('adminorder/<int:pk>/',views.AdminOrderDetailView.as_view(),name='adminorderdetail'),

    path('adminorderlist/',views.AdminOrderListView.as_view(),name='adminorderlist'),

    path('adminorder-<int:pk>-change/',views.AdminOrderStatusView.as_view(),name='adminorderstatuschange'),


    path('job/',views.index2,name='index2'),




]

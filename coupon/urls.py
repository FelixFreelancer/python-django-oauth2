from django.urls import path


from . import views

urlpatterns = [
    path('create/v0.1', views.couponCreate, name='couponCreate'),
    path('redeem/v0.1', views.couponRedeem, name='couponValidate'),
    path('validate/v0.1', views.couponValidate, name='couponValidate'),
    path('activate/v0.1', views.couponActivate, name='couponActivate'),
]
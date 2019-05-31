from django.urls import path


from . import views

urlpatterns = [
    path('request/v0.1', views.getToken_v_01, name='request'),
    path('request/v1.1', views.getToken_v_11, name='request'),
    path('request/v1.2', views.getToken_v_12, name='request'),
]
from django.urls import path


from . import views

urlpatterns = [
    path('buyNotify', views.buyNotify, name='buyNotify'),
    path('useNotify', views.useNotify, name='useNotify'),
]
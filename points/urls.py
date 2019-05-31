from django.urls import path


from . import views

urlpatterns = [
    path('add/v0.1', views.pointsAdd, name='pointsAdd'),
    path('deduct/v0.1', views.pointsDeduct, name='pointsDeduct'),
    path('enquiry/v0.1', views.pointsEnquiry, name='pointsEnquiry'),
    path('add/v1.2', views.pointsAdd_v_12, name='pointsAddV12'),
    path('deduct/v1.2', views.pointsDeduct_v_12, name='pointsDeductV12'),
    path('enquiry/v1.2', views.pointsEnquiry_v_12, name='pointsEnquiryV12'),
]
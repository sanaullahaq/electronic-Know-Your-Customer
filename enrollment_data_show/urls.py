from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path('enter_student_data/', views.enter_student_data, name='enter_student_data'),
    path('create_customer/', views.create_customer, name='create_customer'),
    path('view_student_full_info/<int:student_id>/', views.view_student_full_info,
         name='view_student_full_info'),

    path('update_student_info/<int:student_id>/', views.update_student_info, name='update_student_info'),
    path('delete_student_info/<int:student_id>/', views.delete_student_info, name='delete_student_info'),
    path('view_customer_full_info/<int:customer_id>/', views.view_customer_full_info, name='view_customer_full_info'),
    path('delete_customer/<int:customer_id>/', views.delete_customer, name='delete_customer'),

    path('delete_facebank_data/', views.delete_facebank, name='delete_facebank_data'),
]

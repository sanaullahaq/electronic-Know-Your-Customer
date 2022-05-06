from django.urls import path
from . import views

urlpatterns = [
    path('view_student_info_customer_end/<str:customer_key>/<str:student_id>',
         views.ViewStudentInfoCustomerEnd.as_view(), name='view_student_info_customer_end'),
]

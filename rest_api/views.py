from django.http import Http404
from enrollment_data_show.models import *
from rest_framework import generics
from .serializers import *
from django.shortcuts import get_object_or_404


class ViewStudentInfoCustomerEnd(generics.ListAPIView):
    serializer_class = StudentModelSerializer

    def get_queryset(self):
        student_id = self.kwargs['student_id']
        customer_key = self.kwargs['customer_key']

        if student_id == 'unknown':
            # return Response('No student data found!!!')
            raise Http404("")
        try:
            student = Student.objects.get(nsuID=student_id)
        except Student.DoesNotExist:
            # return Response('No student data found!!!')
            raise Http404("")

        accessible_fields = get_object_or_404(Customer, key=customer_key).accessible_fields
        accessible_fields = [f.strip() for f in accessible_fields.split(',')]

        student_model_fields_name = [field.name for field in Student._meta.get_fields()]
        course_info_model_fields_name = [field.name for field in CourseInfo._meta.get_fields()]
        personal_info_model_fields_name = [field.name for field in PersonalInfo._meta.get_fields()]
        economic_info_model_fields_name = [field.name for field in EconomicInfo._meta.get_fields()]

        student_model_fields_name_accessible_by_customer = list(
            set(student_model_fields_name).intersection(accessible_fields))

        course_info_model_fields_name_accessible_by_customer = list(
            set(course_info_model_fields_name).intersection(accessible_fields))

        personal_info_model_fields_name_accessible_by_customer = list(
            set(personal_info_model_fields_name).intersection(accessible_fields))

        economic_info_model_fields_name_accessible_by_customer = list(
            set(economic_info_model_fields_name).intersection(accessible_fields))

        course_info = CourseInfoModelSerializer
        personal_info = PersonalInfoModelSerializer
        economic_info = EconomicInfoModelSerializer

        if len(student_model_fields_name_accessible_by_customer) != 0:
            student_model_fields_name_accessible_by_customer += ['course_info', 'personal_info', 'economic_info']
            self.serializer_class.Meta.fields = student_model_fields_name_accessible_by_customer
        else:
            self.serializer_class.Meta.fields = ['course_info', 'personal_info', 'economic_info']

        if len(course_info_model_fields_name_accessible_by_customer) != 0:
            course_info.Meta.fields = course_info_model_fields_name_accessible_by_customer
        else:
            course_info.Meta.fields = ''

        if len(personal_info_model_fields_name_accessible_by_customer) != 0:
            personal_info.Meta.fields = personal_info_model_fields_name_accessible_by_customer
        else:
            personal_info.Meta.fields = ''

        if len(economic_info_model_fields_name_accessible_by_customer) != 0:
            economic_info.Meta.fields = economic_info_model_fields_name_accessible_by_customer
        else:
            economic_info.Meta.fields = ''

        self.serializer_class.course_info = course_info
        self.serializer_class.personal_info = personal_info
        self.serializer_class.economic_info = economic_info

        return Student.objects.all().filter(nsuID=student_id)

from rest_framework import serializers, status
from rest_framework.response import Response
from enrollment_data_show.models import Student, CourseInfo, PersonalInfo, EconomicInfo


class CourseInfoModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseInfo
        fields = '__all__'


class PersonalInfoModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalInfo
        fields = '__all__'


class EconomicInfoModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = EconomicInfo
        fields = '__all__'


class StudentModelSerializer(serializers.ModelSerializer):
    course_info = CourseInfoModelSerializer(many=False, read_only=True)
    personal_info = PersonalInfoModelSerializer(many=False, read_only=True)
    economic_info = EconomicInfoModelSerializer(many=False, read_only=True)

    class Meta:
        model = Student
        fields = '__all__'

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     if not serializer.is_valid(raise_exception=False):
    #         return Response({"Fail": "blabla"}, status=status.HTTP_400_BAD_REQUEST)
    #
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response({"Success": "blabla"}, status=status.HTTP_201_CREATED, headers=headers)

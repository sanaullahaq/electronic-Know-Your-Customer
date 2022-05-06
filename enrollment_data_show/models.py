from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from private_storage.fields import PrivateFileField
import os


# Create your models here.
def image_dir(instance, filename):
    return 'uploads/images/nsuID_{0}/{1}'.format(instance.nsuID, filename)


class EconomicInfo(models.Model):
    # id = models.IntegerField(primary_key=True)
    nid_number = models.IntegerField()
    student_occupation = models.CharField(max_length=50)
    student_annual_income = models.FloatField()
    bank_account_number = models.IntegerField()

    def __str__(self):
        return 'NID - ' + str(self.nid_number)


class PersonalInfo(models.Model):
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=6)
    bloodGroup = models.CharField(max_length=3)
    marital_status = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=14)
    fathers_name = models.CharField(max_length=100)
    fathers_occupation = models.CharField(max_length=50)
    fathers_phone_number = models.CharField(max_length=14)
    mothers_name = models.CharField(max_length=100)
    mothers_occupation = models.CharField(max_length=50)
    mothers_phone_number = models.CharField(max_length=14)
    address = models.CharField(max_length=250)

    def __str__(self):
        return 'Fathers name - ' + self.fathers_name + ' - Fathers Phone - ' + str(self.fathers_phone_number)


class CourseInfo(models.Model):
    courses = models.CharField(max_length=200)
    creditHours = models.CharField(max_length=100)
    creditPassed = models.FloatField(default=10)
    grades = models.CharField(max_length=100)

    def __str__(self):
        return 'Courses - ' + self.courses[:18] + '... - Credit Passed - ' + str(self.creditPassed)


class Student(models.Model):
    # Academic Information
    image = PrivateFileField(upload_to=image_dir)
    nsuID = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    birth_certificate_number = models.IntegerField()
    department = models.CharField(max_length=100)
    majorIn = models.CharField(max_length=100)
    enrolled_in = models.IntegerField()
    cgpa = models.FloatField()
    sscPassYear = models.IntegerField()
    sscGpa = models.FloatField()
    hscPassYear = models.IntegerField()
    hscGpa = models.FloatField()

    course_info = models.OneToOneField(CourseInfo, null=True, on_delete=models.CASCADE,
                                       related_name='student_course_info')
    personal_info = models.OneToOneField(PersonalInfo, null=True, on_delete=models.CASCADE,
                                         related_name='student_personal_info')
    economic_info = models.OneToOneField(EconomicInfo, null=True, on_delete=models.CASCADE,
                                         related_name='student_economic_info')

    def __str__(self):
        return self.name + ' - ' + str(self.nsuID)


@receiver(pre_delete, sender=Student)
def student_image_delete(sender, instance, **kwargs):
    path = 'media/private-media/uploads/images/nsuID_{0}'.format(instance.nsuID)
    if instance.image.storage.exists(instance.image.name):
        instance.image.delete(False)
        print("\nImage removed from directory '" + path + "'\n")
        try:
            if os.path.exists(path):
                os.rmdir(path)
                print("\nDirectory '" + path + "' removed\n")
        except OSError as error:
            print("\nError in removing directory '" + path + "'\n")


class Customer(models.Model):
    customer_name = models.CharField(max_length=100)
    accessible_fields = models.CharField(max_length=200)
    key = models.CharField(max_length=16)

    def __str__(self):
        return self.customer_name

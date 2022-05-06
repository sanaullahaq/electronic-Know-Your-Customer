from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.urls import reverse

from .models import *
import uuid
from FACE_RECOGNITION.mtcnn_cv2.Detection import DetectionMtcnn
from FACE_RECOGNITION.FR.Recognition import FaceModel
import cv2
import numpy
import os
from django.contrib import messages
import warnings

warnings.filterwarnings('ignore')


def home(request):
    if request.method == 'POST':
        student_nsu_id = request.POST['student_id']
        customer_key = request.POST['customer_key']
        image = request.FILES.getlist('student_image_id')

        if len(image) == 1:
            face_detector = DetectionMtcnn()
            image = cv2.imdecode(numpy.fromstring(image[0].read(), numpy.uint8), cv2.IMREAD_UNCHANGED)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            in_cropped_face, bboxes, landmarks = face_detector.get_cropped_face(image)

            if in_cropped_face is None:
                return render(request, 'enrollment_data_show/home.html',
                              {'message': 'No face found from the attached image, Upload a single face image'})
            elif len(in_cropped_face) > 1:
                return render(request, 'enrollment_data_show/home.html',
                              {
                                  'message': 'More than one face found from the attached image, Upload a single face '
                                             'image'})
            else:
                FACE_RECOGNITION_MODEL = FaceModel('enrollment_data_show/checkpoints/facebank',
                                                   init_facebank=False)
                crop_face = in_cropped_face[0]
                student_nsu_id, score = FACE_RECOGNITION_MODEL.infer([crop_face])
                return redirect('rest_api:view_student_info_customer_end', customer_key=customer_key,
                                student_id=student_nsu_id)

        elif len(student_nsu_id) != 0:
            return redirect('rest_api:view_student_info_customer_end', customer_key=customer_key,
                            student_id=student_nsu_id)
        else:
            return render(request, 'enrollment_data_show/home.html', {'message': 'Please enter NSU ID or insert an '
                                                                                 'image'})
    else:
        return render(request, 'enrollment_data_show/home.html')


def admin_login(request):
    if request.method == 'GET':
        return render(request, 'enrollment_data_show/admin_login.html', {'form': AuthenticationForm()})
    elif request.method == 'POST':
        user = authenticate(request, username=request.POST['admin_username'], password=request.POST['password'])
        if user is None:
            return render(request, 'enrollment_data_show/admin_login.html',
                          {'form': AuthenticationForm(), 'error': 'Username or Password is incorrect'})
        else:
            login(request, user)
            return redirect('enter_student_data')


@login_required
def admin_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


def convert_grades_to_gradesPoints(grades):
    grades_points = []
    for i in grades:
        if i.__eq__('A'):
            grades_points.append(4.0)
        elif i.__eq__('A-'):
            grades_points.append(3.7)
        elif i.__eq__('B+'):
            grades_points.append(3.3)
        elif i.__eq__('B'):
            grades_points.append(3.0)
        elif i.__eq__('B-'):
            grades_points.append(2.7)
        elif i.__eq__('C+'):
            grades_points.append(2.3)
        elif i.__eq__('C'):
            grades_points.append(2.0)
        elif i.__eq__('C-'):
            grades_points.append(1.7)
        elif i.__eq__('D+'):
            grades_points.append(1.3)
        elif i.__eq__('D'):
            grades_points.append(1)
        elif i.__eq__('F'):
            grades_points.append(0.0)
        elif i.__eq__('I'):
            grades_points.append(0.0)
        elif i.__eq__('W'):
            grades_points.append(0.0)
        elif i.__eq__('R'):
            grades_points.append(0.0)
        else:
            raise ValueError("Sorry, Unknown Grade Submitted!!!")
    return grades_points


def set_academic_info(request, student):
    student.nsuID = request.POST['id']
    student.name = request.POST['name']
    student.email = request.POST['email']
    student.birth_certificate_number = request.POST['birth_certificate_number']
    student.department = request.POST['department']
    student.majorIn = request.POST['major']
    student.enrolled_in = request.POST['enrolled_in']
    student.sscPassYear = request.POST['ssc_passing_year']
    student.sscGpa = request.POST['ssc_gpa']
    student.hscPassYear = request.POST['hsc_passing_year']
    student.hscGpa = request.POST['hsc_gpa']


def set_course_info(request, student, courses, creditHours, grades, course_info):
    course_info = course_info
    course_info.courses = ', '.join(courses)
    course_info.creditHours = ', '.join(creditHours)
    course_info.grades = ', '.join(grades)

    creditPassed = 0
    for c in creditHours:
        creditPassed = creditPassed + float(c)
    course_info.creditPassed = creditPassed

    grades_points = convert_grades_to_gradesPoints(grades)

    total_credit_points_hours = 0
    for (p, c) in zip(grades_points, creditHours):
        total_credit_points_hours = total_credit_points_hours + (p * float(c))
    student.cgpa = format(total_credit_points_hours / creditPassed, ".2f")

    course_info.save()
    student.course_info = course_info


def set_personal_info(request, student, personal_info):
    personal_info = personal_info
    personal_info.date_of_birth = request.POST['dob']
    personal_info.gender = request.POST['gender']
    personal_info.bloodGroup = request.POST['blood_group']
    personal_info.marital_status = request.POST['marital_status']
    personal_info.phone_number = request.POST['phone_number']
    personal_info.fathers_name = request.POST['fathers_name']
    personal_info.fathers_occupation = request.POST['fathers_occupation']
    personal_info.fathers_phone_number = request.POST['fathers_phone_number']
    personal_info.mothers_name = request.POST['mothers_name']
    personal_info.mothers_occupation = request.POST['mothers_occupation']
    personal_info.mothers_phone_number = request.POST['mothers_phone_number']
    personal_info.address = request.POST['address']
    personal_info.save()

    student.personal_info = personal_info


def set_economic_info(request, student, economic_info):
    economic_info = economic_info
    economic_info.nid_number = request.POST['nid_number']
    economic_info.student_occupation = request.POST['student_occupation']
    economic_info.student_annual_income = request.POST['student_annual_income']
    economic_info.bank_account_number = request.POST['bank_account_number']
    economic_info.save()

    student.economic_info = economic_info


def update_create_student_obj(request, student, course_info, personal_info, economic_info):
    courses = [x.upper().strip() for x in request.POST['courseList'].split(',')]
    creditHours = [x.strip() for x in request.POST['creditList'].split(',')]
    grades = [x.upper().strip() for x in request.POST['gradeList'].split(',')]

    if len(courses) == len(creditHours) and len(courses) == len(grades):

        set_academic_info(request, student)  # academic information setting method
        # course information setting method
        set_course_info(request=request, student=student, courses=courses, creditHours=creditHours, grades=grades,
                        course_info=course_info)
        set_personal_info(request, student, personal_info)  # personal information setting method
        set_economic_info(request, student, economic_info)  # economic information setting method
        return 'Student info added successfully!!!'
    else:
        raise ValueError('Number courses/credit hours/grades are not equal')


@login_required
def enter_student_data(request):
    student = Student()
    course_info = CourseInfo()
    personal_info = PersonalInfo()
    economic_info = EconomicInfo()

    if request.method == 'POST':
        image = request.FILES.getlist('image')[0]
        original_image = image

        # face detector
        face_detector = DetectionMtcnn()
        image = cv2.imdecode(numpy.fromstring(image.read(), numpy.uint8), cv2.IMREAD_UNCHANGED)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        in_cropped_face, bboxes, landmarks = face_detector.get_cropped_face(image)
        if in_cropped_face is None:
            return render(request, 'enrollment_data_show/enter_student_data.html',
                          {'message': 'No face found from the attached image, Upload a single face image',
                           'studentDict': Student.objects.all()})
        elif len(in_cropped_face) > 1:
            return render(request, 'enrollment_data_show/enter_student_data.html',
                          {'message': 'More than one face found from the attached image, Upload a single face image',
                           'studentDict': Student.objects.all()})
        else:
            # face registration
            if os.path.exists('enrollment_data_show/checkpoints/facebank/facebank.pth'):
                init_facebank = False
            else:
                init_facebank = True
            FACE_RECOGNITION_MODEL = FaceModel('enrollment_data_show/checkpoints/facebank', init_facebank=init_facebank)
            crop_face = in_cropped_face[0]
            registered = FACE_RECOGNITION_MODEL.add_face([crop_face], request.POST['id'])
            print('Registered: ', registered)
            student.image = original_image

            try:
                message = update_create_student_obj(request=request, student=student, course_info=course_info,
                                                    personal_info=personal_info, economic_info=economic_info)
            except ValueError as error:
                return render(request, 'enrollment_data_show/enter_student_data.html',
                              {'message': str(error), 'studentDict': Student.objects.all()})
            student.save()
            return render(request, 'enrollment_data_show/enter_student_data.html',
                          {'message': message, 'studentDict': Student.objects.all()})
    else:
        return render(request, 'enrollment_data_show/enter_student_data.html', {'studentDict': Student.objects.all()})


def get_all_models_fields_name():
    student_model_fields_name = [field.name for field in Student._meta.get_fields()]
    student_model_fields_name += [field.name for field in CourseInfo._meta.get_fields()]
    student_model_fields_name += [field.name for field in PersonalInfo._meta.get_fields()]
    student_model_fields_name += [field.name for field in EconomicInfo._meta.get_fields()]
    try:
        while True:
            student_model_fields_name.remove('id')
    except ValueError:
        pass

    try:
        while True:
            student_model_fields_name.remove('student')
    except ValueError:
        pass

    student_model_fields_name.remove('course_info')
    student_model_fields_name.remove('personal_info')
    student_model_fields_name.remove('economic_info')
    student_model_fields_name.remove('student_course_info')
    student_model_fields_name.remove('student_personal_info')
    student_model_fields_name.remove('student_economic_info')

    return student_model_fields_name


@login_required
def create_customer(request):
    student_model_fields_name = get_all_models_fields_name()
    # print(student_model_fields_name)
    if request.method == 'POST':
        customer = Customer()
        customer.customer_name = request.POST['customer_name']

        selected_fields = request.POST.getlist('selected_fields')
        selected_fields = ', '.join(selected_fields)
        # print(selected_fields)
        customer.accessible_fields = selected_fields
        customer.key = uuid.uuid4().hex[:16].upper()
        customer.save()

        return render(request, 'enrollment_data_show/create_customer.html',
                      {'message': 'Customer Created Successfully',
                       'student_model_fields_name': student_model_fields_name,
                       'customerDict': Customer.objects.all()})
    else:
        return render(request, 'enrollment_data_show/create_customer.html',
                      {'student_model_fields_name': student_model_fields_name,
                       'customerDict': Customer.objects.all()})


@login_required
def update_student_info(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    course_info = get_object_or_404(CourseInfo, pk=student.course_info.id)
    personal_info = get_object_or_404(PersonalInfo, pk=student.personal_info.id)
    economic_info = get_object_or_404(EconomicInfo, pk=student.economic_info.id)
    if request.method == "POST":
        try:
            message = update_create_student_obj(request=request, student=student, course_info=course_info,
                                                personal_info=personal_info, economic_info=economic_info)
        except ValueError as error:
            return render(request, 'enrollment_data_show/view_student_full_info.html',
                          {'message': str(error), 'student': student})
        if message.__eq__('Student info added successfully!!!'):
            message = 'Student info updated successfully!!!'
            student.save()
            return render(request, 'enrollment_data_show/view_student_full_info.html',
                          {'message': message, 'student': student})
        else:
            return render(request, 'enrollment_data_show/update_student_info.html', {'student': student,
                                                                                     'message': message})
    else:
        return render(request, 'enrollment_data_show/update_student_info.html', {'student': student})


@login_required
def delete_student_info(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    if request.method == 'POST':
        course_info = get_object_or_404(CourseInfo, pk=student.course_info.id)
        personal_info = get_object_or_404(PersonalInfo, pk=student.personal_info.id)
        economic_info = get_object_or_404(EconomicInfo, pk=student.economic_info.id)
        student.delete(), course_info.delete(), personal_info.delete(), economic_info.delete()
    return redirect('enter_student_data')


@login_required
def view_student_full_info(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    return render(request, 'enrollment_data_show/view_student_full_info.html', {'student': student})


@login_required
def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    if request.method == 'POST':
        customer.delete()
    return redirect('create_customer')


@login_required
def view_customer_full_info(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    return render(request, 'enrollment_data_show/view_customer_full_info.html', {'customer': customer})


@login_required
def delete_facebank(request):
    path1 = 'enrollment_data_show/checkpoints/facebank/facebank.pth'
    path2 = 'enrollment_data_show/checkpoints/facebank/names.npy'
    if os.path.exists(path1):
        os.remove(path1)
        print("\n'" + path1 + 'Deleted\n')
        os.remove(path2)
        print("\n'" + path2 + 'Deleted\n')
        messages.success(request, 'Facebank Deleted Successfully!!!')
        print('\nFacebank Deleted Successfully!!!\n')
        return redirect('home')
    else:
        messages.warning(request, 'No facebank to Delete!!!')
        print('\nNo facebank to Delete!!!\n')
        return redirect('home')

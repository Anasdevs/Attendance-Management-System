from django.contrib.auth.hashers import make_password, check_password
import os
from django.core.mail import send_mail
from django.conf import settings
import dotenv
from django.http import JsonResponse
import string
import random
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from ams.models import Faculty, Class, Student, Attendance
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from datetime import datetime
from django.db.models import Q, Case, When, Value, Subquery, OuterRef
from django.db.models.functions import Coalesce
import csv

dotenv.load_dotenv()


@csrf_exempt
def send_password(request):
    if request.method == 'POST':
        # Retrieve JSON data from the request body
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')

        try:
            # Check if faculty email exists in the Faculty model
            faculty = Faculty.objects.get(faculty_email=email)
        except ObjectDoesNotExist:
            # Return a response indicating that the faculty email is not found
            return JsonResponse({'message': 'Your email is not added. Please contact the administrator.'})

        # Generate a random password
        password = generate_random_password()

        # Send password email
        send_password_email(email, password)

        # Update faculty model with hashed password
        faculty.password = make_password(password)
        faculty.save()

        response_msg = f"Password sent to {email}"
        return JsonResponse({'message': response_msg})

    return JsonResponse({'error': 'Invalid request'})

# Rest of the code remains the same...

def generate_random_password(length=8):
    # Generate a random password of the specified length
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def send_password_email(email, password):
    # Compose email message
    subject = 'Your Account Password for AMS'
    message = f'Your account password is: {password}'
    # from_email = settings.EMAIL_HOST_USER  # Access EMAIL_HOST_USER from settings
    from_email = os.environ.get('EMAIL_HOST_USER')
    recipient_list = [email]
    print(from_email)
    # Send email
    send_mail(subject, message, from_email, recipient_list)


from django.contrib.auth import authenticate

# ...

@csrf_exempt
def validate_password(request):
    if request.method == 'POST':
        # Retrieve JSON data from the request body
        data = json.loads(request.body)
        email = data.get('email')
        password_entered = data.get('password')

        try:
            # Retrieve the faculty with the provided email
            faculty = Faculty.objects.get(faculty_email=email)

            # Check if the provided password matches the hashed password in the model
            if check_password(password_entered, faculty.password):
                return JsonResponse({'success': True, 'message': 'Password validated successfully!'})

            else:
                return JsonResponse({'success': False, 'message': 'Invalid password'})

        except Faculty.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Faculty not found'})

    return JsonResponse({'success': False, 'message': 'Invalid request'})


    
@csrf_exempt
def signin(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password_entered = data.get('password')
        
        try:
            faculty = Faculty.objects.get(faculty_email=email)
            
            if check_password(password_entered, faculty.password):
                # Create a session for the authenticated user
                request.session['faculty_email'] = faculty.faculty_email
                # print(faculty.faculty_email)
                request.session.save()  # Save the session data
                # print(request.session.session_key) 
                # faculty_email = request.session.get('faculty_email')
                # print(faculty_email)

                return JsonResponse({'success': True, 'message': 'Password validated successfully!'})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid email or password.'})
        
        except Faculty.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid email or password.'})
    
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request'})





@csrf_exempt
# @login_required
def dashboard_data(request):
    try:
        faculty_email = request.session.get('faculty_email')
        # print(faculty_email)

        if faculty_email:
            faculty = Faculty.objects.get(faculty_email=faculty_email)

            faculty_data = {
                'name': faculty.faculty_name,  # Use faculty_name instead of name
                'email': faculty.faculty_email
            }

            assigned_classes = faculty.get_assigned_classes()
            classes_list = []

            for assigned_class in assigned_classes:
                class_data = {
                    'course_id': assigned_class.course_id,
                    'course': assigned_class.course,
                    'semester': assigned_class.semester,
                    'section': assigned_class.section,
                    'shift': assigned_class.shift,
                    'subject': assigned_class.subject,
                }
                classes_list.append(class_data)

            response_data = {
                'faculty': faculty_data,
                'classes': classes_list
            }

            return JsonResponse(response_data, safe=False)

        else:
            return JsonResponse({'error': 'Authentication required'})

    except Faculty.DoesNotExist:
        return JsonResponse({'error': 'Faculty not found'})
    
@csrf_exempt
def take_attendance(request):
    if request.method == 'GET':
        course_id = request.GET.get('course_id')
        date = request.GET.get('date')

        attendance_subquery = Attendance.objects.filter(
            student_id=OuterRef('pk'),
            date=date
        ).values('status', 'date')

        # print(attendance_subquery)
        
        student_data = Student.objects.filter(class_attendance__course_id=course_id).values(
            'enrolment_no',
            'name',
        ).annotate(
            filtered_status=Coalesce(Subquery(attendance_subquery.values('status')), Value(None)),
            filtered_date=Coalesce(Subquery(attendance_subquery.values('date')), Value(None)),
        ).distinct()

        # print(student_data)
        students = []
        for data in student_data:
            student = {
                'enrolment_no': data['enrolment_no'],
                'name': data['name'],
                'attendance__status': data['filtered_status'],
                'attendance__date': data['filtered_date'],
            }
            students.append(student)
        # print(students)
        response_data = {'students': students}
        # print(response_data)
        return JsonResponse(response_data)
        


@require_POST
@csrf_exempt
def submit_attendance(request):
    try:
        data = json.loads(request.body)
        course_id = data.get('course_id')
        attendance_data = data.get('attendance_data')

        # Retrieve the class object by course ID
        class_obj = Class.objects.get(course_id=course_id)

        for fields in attendance_data:
            enrolment_no = fields.get('enrolment_no')
            attendance_status = fields.get('attendance__status')
            attendance_date_str = fields.get('attendance_date')
            # print(attendance_date_str)
            # Convert the date string to a datetime object
            # attendance_date = datetime.strptime(attendance_date_str, '%Y-%m-%d').date()
            attendance_date = datetime.fromisoformat(attendance_date_str)
            # print(attendance_date)

            # Retrieve the student by enrolment_no
            student_obj = Student.objects.get(enrolment_no=enrolment_no, class_attendance=class_obj)

            # Create or update the attendance record for the student
            attendance, created = Attendance.objects.get_or_create(
                student=student_obj,
                class_attendance=class_obj,
                date=attendance_date
            )
            attendance.status = attendance_status
            attendance.save()

        return JsonResponse({'message': 'Attendance submitted successfully'})
    except Exception as e:
        print("Exception:", e)
        return JsonResponse({'error': str(e)})
    

from django.db.models import Count, F
@csrf_exempt
def generate_attendance_report(request):
    if request.method == 'GET':
        start_date = request.GET.get('startDate')
        end_date = request.GET.get('endDate')
        course_id = request.GET.get('courseId')  # Add courseId parameter to get the class ID

        # Fetch attendance data based on the provided start date, end date, and class ID
        attendance_data = Attendance.objects.filter(
            date__range=[start_date, end_date],
            class_attendance__course_id=course_id
        )

        # Prepare the CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="attendance_report_{start_date}_{end_date}.csv"'

        # Create the CSV writer
        writer = csv.writer(response)
        writer.writerow(['Enrollment Number', 'Name', 'Subject', 'Present Days', 'Total Days', 'Percentage'])

        # Calculate attendance statistics for each student
        attendance_stats = attendance_data.values(
            'student__enrolment_no',
            'student__name',
            'class_attendance__subject',
        ).annotate(
            total_present=Count('id', filter=Q(status='Present')),
            total_days=Count('id')
        ).order_by('student__enrolment_no')

        # Write attendance data to the CSV file
        for stats in attendance_stats:
            enrollment_no = stats['student__enrolment_no']
            name = stats['student__name']
            subject = stats['class_attendance__subject']
            present_days = stats['total_present']
            total_days = stats['total_days']
            percentage = (present_days / total_days) * 100 if total_days > 0 else 0

            writer.writerow([enrollment_no, name, subject, present_days, total_days, percentage])

        return response

    return JsonResponse({'error': 'Invalid request'})

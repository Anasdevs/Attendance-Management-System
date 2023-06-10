from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json


# ====================== Test View ==================
def test(request):
    data = {
        'message': 'AMS Server Online!'
    }
    return JsonResponse(data)

from .models import MSI

############################# TEACHER's View #####################

# =========== teacher's functions =============

@api_view(['POST'])
def teacher_dashboard(request):
    data = json.loads(request.body)
    UID = data.get('user_id')
    # onload fetch
    #     teacher profile
    #     total class

    # get teacher's profile
    # teacherIDs from MSI
    # get class list (by teacher's classes assigned)

    return JsonResponse({"Status":False,'message': 'server error'}, status=501)

    '''
    {
        "user_id":"123"
    }
    '''

@api_view(['POST'])
def create_class(request):
    data = json.loads(request.body)
    email = data.get('email')
    cource_name = data.get('cource_name')
    sem = data.get('semester')
    section = data.get('section')
    subject = data.get('subject')
    students = data.get('students')

    MSI.add_new_class(cource_name,sem,section,subject, email, students)

    return JsonResponse({"Status":True,'message': 'Success'}, status=200)


# ======================== TEACHER LOGIN ROUTES =======================

# if we wanted to do email only type
'''
# ---- Admin verifing teacher's email (1st step of teacher add)
@api_view(['POST'])
def admin_teacher_Add(request):
    data = json.loads(request.body)
    email = data.get('email')
    
    if not MSI.verify_registered_email(email):
        response = admin_teacher_Add(email)
        if not response:
            return JsonResponse({"Status":False,'message': 'server error'}, status=501)
        else:
            MSI.save()
            return JsonResponse({"Status":True,'message': 'Successfully added'}, status=200)
    else:

        return JsonResponse({"status":True, 'message': 'already exist'}, status=200)

# --------- check for verify
@api_view(['POST'])
def verify_teacher(request):
    data = json.loads(request.body)
    email = data.get('email')
    if not MSI.verify_registered_email(email):
        return JsonResponse({"Status":False,'message': 'email not found'}, status=200)
    else:
        exist = MSI.check_teacher_user(email)
        if exist["status"] == True:
            return JsonResponse({"Status":True,"userCreated":True,"password":exist["password"],'message': 'User Found'}, status=200)
        else:
            return JsonResponse({"Status":True,"userCreated":False,"password":None,'message': 'email verified But user not created'}, status=200)
'''


# ---------------- login ---------------------
@api_view(['POST'])
def teacher_login(request):

    data = json.loads(request.body)
    email = data.get('email')
    password = data.get('password')
    exist = MSI.teacherLogin(email,password)

    if exist["status"] == True:
        return  JsonResponse({"status":"success","email":"email"}, status=200)
    return JsonResponse(exist)

    '''
    {
        "email" : "harsh@email.com",
        "password":"harshharsh"
    }
    '''

# ------------ register teacher who's verified
# from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
@api_view(['POST'])
def teacher_register(request):
    data = json.loads(request.body)
    email = data.get('email')
    name = data.get('name')
    title = data.get('title')

    # try:
    res = MSI.add_new_teacher(email,name, title)
    print(res)
    return JsonResponse({"status":True, "response":"Success"}, status= 200)

    '''
    {
        "email":"harshagnihotri90@gmail.com",
        "name":"test teacher",
        "title":"Assitant professor"
    }
    '''

def test1():
    res ={
        "email":"harshagnihotri90@gmail.com",
        "name":"test teacher",
        "title":"Assitant professor"
    }
    return MSI.add_new_teacher(email=res["email"], name= res["name"], title= res["title"])
  

print(test1())

@api_view(['POST'])
def adminlogin(request):
    # if request.method == 'POST':
    data = json.loads(request.body)
    login_id = data.get('loginId')
    password = data.get('password')

    if login_id == 'anass' and password == 'anass':
        if (MSI.classes).keys():
            data = {
                "classes":(MSI.classes).keys(),
                "teachers":(MSI.instructors).keys(),
            }
        else:
            data = {
                "classes":(MSI.classes),
                "teachers":(MSI.instructors),
            }
        return JsonResponse({'message': 'Login successful', "data":data}, status=200)
    else:
        # Return error response
        return JsonResponse({'message': 'Invalid login credentials'}, status=400)






#API endpoints for admindashboard 

#Add faculty

from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def add_faculty(request):
    email = request.data.get('email')

    # Perform necessary validation
    # Add the faculty email to the database

    return Response({'message': 'Faculty added successfully'})


#Remove faculty 

@api_view(['POST'])
def remove_faculty(request):
    email = request.data.get('email')

    # Perform necessary validation 
    # Remove the faculty email from the database

    return Response({'message': 'Faculty removed successfully'})



#Edit faculty

@api_view(['POST'])
def edit_faculty(request):
    email = request.data.get('email')

    # Perform necessary validation
    # Update the faculty email in the database

    return Response({'message': 'Faculty email updated successfully'})



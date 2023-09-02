from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from corehr.models import User,AttendanceLogs
from django.utils import timezone
import json
import datetime
# Create your views here.
class CreateUser(ViewSet):
    def create(self,request):
        req_dict=json.loads(request.body)
        res = User.objects.create(emp_no=req_dict.get("emp_no"),
                                emp_name=req_dict.get("emp_name"),
                                first_name=req_dict.get("first_name"),
                                last_name=req_dict.get("last_name"),
                                email_id=req_dict.get("email_id"),
                                father_name=req_dict.get("father_name"),
                                name_as_aadhar=req_dict.get("name_as_aadhar"),
                                emergency_contact_name=req_dict.get("emergency_contact_name"),
                                emergency_contact=req_dict.get("emergency_contact"),
                                aadhar_number=req_dict.get("aadhar_number"),
                                mobile_number=req_dict.get("mobile_number"),
                                designation=req_dict.get("designation"),
                                location=req_dict.get("location"),
                                department=req_dict.get("department"),
                                permanent_address=req_dict.get("permanent_address"),
                                temporary_address=req_dict.get("temporary_address"),
                                date_of_joining=req_dict.get("date_of_joining"),
                                date_of_birth=req_dict.get("date_of_birth"),
                                gender=req_dict.get("gender"),
                                pan=req_dict.get("pan"),
                                maritial_status=req_dict.get("maritial_status"),
                                ctc=req_dict.get("ctc"),
                                is_pf_eligible=req_dict.get("is_pf_eligible"),
                                is_esi_eligible=req_dict.get("is_esi_eligible")
                                  )

        return Response(req_dict,status=200)
    def list(self,request):   
        res = User.objects.all()
        print(res)
        return Response(res.values(),status=200)
    
class UserLogin(ViewSet):
    def create(self,request):        
        today = timezone.localtime()
        is_today_check=timezone.localdate()
        req_body = json.loads(request.body)
        email = req_body.get("email_id")
        user = User.objects.filter(email_id=email).first()
        if not user:
            return Response({"message":"user not found"},status=401)  
        dupRecoed = AttendanceLogs.objects.filter(login_time__gte=is_today_check,user=user).first()
        if dupRecoed:
            return Response({"message":"already logged in"},status=403)
           
        else:
            login = AttendanceLogs.objects.create(user=user,login_time=today,is_present=False)
        return Response("success",status=200)
    def patch(self,request):
        today = timezone.localdate()
        logout_time = timezone.localtime()
        req_body = json.loads(request.body)
        email = req_body.get("email_id")
        user = User.objects.filter(email_id=email).first()
        if not user:
            return Response({"message":"user not found"},status=401)   
        dupRecoed = AttendanceLogs.objects.filter(login_time__gte=today,user=user).values().first()
        if dupRecoed:
            print(dupRecoed)
            in_time = dupRecoed['login_time']
            time_diff = logout_time-in_time
            AttendanceLogs.objects.filter(login_time__gte=today,user=user).update(logout_time=logout_time)  
        print(str(time_diff))
        dateStr = str(time_diff).split(":")
        print(dateStr)
        if int(dateStr[0]) >= 9:
            print("in........")
            AttendanceLogs.objects.filter(login_time__gte=today,user=user).update(is_present=True)

        
        if dupRecoed:
            print("present")
        return Response("success",status=200)
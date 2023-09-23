from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from corehr.models import UserBasicDetails,AttendanceLogs,Events
from django.utils import timezone
from datetime import timedelta,datetime
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt import authentication
from users_api.models import User
import calendar
import numpy
import json
# Create your views here.
class CreateAuthUser(ViewSet):
    def create(self,request):
        req_dict=json.loads(request.body)
        res = User.objects.create(
            email = req_dict.get("email"),
            password = req_dict.get("password"),
            first_name=req_dict.get("first_name"),
            last_name=req_dict.get("last_name"),
            username = req_dict.get("email")
        )
        return Response("created",status=200)
    
class GetMydetails(ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def list(self,request):
        email = request.GET.get("user_email")
        print(email)
        result = UserBasicDetails.objects.filter(email_id=email).values().first()
        print(result)
        return Response(result,status=200)
class CreateUserBasicDetails(ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def create(self,request):
        req_dict=json.loads(request.body)
        user = User.objects.filter(email=req_dict["email_id"]).first()
        res = UserBasicDetails.objects.create(emp_no=req_dict.get("emp_no"),
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
                                is_esi_eligible=req_dict.get("is_esi_eligible"),
                                user=user
                                  )

        return Response(req_dict,status=200)
    def list(self,request):   
        res = UserBasicDetails.objects.all()
        return Response(res.values(),status=200)
    
class AttendancePunching(ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def create(self,request):        
        today = timezone.localtime()
        is_today_check=timezone.localdate()
        
        req_body = json.loads(request.body) 
        print(req_body)       
        email = req_body["user_email"]
        
        user = User.objects.filter(email=email).first()
        print(".......",user)
        if not user:
            return Response({"message":"user not found"},status=401)  
        create_all_logs = AttendanceLogs.objects.filter(login_time__month=today.month,user=user).values("login_time").all()
        if not create_all_logs:
            for x in range(calendar.monthrange(today.year, today.month)[1]):
                da_te=datetime(today.year, today.month, x+1)
                week =da_te.strftime('%A')
                if x+1 == today.day:
                    AttendanceLogs.objects.create(login_time=today,user=user,created_at=da_te,week_day=week)
                else:
                    AttendanceLogs.objects.create(user=user,created_at=da_te,week_day=week)

            return Response({"message":"created records for the month and logged in"},status=200)
        else:
            todays_record = AttendanceLogs.objects.filter(user=user,created_at=is_today_check).values().first()
            if not todays_record["login_time"]:
                AttendanceLogs.objects.filter(user=user,created_at=is_today_check).update(login_time=today)
                return Response({"message":"successfully punched in "},status=200)
            elif todays_record["login_time"]:
                return Response({"message":"Already logged in"},status=200)
            else:
                return Response({"message":"Something Went Wrong"},status=500)
    def patch(self,request):
        today = timezone.localdate()
        logout_time = timezone.localtime()
        req_body = json.loads(request.body)
        email = req_body.get("user_email")
        user = User.objects.filter(email=email).first()
        is_nightshift_user = UserBasicDetails.objects.filter(user=user).first()
        # if night shift user query is login_time__lte
        # if day shift user query is login_time__gte
        if not user:
            return Response({"message":"user not found"},status=401) 
        if is_nightshift_user and is_nightshift_user.is_night_shift:  
            dupRecoed = AttendanceLogs.objects.filter(login_time__lte=today,user=user)
        else:
            dupRecoed = AttendanceLogs.objects.filter(login_time__gte=today,user=user)        
        if not dupRecoed:
            return Response({"message":"loogin first"},status=403)
        if dupRecoed:
            in_time = dupRecoed.first().login_time
            time_diff = logout_time-in_time
            dupRecoed.update(logout_time=logout_time,work_hours=time_diff)
        dateStr = str(time_diff).split(":")
        if int(dateStr[0]) >= 9:
            dupRecoed.update(is_present=True,work_hours=time_diff)
        return Response({"message":"successfully logged out","loggoff_time":logout_time},status=200)

class UserSessionLogin(ViewSet):
    def create(self,request):
        rd = request.data
        email = rd.get("email")
        password = rd.get("password")
        user = User.objects.filter(email=email,password=password).first()
        if user:
            refresh = RefreshToken.for_user(user)
            res = {
                "refresh":str(refresh),
                "access":str(refresh.access_token)
            }
            return Response(res,status=200)
        else:
            return Response({"message":"Login Failed"},status=401)
        

class LeaveDetails(ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def list(self,request):    
        email = request.GET.get("email_id")
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"message":"not found"},status=401)
        today = timezone.localtime()+timedelta(days=1)
        today_str = str(today)
        today_str = today_str.split(" ")[0]
        bd_holidays = ["2023-09-05"]
        bd_cal = numpy.busdaycalendar(weekmask="1111100", holidays=bd_holidays)
        count = numpy.busday_count('2023-09-01',today_str,busdaycal=bd_cal)
        present_count = AttendanceLogs.objects.filter(user=user,is_present=True).values("is_present").all()
        return Response({"present_days":len(present_count),"absent_days":count-len(present_count)},status=200)

class AttendanceDetails(ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def list(self,request):
        currentDay = datetime.now().day
        email = request.GET.get("email_id")
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"message":"User not found"},status=401)
        data = AttendanceLogs.objects.filter(user=user).order_by("created_at").values().all()
        
        if data:
            return Response(data,status=200)
        else:
            return Response({"message":"no data"},status=204)
        
class EventDetails(ViewSet):
    def create(self,request):
        name = request.data.get("name")
        date = request.data.get("date")
        event_type = request.data.get("eventType")
        shift = request.data.get("shift")
        date = datetime.strptime(date, '%Y-%m-%d').date()
        check_dup = Events.objects.filter(date=date,event_type=event_type,name=name)
        if check_dup:
            return Response({"message":"already exists"},status=400)
        res = Events.objects.create(name=name,date=date,event_type=event_type,shift=shift)
        if res:
            return Response({"message":"created successfully"},status=200)
        else:
            return Response ({"message":"something wrong"},status=500)
        
    def list(self,request):
        res = Events.objects.values()
        if res:
            return Response(res,status=200)
        else:
            return Response([],status=204)
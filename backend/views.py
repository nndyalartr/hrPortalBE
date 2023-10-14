from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from corehr.models import UserBasicDetails,AttendanceLogs,Events,Leaveapprovals
from django.utils import timezone
from datetime import timedelta,datetime
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt import authentication
from users_api.models import User
from .bussiness_logic import AttendanceRelatedLogics
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
        result = UserBasicDetails.objects.filter(email_id=email).values().first()
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
        email = req_body["user_email"]        
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"message":"user not found"},status=401)  
        create_all_logs = AttendanceLogs.objects.filter(login_time__month=today.month,user=user).exclude(leave_details="")
        leave_days = AttendanceLogs.objects.filter(created_at__month=today.month,user=user)
        holidays = Events.objects.filter(event_type="Holiday",date__month=today.month)
        print(holidays)
        existing_days = []
        if len(leave_days):
            for days in leave_days:
                existing_days.append(days.created_at)
        if not create_all_logs:
            for x in range(calendar.monthrange(today.year, today.month)[1]):
                da_te=datetime(today.year, today.month, x+1)
                week =da_te.strftime('%A')
                week_off = ['Saturday','Sunday']
                if datetime.date(da_te) not in existing_days:
                    if x+1 == today.day:
                        if week in week_off:
                            AttendanceLogs.objects.create(login_time=today,user=user,created_at=da_te,week_day=week,remarks="Week-Off")
                        else:
                            AttendanceLogs.objects.create(login_time=today,user=user,created_at=da_te,week_day=week)
                    else:
                        if week in week_off:
                            AttendanceLogs.objects.create(user=user,created_at=da_te,week_day=week,remarks="Week-Off")
                        else:
                            AttendanceLogs.objects.create(user=user,created_at=da_te,week_day=week)
                # elif datetime.date(da_te) in existing_days:
                #     AttendanceLogs.objects.filter(created_at=da_te).update(login_time=today)
            for holiday in holidays:
                holiday_update = AttendanceLogs.objects.filter(created_at=holiday.date).update(remarks="Holiday")

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
        # return Response({"message":"Something Went Wrong"},status=500)
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
        if int(dateStr[0]) >= 8:
            dupRecoed.update(is_present=True,work_hours=time_diff,remarks="present")
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
                "access":str(refresh.access_token),
                "role":user.role,
                "name":user.first_name
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
        today = timezone.localtime()
        email = request.GET.get("email_id")
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"message":"User not found"},status=401)
        data = AttendanceLogs.objects.filter(user=user,created_at__lte=today).order_by("created_at").values().all()
        
        if data:
            return Response(data,status=200)
        else:
            return Response({"message":"no data"},status=204)
        
class EventDetails(ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
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
        
class LeaveApply(ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def create(self,request):
        req_user = request.data.get("email")
        leave_details = request.data.get("leaves")
        leave_type = request.data.get("leave_type")
        leave_reason = request.data.get("leave_reason")
        user_query = User.objects.filter(email=req_user).prefetch_related("leader_name").first()
        result = Leaveapprovals.objects.create(leave_details=leave_details,leave_type=leave_type,leave_reason=leave_reason,applied_by=user_query,approver=user_query.leader_name,status="pending")
        return Response({"message":"Suucessfully applied leave"},status=200)
    
    def list(self,request):
        req_user = request.GET.get("email")
        user = User.objects.filter(email=req_user).prefetch_related("leader_name").first()
        context = []
        res = Leaveapprovals.objects.filter(applied_by=user).prefetch_related("approver").values()
        for item in res:
            data_dict = {}
            no_of_leaves = 0
            date_strings = []            
            for leave in item["leave_details"]:                
                date_strings.append(leave['date'])
                if leave['session'] == 'fullDay':
                    no_of_leaves += 1
                else:
                    no_of_leaves += 0.5

            date_objects = [datetime.strptime(date_str, '%Y-%m-%d').date() for date_str in date_strings]
            data_dict['id'] = item['id']
            data_dict['reason'] = item['leave_reason']
            data_dict['type'] = item['leave_type']
            data_dict["leaves"] = item['leave_details']
            data_dict['status'] = item['status']
            data_dict['leaveCount'] = no_of_leaves
            data_dict['approver'] = user.leader_name.first_name
            data_dict['startDate'] = min(date_objects)
            data_dict['endDate'] = max(date_objects)
            context.append(data_dict)
        return Response(context,status=200)
    
class LeaveApproval(ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def patch(self,request):
        id = request.data.get("id")
        action = request.data.get("action")
        res = Leaveapprovals.objects.filter(id=id).update(status=action)
        leave_obj = Leaveapprovals.objects.get(id=id)
        for leave in leave_obj.leave_details:
            pp = AttendanceLogs.objects.filter(user=leave_obj.applied_by,created_at = datetime.strptime(leave['date'], '%Y-%m-%d').date())
            if pp:
                pp.update(leave_details=leave['session'])
                if leave['session'] == 'fullDay':
                    pp.update(remarks = "leave")
                else:
                    pp.update(remarks = "H/A")
            else:
                leave_day = datetime.strptime(leave['date'], '%Y-%m-%d').date()
                da_te=datetime(leave_day.year, leave_day.month, leave_day.day)
                week =da_te.strftime('%A')
                if leave['session'] == 'fullDay':
                    AttendanceLogs.objects.create(user=leave_obj.applied_by,created_at=da_te,week_day=week,leave_details=leave['session'],remarks = "leave")                    
                else:
                    AttendanceLogs.objects.create(user=leave_obj.applied_by,created_at=da_te,week_day=week,leave_details=leave['session'],remarks = "H/A")
        if res  == 1:
            return Response({"message":"approved leave request"},status=200)
        else:
            return Response({"message":"something went wrong"},status=500)
    def list(self,request):
        email = request.GET.get("email")
        user = User.objects.filter(email=email).first()
        my_list = Leaveapprovals.objects.filter(approver=user,status="pending").prefetch_related("applied_by")
        context = []
        for item in my_list:
            no_of_leaves = 0
            date_strings = [] 
            start_session =''
            end_session =''           
            for leave in item.leave_details:
                date_strings.append(leave['date'])              
                if leave['session'] == 'fullDay':
                    no_of_leaves += 1
                else:
                    no_of_leaves += 0.5
            date_objects = [datetime.strptime(date_str, '%Y-%m-%d').date() for date_str in date_strings]
            for leave in item.leave_details:
                if str(min(date_objects)) == str(leave['date']):
                    start_session = leave['session']
                elif str(max(date_objects)) == str(leave['date']):
                    end_session = leave['session']
            data_dict ={}
            data_dict['id'] = item.id
            data_dict["applied_by"] = item.applied_by.first_name
            data_dict["leave_count"] = no_of_leaves
            data_dict['startDate'] = min(date_objects)
            data_dict['start_session'] = start_session
            data_dict['endDate'] = max(date_objects)
            data_dict['end_session'] = end_session
            data_dict['reason'] = item.leave_reason
            context.append(data_dict)
        if context:
            return Response(context,status=200)
        else:
            return Response([],status=204)
 
class AttendanceRegularize(ViewSet,AttendanceRelatedLogics):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def list(self,request):
        result = self.attendance_regularize_det(request)
        return Response(result['absent_logs'],status=result["status"])
    
class ApplyAttendanceRegularize(ViewSet,AttendanceRelatedLogics):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def create(self,request):
        result = self.attendance_regularize_apply(request)
        return Response(result,status=result['status'])
    
class ListAttendanceRegularize(ViewSet,AttendanceRelatedLogics):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def list(self,request):
        result = self.attendance_regularize_list(request)
        return Response(result['data'],status=result['status'])

class ApproveAttendanceRegularize(ViewSet,AttendanceRelatedLogics):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def patch(self,request):
        result = self.attendance_regularize_approve_final(request)
        return Response(result,status=result['status'])
    def list(self,request):
        result = self.attendance_regularize_approve(request)
        return Response(result['data'],status=result['status'])
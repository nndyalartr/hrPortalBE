from datetime import timedelta,datetime
from django.utils import timezone
from corehr.models import UserBasicDetails,AttendanceLogs,Events,Leaveapprovals,AttendanceRegularization
from users_api.models import User

class AttendanceRelatedLogics():
    def attendance_regularize_det(self,request):
        user_id = request.GET.get("id")
        try:
            user = User.objects.get(email=user_id)
        except:
            return({"absent_logs":[],"message":"User not found","status":400})
        today = timezone.localtime()
        response_logs = AttendanceLogs.objects.filter(user=user,is_present=False,created_at__lte=today,created_at__month__gte = today.month,remarks="").values()
        if response_logs:
            return({"absent_logs":response_logs,"status":200})
        else:
            return({"absent_logs":[],"status":204})
        
    def attendance_regularize_apply(self,request):
        attendance_id = request.data.get("attendance_id")
        login_time = request.data.get("login_time")
        date = request.data.get("date")
        logout_time = request.data.get("logout_time")
        reason = request.data.get("reason")
        user_email = request.data.get("user_email")
        user = User.objects.get(email = user_email)        
        result = AttendanceRegularization.objects.create(date=date,attendance_id=attendance_id,login_time=login_time,logout_time=logout_time,reason=reason,status="pending",applied_by=user,approver=user.leader_name)
        AttendanceLogs.objects.filter(id=attendance_id).update(remarks="Attendance Regularization pending")
        if result:
            return({"message":"Successfully generated request","status":200})
        else:
            return ({"message":"something went wrong","status":400})
        
    def attendance_regularize_list(self,request):
        id = request.GET.get("id")
        user = User.objects.get(email = id)        
        result = AttendanceRegularization.objects.filter(applied_by = user)
        if result:
            array = []
            for res in result: 
                dict__ = {}
                dict__["id"] = res.id
                dict__["date"] = res.date
                dict__["login_time"] = res.login_time
                dict__["logout_time"] = res.logout_time
                dict__["working_hours"] = res.working_hours
                dict__["reason"] = res.reason
                dict__["status"] = res.status
                dict__["approver"] = res.approver.first_name
                array.append(dict__)
            return({"data":array,"status":200})
        else:
            return({"data":[],"status":204})
        
    def attendance_regularize_approve(self,request):
        id = request.GET.get("id")
        user = User.objects.get(email=id)        
        result = AttendanceRegularization.objects.filter(approver=user,status="pending")
        if result:
            array = []
            for res in result: 
                dict__ = {}
                dict__["id"] = res.id
                dict__["date"] = res.date
                dict__["attendance_id"] = res.attendance_id
                dict__["login_time"] = res.login_time
                dict__["logout_time"] = res.logout_time
                dict__["working_hours"] = res.working_hours
                dict__["reason"] = res.reason
                dict__["status"] = res.status
                dict__["applied_by"] = res.applied_by.first_name
                array.append(dict__)
            return({"data":array,"status":200})
        else:
            return({"data":[],"status":204})
        
    def attendance_regularize_approve_final(self,request):
        id = request.data.get("id")
        action = request.data.get("action")
        if action == "approved":
            result =  AttendanceRegularization.objects.get(id = id)
            result.status = "approved"
            result.save()
            AttendanceLogs.objects.filter(id=result.attendance_id).update(remarks="Regularized",is_present=True)
            if result:
                return({"message":"Successfully Updated","status":200})
            else:
                return({"message":"something Wnt Wrong","status":500})

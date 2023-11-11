from datetime import timedelta,datetime
import json
from django.utils import timezone
from corehr.models import UserBasicDetails,AttendanceLogs,Events,Leaveapprovals,AttendanceRegularization,Resignation
from users_api.models import User
class UserRelatedLogics():
    def create_user(self,request):
        req_dict=json.loads(request.body)
        try:
            user = User.objects.create(
                email = req_dict.get("email"),
                password = "Welcome@123",
                first_name=req_dict.get("first_name"),
                last_name=req_dict.get("last_name"),
                username = req_dict.get("email")
            )
            permanent_address=req_dict.get("permanent_address")
            res = UserBasicDetails.objects.create(emp_no=req_dict.get("emp_id"),
                            emp_name=req_dict.get("emp_name"),
                            first_name=req_dict.get("first_name"),
                            last_name=req_dict.get("last_name"),
                            email_id=req_dict.get("email"),
                            father_name=req_dict.get("father_name"),
                            name_as_aadhar=req_dict.get("name_as_aadhar"),
                            emergency_contact_name=req_dict.get("emergency_contact_name"),
                            emergency_contact=req_dict.get("emergency_contact"),
                            aadhar_number=req_dict.get("aadhar_number"),
                            mobile_number=req_dict.get("mobile_number"),
                            designation=req_dict.get("designation"),
                            location=req_dict.get("location"),
                            department=req_dict.get("department"),
                            permanent_address=permanent_address,
                            temporary_address=req_dict.get("temporary_address",permanent_address),
                            date_of_joining=req_dict.get("date_of_joining"),
                            date_of_birth=req_dict.get("date_of_birth"),
                            gender=req_dict.get("gender",""),
                            ctc=req_dict.get("ctc"),
                            pan=req_dict.get("pan",""),
                            maritial_status=req_dict.get("maritial_status",""),
                            is_pf_eligible=True,
                            is_esi_eligible=req_dict.get("is_esi_eligible"),
                            user=user
                                )
            return({"message":"Successfully created user","status":200})
        except Exception as e:
            return({"message":"e","status":400})
            
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
            
class ResignationRelatedLogics(object):
    def apply_resignation(self,request):
        req_data = request.data
        print(req_data)
        user = User.objects.get(email=req_data['user_email'])
        res = Resignation.objects.create(resignation_date=req_data['resignation_date'],
                                         personal_phone_no=req_data['personal_phone_no'],
                                         personal_mail_id=req_data['personal_mail_id'],
                                         resignation_reason=req_data['resignation_reason'],
                                         status="pending",
                                         applied_by=user,
                                         approver=user.leader_name
                                         )
        if res:
            return({"message":"Resignation Submitted Successfully","status":200})
        else:
            return({"message":"something went wrong","status":500})
        
    def get_all_resignations(self,request):
        id = request.GET.get("user_email")
        user = User.objects.get(email=id)        
        result = Resignation.objects.filter(approver=user,status="pending")
        if result:
            array = []
            for res in result: 
                dict__ = {}
                dict__["id"] = res.id
                dict__["resignation_date"] = res.resignation_date
                dict__["resignation_reason"] = res.resignation_reason
                dict__["status"] = res.status
                dict__["applied_by"] = res.applied_by.first_name
                array.append(dict__)
            return({"data":array,"status":200})
        else:
            return({"data":[],"status":204})
    def get_resignation_status(self,request):
        id = request.GET.get("user_email")
        user = User.objects.get(email=id)        
        result = Resignation.objects.filter(applied_by=user)
        if result:
            array = []
            for res in result: 
                dict__ = {}
                dict__["id"] = res.id
                dict__["resignation_date"] = res.resignation_date
                dict__["resignation_reason"] = res.resignation_reason
                dict__["status"] = res.status,
                dict__['exit_date'] = res.date_of_exit
                dict__["approver"] = res.approver.first_name
                array.append(dict__)
            return({"data":array,"status":200})
        else:
            return({"data":[],"status":204})
        
    def approve_resignations(self,request):
        id = request.data["user_email"]
        record_id = request.data['record_id']
        status = request.data['status']
        exit_date = request.data['exit_date']        
        if status == 'Approved' and exit_date:
            date = datetime.strptime(exit_date, '%Y-%m-%d').date()
            Resignation.objects.filter(id=record_id).update(status=status,date_of_exit=date)
        elif status == 'Approved' and not exit_date:
            return ({"message":"Please select date","status":400})
        elif status == 'Rejected':
            Resignation.objects.filter(id=record_id).update(status=status)
        else:
            pass
        user = User.objects.get(email=id)        
        result = Resignation.objects.filter(approver=user,status="pending")
        if result:
            array = []
            for res in result: 
                dict__ = {}
                dict__["id"] = res.id
                dict__["resignation_date"] = res.resignation_date
                dict__["resignation_reason"] = res.resignation_reason
                dict__["status"] = res.status
                dict__["applied_by"] = res.applied_by.first_name
                array.append(dict__)
            return({"data":array,"status":200})
        else:
            return({"data":[],"status":204})

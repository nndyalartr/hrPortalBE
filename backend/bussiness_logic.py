from datetime import timedelta,datetime
import json
from django.utils import timezone
from corehr.models import UserBasicDetails,AttendanceLogs,Events,Leaveapprovals,AttendanceRegularization,Resignation
from users_api.models import User
import pandas as pd

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
        
class AttendanceReports(object):
    def get_all_attendance_reports(self,from_date,to_date):
        from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
        to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
        all_users = User.objects.all()
        attendance_logs = []
        for user in all_users:
            res = AttendanceLogs.objects.filter(user=user,created_at__gte =from_date,created_at__lte = to_date).values('is_present','work_hours','leave_details','remarks','created_at','week_day')
            data_dict = {
                "user_name":user.first_name,
                "attendance_logs":res
            }
            attendance_logs.append(data_dict)
        rows = []
        for record in attendance_logs:
            present_count = 0
            leave_count = 0
            abscent_count = 0
            user_name = record["user_name"]
            
            for log in record['attendance_logs']:
                date = log["created_at"]
                is_present = log["is_present"]
                work_hours = log["work_hours"]
                leave_details = log["leave_details"]
                remarks = log["remarks"] 
                week_days = log["week_day"]
                week_list = ["Sunday","Saturday"] 
                if is_present:
                    present_count += 1
                elif not is_present and leave_details == "fullDay":
                    leave_count += 1
                elif not is_present and (leave_details == "s-1" or leave_details == "s-2"):
                    leave_count += .5
                elif  leave_details is None and not is_present and week_days not in week_list:
                    abscent_count += 1  
            user_logs = {"User Name": user_name,"Present Days":present_count,"Leave Days":leave_count,"Abscent Days":abscent_count}   
            for log in record["attendance_logs"]:
                date = log["created_at"]
                is_present = log["is_present"]
                leave_details = log["leave_details"]
                remarks = log["remarks"] 
                            
                final_remarks = ""                
                if remarks:
                    final_remarks = remarks
                if is_present:
                    final_remarks = "present"
                if not remarks and not is_present:
                    final_remarks = "Abscent"
                elif not log :
                    final_remarks = "N/A"
                user_logs[date] = final_remarks
            
            rows.append(user_logs)

        # Create a DataFrame
        

        return(rows)
    
class UsersBulkUploadLogics(object):
    def create_users_bulk_upload(self,request):
        csv_users_data = pd.read_csv(request.FILES['users'])
        csv_users_data.rename(
            columns = {
                list(csv_users_data)[0]:"emp_id",
                list(csv_users_data)[1]:"first_name",
                list(csv_users_data)[2]:"last_name",
                list(csv_users_data)[3]:"date_of_birth",
                list(csv_users_data)[4]:"gender",
                list(csv_users_data)[5]:"blood_group",
                list(csv_users_data)[6]:"father_name",
                list(csv_users_data)[7]:"maritial_status",
                list(csv_users_data)[8]:"mobile_number",
                list(csv_users_data)[9]:"date_of_joining",
                list(csv_users_data)[10]:"department",
                list(csv_users_data)[11]:"designation",
                list(csv_users_data)[12]:"email",
                list(csv_users_data)[13]:"emergency_contact",
                list(csv_users_data)[14]:"emergency_contact_name",
                list(csv_users_data)[15]:"permanent_address",
                list(csv_users_data)[16]:"temporary_address",
                list(csv_users_data)[17]:"aadhar_number",
                list(csv_users_data)[18]:"project_name",
                list(csv_users_data)[19]:"role",
                list(csv_users_data)[20]:"ctc",
                list(csv_users_data)[21]:"pan",
                list(csv_users_data)[22]:"is_esi_eligible",  
                list(csv_users_data)[23]:"name_as_aadhar"              
            },
            inplace=True
        )
        for req_dict in csv_users_data.iloc:
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
                                emp_name=req_dict.get("first_name")+req_dict.get("last_name"),
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
                                location=req_dict.get("location",""),
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
                                blood_group=req_dict.get("blood_group"),
                                project_name=req_dict.get("project_name"),
                                role=req_dict.get("role"),
                                user=user
                                    )
            except Exception as e:
                return({"message":str(e),"status":400})
        
        return ({"message":f"success fully created {len(csv_users_data)} users","status":200})
    
class UserDataLogics(object):
    def get_all_user_details(self,request):
        details = []
        result = UserBasicDetails.objects.all()
        for item in result:
            data_dict = {}
            data_dict["email_id"] = item.email_id,
            data_dict["emp_no"] = item.emp_no,
            data_dict["emp_name"] = item.emp_name
            details.append(data_dict)
        return details
    

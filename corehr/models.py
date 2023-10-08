from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils import timezone
from django.conf import settings
# Create your models here.
class UserBasicDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    emp_no=models.CharField()
    emp_name = models.TextField()
    first_name=models.TextField()
    last_name=models.TextField()
    email_id=models.EmailField()
    father_name=models.TextField(null=True)
    name_as_aadhar=models.TextField()
    emergency_contact_name=models.TextField(null=True)
    emergency_contact=models.TextField()
    aadhar_number=models.IntegerField()
    mobile_number=models.TextField()
    designation=models.TextField()
    location=models.TextField()
    department=models.TextField(null=True)
    permanent_address=models.TextField(null=True)
    temporary_address=models.TextField(null=True)
    date_of_joining=models.DateField()
    date_of_birth=models.DateField()
    gender=models.CharField()
    pan=models.TextField(null=True)
    maritial_status=models.TextField(null=True)
    ctc=models.IntegerField(null=True)
    is_pf_eligible=models.BooleanField(null=True)
    is_esi_eligible=models.BooleanField(null=True)
    is_night_shift=models.BooleanField(default=False,null=False)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True)



class AttendanceLogs(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,max_length=500,primary_key=True,editable=False
    )
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True)
    login_time=models.DateTimeField(null=True)
    logout_time=models.DateTimeField(null=True)
    is_present=models.BooleanField(default=False,null=True)
    leave_details= models.TextField(null=True)
    work_hours = models.TextField(null=True)
    created_at=models.DateField(null=True)
    week_day=models.TextField(null=True)


class Events(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,max_length=500,primary_key=True,editable=False
    )
    name = models.TextField()
    date = models.DateField()
    shift = models.TextField()
    event_type = models.TextField()

class Leaveapprovals(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,max_length=500,primary_key=True,editable=False
    )
    leave_type = models.TextField(null=False,default="")
    leave_reason = models.TextField(null=False,default="")
    applied_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,related_name="applied_by")
    approver = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,related_name="approver")
    leave_details = models.JSONField()
    status = models.TextField()
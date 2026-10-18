from django.db import models
from django.conf import settings
class AttendanceRecord(models.Model):
 student=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='attendance_records'); class_name=models.CharField(max_length=60,blank=True); date=models.DateField(); status=models.CharField(max_length=10,choices=[('PRESENT','Present'),('ABSENT','Absent'),('LATE','Late'),('LEAVE','Leave')]); marked_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='attendance_marked'); remarks=models.CharField(max_length=255,blank=True)
 class Meta: unique_together=('student','date'); ordering=['-date']
class LeaveRequest(models.Model):
 student=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='leave_requests'); start_date=models.DateField(); end_date=models.DateField(); reason=models.TextField(); status=models.CharField(max_length=12,default='PENDING'); reviewed_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,blank=True,null=True,related_name='leave_reviews'); created_at=models.DateTimeField(auto_now_add=True)

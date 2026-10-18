from django.db import models
from django.conf import settings
class Notification(models.Model):
 recipient=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='academix_notifications'); title=models.CharField(max_length=160); message=models.TextField(); url=models.CharField(max_length=255,blank=True); is_read=models.BooleanField(default=False); created_at=models.DateTimeField(auto_now_add=True)
 class Meta: ordering=['-created_at']
class Announcement(models.Model):
 title=models.CharField(max_length=180); body=models.TextField(); audience_roles=models.JSONField(default=list,blank=True); class_name=models.CharField(max_length=60,blank=True); created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT); published_at=models.DateTimeField(blank=True,null=True); created_at=models.DateTimeField(auto_now_add=True)

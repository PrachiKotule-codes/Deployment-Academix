from django.db import models
from django.conf import settings
class AuditLog(models.Model):
 actor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True); action=models.CharField(max_length=120); object_type=models.CharField(max_length=120,blank=True); object_id=models.CharField(max_length=80,blank=True); details=models.JSONField(default=dict,blank=True); ip_address=models.GenericIPAddressField(blank=True,null=True); created_at=models.DateTimeField(auto_now_add=True)
 class Meta: ordering=['-created_at']

from django.db import models
from django.conf import settings
class UserProfile(models.Model):
 class Role(models.TextChoices):
  ADMIN='ADMIN','Admin'; TEACHER='TEACHER','Teacher'; STUDENT='STUDENT','Student'; PARENT='PARENT','Parent'
 user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='academix_profile')
 role=models.CharField(max_length=12,choices=Role.choices,default=Role.STUDENT)
 display_name=models.CharField(max_length=120,blank=True); phone=models.CharField(max_length=30,blank=True)
 class_name=models.CharField(max_length=60,blank=True); division=models.CharField(max_length=30,blank=True); academic_year=models.CharField(max_length=20,default='2026-2027')
 linked_students=models.ManyToManyField(settings.AUTH_USER_MODEL,blank=True,related_name='linked_parents')
 def __str__(self): return f'{self.user.username} ({self.role})'

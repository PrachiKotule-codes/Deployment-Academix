from django.db import models
from django.conf import settings
class Subject(models.Model):
 name=models.CharField(max_length=120,unique=True); code=models.CharField(max_length=30,blank=True); description=models.TextField(blank=True)
 def __str__(self): return self.name
class Course(models.Model):
 title=models.CharField(max_length=160); subject=models.ForeignKey(Subject,on_delete=models.PROTECT,related_name='courses')
 description=models.TextField(blank=True); module_name=models.CharField(max_length=120,blank=True); teacher=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='teaching_courses')
 class_name=models.CharField(max_length=60,blank=True); division=models.CharField(max_length=30,blank=True); academic_year=models.CharField(max_length=20,default='2026-2027')
 thumbnail=models.ImageField(upload_to='thumbnails/',blank=True,null=True); is_published=models.BooleanField(default=False); created_at=models.DateTimeField(auto_now_add=True)
 def __str__(self): return self.title

from django.db import models
from django.conf import settings
from academics.models import Course
class Test(models.Model):
 course=models.ForeignKey(Course,on_delete=models.CASCADE,related_name='tests'); title=models.CharField(max_length=180); instructions=models.TextField(blank=True); duration_minutes=models.PositiveIntegerField(default=30); total_marks=models.PositiveIntegerField(default=100); starts_at=models.DateTimeField(blank=True,null=True); ends_at=models.DateTimeField(blank=True,null=True); status=models.CharField(max_length=12,default='DRAFT'); created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
 def __str__(self): return self.title
class Question(models.Model):
 test=models.ForeignKey(Test,on_delete=models.CASCADE,related_name='questions'); prompt=models.TextField(); kind=models.CharField(max_length=8,default='MCQ'); options=models.JSONField(default=list,blank=True); correct_answer=models.TextField(blank=True); marks=models.PositiveIntegerField(default=1); order=models.PositiveIntegerField(default=1)
class TestAttempt(models.Model):
 test=models.ForeignKey(Test,on_delete=models.CASCADE,related_name='attempts'); student=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='test_attempts'); started_at=models.DateTimeField(auto_now_add=True); submitted_at=models.DateTimeField(blank=True,null=True); score=models.DecimalField(max_digits=7,decimal_places=2,blank=True,null=True); is_submitted=models.BooleanField(default=False)
 class Meta: unique_together=('test','student')

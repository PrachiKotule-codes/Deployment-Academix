from django.db import models
from django.conf import settings
from academics.models import Course
class Homework(models.Model):
 course=models.ForeignKey(Course,on_delete=models.CASCADE,related_name='homework'); title=models.CharField(max_length=180); instructions=models.TextField(); due_at=models.DateTimeField(); created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT); created_at=models.DateTimeField(auto_now_add=True); is_published=models.BooleanField(default=False)
 def __str__(self): return self.title
class HomeworkSubmission(models.Model):
 homework=models.ForeignKey(Homework,on_delete=models.CASCADE,related_name='submissions'); student=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='homework_submissions'); answer_text=models.TextField(blank=True); attachment=models.FileField(upload_to='homework_submissions/',blank=True,null=True); status=models.CharField(max_length=12,default='SUBMITTED'); marks=models.DecimalField(max_digits=6,decimal_places=2,blank=True,null=True); feedback=models.TextField(blank=True); submitted_at=models.DateTimeField(auto_now_add=True)
 class Meta: unique_together=('homework','student')

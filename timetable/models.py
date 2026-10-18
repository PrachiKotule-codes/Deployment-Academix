from django.db import models
from academics.models import Subject
class TimetableEntry(models.Model):
 class_name=models.CharField(max_length=60); division=models.CharField(max_length=30,blank=True); subject=models.ForeignKey(Subject,on_delete=models.PROTECT); teacher_name=models.CharField(max_length=120,blank=True); weekday=models.PositiveSmallIntegerField(); start_time=models.TimeField(); end_time=models.TimeField(); room=models.CharField(max_length=80,blank=True); academic_year=models.CharField(max_length=20,default='2026-2027')
 @property
 def weekday_label(self): return ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'][self.weekday] if 0 <= self.weekday <= 6 else '—'
 class Meta: ordering=['weekday','start_time']

from django.db import models
from django.conf import settings
from academics.models import Course
class Lesson(models.Model):
 class Status(models.TextChoices): DRAFT='DRAFT','Draft'; PUBLISHED='PUBLISHED','Published'
 course=models.ForeignKey(Course,on_delete=models.CASCADE,related_name='lessons'); title=models.CharField(max_length=180); description=models.TextField(blank=True); section_title=models.CharField(max_length=120,blank=True); quick_recap=models.TextField(blank=True); mindmap_url=models.URLField(blank=True)
 order=models.PositiveIntegerField(default=1); video_url=models.URLField(blank=True); video_file=models.FileField(upload_to='lesson_videos/',blank=True,null=True); thumbnail=models.ImageField(upload_to='lesson_thumbnails/',blank=True,null=True)
 duration_minutes=models.PositiveIntegerField(default=0); status=models.CharField(max_length=12,choices=Status.choices,default=Status.DRAFT); created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT); created_at=models.DateTimeField(auto_now_add=True)
 class Meta: ordering=['order','id']
 def __str__(self): return self.title
 @property
 def embed_url(self):
  url=(self.video_url or '').strip()
  if 'youtu.be/' in url: return 'https://www.youtube.com/embed/'+url.split('youtu.be/')[-1].split('?')[0]
  if 'youtube.com/watch' in url and 'v=' in url: return 'https://www.youtube.com/embed/'+url.split('v=')[-1].split('&')[0]
  if 'youtube.com/shorts/' in url: return 'https://www.youtube.com/embed/'+url.split('shorts/')[-1].split('?')[0]
  if 'drive.google.com/file/d/' in url: return 'https://drive.google.com/file/d/'+url.split('/file/d/')[-1].split('/')[0]+'/preview'
  return url
class StudyMaterial(models.Model):
 lesson=models.ForeignKey(Lesson,on_delete=models.CASCADE,related_name='materials'); title=models.CharField(max_length=160); file=models.FileField(upload_to='study_materials/',blank=True,null=True); external_url=models.URLField(blank=True)
class LessonProgress(models.Model):
 lesson=models.ForeignKey(Lesson,on_delete=models.CASCADE,related_name='progress_records'); student=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='lesson_progress'); completed=models.BooleanField(default=False); last_position_seconds=models.PositiveIntegerField(default=0); updated_at=models.DateTimeField(auto_now=True)
 class Meta: unique_together=('lesson','student')
 def __str__(self): return f'{self.student} · {self.lesson}'

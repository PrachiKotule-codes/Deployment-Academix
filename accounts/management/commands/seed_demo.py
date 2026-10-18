from datetime import timedelta, time as dt_time
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from accounts.models import UserProfile
from academics.models import Subject, Course
from lessons.models import Lesson, StudyMaterial, LessonProgress
from homework.models import Homework, HomeworkSubmission
from attendance.models import AttendanceRecord
from timetable.models import TimetableEntry
from fees.models import FeeRecord, PaymentRecord
from exams.models import Test
from notifications.models import Notification, Announcement

User = get_user_model()

class Command(BaseCommand):
    help = 'Create or refresh local demo accounts and sample academic data.'
    def handle(self, *args, **kwargs):
        # These local-demo passwords are deliberately reset on each seed run so students can log in reliably.
        primary = {}
        def make_user(username, first_name, last_name, role, password, class_name='', division='A', email=None):
            user, _ = User.objects.get_or_create(username=username, defaults={
                'first_name': first_name, 'last_name': last_name,
                'email': email or f'{username}@academix.local',
            })
            user.first_name=first_name; user.last_name=last_name
            user.email=email or f'{username}@academix.local'
            user.set_password(password)
            if role == 'ADMIN': user.is_staff=True
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role=role; profile.display_name=user.get_full_name()
            profile.class_name=class_name if role=='STUDENT' else ''
            profile.division=division if role=='STUDENT' else ''
            profile.academic_year='2026-2027'; profile.save()
            return user

        admin = make_user('admin_demo','Academix','Admin','ADMIN','Admin123',email='admin@academix.local')
        teachers=[]
        teacher_specs=[('teacher_demo','Anjali','Deshmukh','Teacher123'),('teacher2','Rahul','Patil','Teacher123'),('teacher3','Neha','Shinde','Teacher123'),('teacher4','Amit','Kulkarni','Teacher123'),('teacher5','Sneha','Joshi','Teacher123')]
        for spec in teacher_specs:
            teachers.append(make_user(*spec[:3],'TEACHER',spec[3],email=f'{spec[0]}@academix.local'))
        students=[]
        student_specs=[('student_demo','Riya','Sharma','Student123')]
        student_specs += [(f'student{i}', name, surname, 'Student123') for i,(name,surname) in enumerate([
            ('Aarav','Patel'),('Anaya','Shah'),('Ishaan','Joshi'),('Aditi','Desai'),('Vivaan','More'),('Sara','Kulkarni'),('Kabir','Jadhav'),('Myra','Pawar'),('Arjun','Bhosale')],start=2)]
        for username, first, last, pw in student_specs:
            students.append(make_user(username,first,last,'STUDENT',pw,'Class 10','A',f'{username}@academix.local'))
        parents=[]
        parent_specs=[('parent_demo','Meena','Sharma','Parent123')]
        parent_specs += [(f'parent{i}', f'Parent{i}', 'Family', 'Parent123') for i in range(2,11)]
        for username,first,last,pw in parent_specs:
            parents.append(make_user(username,first,last,'PARENT',pw,email=f'{username}@academix.local'))
        for parent, student in zip(parents, students):
            parent.academix_profile.linked_students.add(student)

        subject_names=['Mathematics','Science','English','Social Studies','Computer Science']
        courses=[]
        for i, subject_name in enumerate(subject_names):
            subject,_=Subject.objects.get_or_create(name=subject_name,defaults={'code':f'SUB{i+1:02d}','description':f'{subject_name} course content for Class 10.'})
            teacher=teachers[i]
            course,_=Course.objects.get_or_create(title=f'Class 10 {subject_name}',subject=subject,teacher=teacher,defaults={
                'description':f'Learn {subject_name} through structured lessons, study notes and practice activities.',
                'module_name':'Term 1','class_name':'Class 10','division':'A','academic_year':'2026-2027','is_published':True,
            })
            course.description=f'Learn {subject_name} through structured lessons, study notes and practice activities.'
            course.module_name='Term 1'; course.class_name='Class 10'; course.division='A'; course.academic_year='2026-2027'; course.is_published=True; course.save()
            courses.append(course)
            lesson_titles=[('Core concepts','Build a foundation by understanding the key ideas.'),('Worked examples','Review worked examples and practice applying the concept.'),('Quick revision','Review the most important points before an assessment.')]
            for order,(title,recap) in enumerate(lesson_titles,1):
                lesson,_=Lesson.objects.get_or_create(course=course,title=f'{subject_name}: {title}',defaults={
                    'description':f'{title} in {subject_name}. Replace this demo description and add your approved lesson video or file.',
                    'section_title':'Term 1 · Fundamentals','quick_recap':recap,'order':order,'duration_minutes':12+order*3,
                    'status':'PUBLISHED','created_by':teacher,
                })
                lesson.status='PUBLISHED'; lesson.save(update_fields=['status'])

        math_course=courses[0]
        hw,_=Homework.objects.get_or_create(course=math_course,title='Practice: Number systems',created_by=teachers[0],defaults={
            'instructions':'Solve the assigned questions and show your working. You may write your answer in the text box or attach a file.',
            'due_at':timezone.now()+timedelta(days=3),'is_published':True,
        })
        hw.is_published=True; hw.save(update_fields=['is_published'])
        for student in students[:3]:
            sub,_=HomeworkSubmission.objects.get_or_create(homework=hw,student=student,defaults={'answer_text':'Sample submitted work for demonstration.','status':'SUBMITTED'})
            if student==students[0]:
                sub.status='REVIEWED';sub.marks=8;sub.feedback='Good effort. Show each calculation step clearly.';sub.save()
        now=timezone.localdate()
        for student_index,student in enumerate(students):
            for offset in range(1,6):
                day=now-timedelta(days=offset)
                status='ABSENT' if (student_index==0 and offset==3) else ('PRESENT' if offset%4 else 'LATE')
                AttendanceRecord.objects.update_or_create(student=student,date=day,defaults={'class_name':'Class 10','status':status,'marked_by':teachers[0]})
        for day,subject in enumerate([c.subject for c in courses[:5]]):
            TimetableEntry.objects.get_or_create(class_name='Class 10',division='A',subject=subject,weekday=day,start_time=dt_time(9,0),defaults={
                'end_time':dt_time(9,45),'teacher_name': teachers[day].get_full_name(),
            })
        for index,student in enumerate(students):
            fee,_=FeeRecord.objects.get_or_create(student=student,title='Annual school fee',academic_year='2026-2027',defaults={'amount':25000,'due_date':now+timedelta(days=30)})
            if index==0:
                PaymentRecord.objects.get_or_create(fee=fee,reference='DEMO-PAY-001',defaults={'amount':10000,'paid_on':now,'recorded_by':admin})
        test,_=Test.objects.get_or_create(course=math_course,title='Mathematics foundation quiz',created_by=teachers[0],defaults={
            'instructions':'Teacher-created demo test shell. Add questions before using it as a real assessment.',
            'duration_minutes':20,'total_marks':20,'status':'AVAILABLE',
        })
        Notification.objects.get_or_create(recipient=students[0],title='Welcome to ACADEMIX',defaults={'message':'Your demo learning space is ready. Open My Learning to begin.','url':'/courses/'})
        Notification.objects.get_or_create(recipient=parents[0],title='Welcome to ACADEMIX',defaults={'message':'Your parent account is linked to Riya Sharma. Use this portal to check attendance, homework and progress.','url':'/'})
        Announcement.objects.get_or_create(title='Welcome to ACADEMIX',created_by=admin,defaults={'body':'This is sample announcement data for the local demo. Replace it with an institution update.','audience_roles':['ADMIN','TEACHER','STUDENT','PARENT'],'published_at':timezone.now()})
        self.stdout.write(self.style.SUCCESS('Demo data created/refreshed. Passwords were reset to the local demo values listed in README.md.'))

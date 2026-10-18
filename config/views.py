from datetime import date
from functools import wraps
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import Avg, Count, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from accounts.models import UserProfile
from academics.models import Course, Subject
from lessons.models import Lesson, LessonProgress, StudyMaterial
from homework.models import Homework, HomeworkSubmission
from exams.models import Test, TestAttempt
from attendance.models import AttendanceRecord
from timetable.models import TimetableEntry
from fees.models import FeeRecord, PaymentRecord
from notifications.models import Notification, Announcement
from .forms import (SignupForm, CourseForm, LessonForm, MaterialForm, HomeworkForm, SubmissionForm,
                    ReviewForm, TimetableForm, FeeForm, PaymentForm, TestForm, UserCreateForm)

User = get_user_model()

def user_role(user):
    if user.is_superuser: return 'ADMIN'
    p=UserProfile.objects.filter(user=user).first()
    return p.role if p else ('ADMIN' if user.is_staff else 'STUDENT')

def role_required(*roles):
    def decorate(view):
        @wraps(view)
        @login_required
        def wrapped(request,*args,**kwargs):
            r=user_role(request.user)
            if roles and r not in roles: raise PermissionDenied('Your account does not have permission to open this page.')
            return view(request,*args,**kwargs)
        return wrapped
    return decorate

def profile_of(user):
    profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role': user_role(user), 'display_name': user.get_full_name()})
    return profile

def student_users():
    return User.objects.filter(academix_profile__role='STUDENT').select_related('academix_profile').order_by('first_name','username')

def teacher_students(user):
    qs=student_users().none()
    for class_name, division in Course.objects.filter(teacher=user).values_list('class_name','division').distinct():
        if not class_name: continue
        class_filter=Q(academix_profile__class_name=class_name)
        if division: class_filter &= (Q(academix_profile__division=division)|Q(academix_profile__division=''))
        qs=qs | student_users().filter(class_filter)
    return qs.distinct()

def allowed_courses(user):
    r=user_role(user); p=profile_of(user)
    if r=='ADMIN': return Course.objects.select_related('subject','teacher').all()
    if r=='TEACHER': return Course.objects.select_related('subject','teacher').filter(teacher=user)
    if r=='PARENT':
        child_profiles=UserProfile.objects.filter(user__in=p.linked_students.all())
        if not child_profiles.exists(): return Course.objects.none()
        # Match class/division pairs together for families with more than one child.
        q=Q(class_name='',division='')
        for child_profile in child_profiles:
            if child_profile.class_name:
                q |= Q(class_name=child_profile.class_name,division__in=[child_profile.division,''])
        return Course.objects.filter(is_published=True).filter(q).select_related('subject','teacher').distinct()
    if not p.class_name: return Course.objects.none()
    qs=Course.objects.filter(is_published=True).filter(Q(class_name=p.class_name)|Q(class_name=''))
    if p.division: qs=qs.filter(Q(division=p.division)|Q(division=''))
    return qs.select_related('subject','teacher')

def permitted_course(user, pk):
    course=get_object_or_404(Course.objects.select_related('teacher','subject'),pk=pk)
    r=user_role(user); p=profile_of(user)
    if r=='ADMIN': return course
    if r=='TEACHER' and course.teacher_id==user.id: return course
    if r in ('STUDENT','PARENT') and course.is_published:
        allowed=allowed_courses(user).filter(pk=course.pk).exists()
        if allowed:return course
    raise PermissionDenied('You do not have access to this course.')

def notify(user, title, message, url=''):
    Notification.objects.create(recipient=user,title=title,message=message,url=url)

def notify_student_and_parents(student, title, message, url=''):
    notify(student,title,message,url)
    profiles=UserProfile.objects.filter(linked_students=student).select_related('user')
    for parent_profile in profiles: notify(parent_profile.user,title,message,url)

@require_POST
@login_required
def logout_view(request):
    from django.contrib.auth import logout
    logout(request); return redirect('login')

def signup(request):
    if request.user.is_authenticated: return redirect('dashboard')
    if request.method=='POST':
        form=SignupForm(request.POST)
        if form.is_valid():
            user=form.save(); login(request,user); messages.success(request,'Your account was created. Welcome to ACADEMIX!'); return redirect('dashboard')
    else: form=SignupForm()
    return render(request,'accounts/signup.html',{'form':form})

@login_required
def dashboard(request):
    r=user_role(request.user); profile=profile_of(request.user); today=timezone.localdate()
    context={'today':today,'profile':profile,'role':r}
    if r=='ADMIN':
        context.update({'student_count':student_users().count(),'teacher_count':User.objects.filter(academix_profile__role='TEACHER').count(),'parent_count':User.objects.filter(academix_profile__role='PARENT').count(),'course_count':Course.objects.count(),'homework_count':Homework.objects.count(),'pending_submissions':HomeworkSubmission.objects.filter(status='SUBMITTED',marks__isnull=True).count(),'courses':Course.objects.select_related('teacher','subject').order_by('-created_at')[:6],'recent_users':User.objects.select_related('academix_profile').order_by('-date_joined')[:8]})
        template='dashboard_admin.html'
    elif r=='TEACHER':
        courses=Course.objects.filter(teacher=request.user).select_related('subject')
        hw=Homework.objects.filter(created_by=request.user)
        qs=HomeworkSubmission.objects.filter(homework__created_by=request.user,status='SUBMITTED',marks__isnull=True)
        students=teacher_students(request.user)
        context.update({'courses':courses.order_by('-created_at')[:6],'course_count':courses.count(),'homework_count':hw.count(),'pending_reviews':qs.count(),'student_count':students.count(),'upcoming_timetable':TimetableEntry.objects.filter(teacher_name__icontains=request.user.get_full_name() or request.user.username)[:5]})
        template='dashboard_teacher.html'
    elif r=='PARENT':
        children=profile.linked_students.select_related('academix_profile').all()
        data=[]
        for child in children:
            cp=profile_of(child)
            child_courses=allowed_courses(child)
            total=Lesson.objects.filter(course__in=child_courses,status='PUBLISHED').count()
            done=LessonProgress.objects.filter(student=child,completed=True,lesson__course__in=child_courses,lesson__status='PUBLISHED').count()
            att=AttendanceRecord.objects.filter(student=child)
            present=att.filter(status__in=['PRESENT','LATE']).count()
            pct=round(100*present/att.count()) if att.exists() else 0
            hw_qs=Homework.objects.filter(is_published=True,course__in=child_courses)
            hw_total=hw_qs.count()
            hw_pending=hw_qs.exclude(submissions__student=child).count()
            data.append({'user':child,'profile':cp,'total':total,'done':done,'attendance_pct':pct,'homework':hw_total,'homework_pending':hw_pending,'fees':FeeRecord.objects.filter(student=child)})
        context.update({'children_data':data,'child_count':children.count(),'notification_count':Notification.objects.filter(recipient=request.user,is_read=False).count()})
        template='dashboard_parent.html'
    else:
        courses=allowed_courses(request.user)
        total_lessons=Lesson.objects.filter(course__in=courses,status='PUBLISHED').count()
        complete=LessonProgress.objects.filter(student=request.user,completed=True,lesson__course__in=courses).count()
        percent=round(100*complete/total_lessons) if total_lessons else 0
        homeworks=Homework.objects.filter(is_published=True,course__in=courses).select_related('course').order_by('due_at')
        display_courses=list(courses.order_by('title')[:6])
        for course in display_courses:
            course_total=course.lessons.filter(status='PUBLISHED').count()
            course_done=LessonProgress.objects.filter(student=request.user,lesson__course=course,completed=True).count()
            course.user_progress_percent=round(course_done*100/course_total) if course_total else 0
        context.update({'courses':display_courses,'course_count':courses.count(),'total_lessons':total_lessons,'completed_lessons':complete,'progress_percent':percent,'homework_count':homeworks.count(),'pending_homeworks':homeworks.exclude(submissions__student=request.user).count(),'upcoming_homework':homeworks.exclude(submissions__student=request.user).order_by('due_at')[:4],'attendance_records':AttendanceRecord.objects.filter(student=request.user).order_by('-date')[:5],'attendance_count':AttendanceRecord.objects.filter(student=request.user).count(),'attendance_pct':round(100*AttendanceRecord.objects.filter(student=request.user,status__in=['PRESENT','LATE']).count()/AttendanceRecord.objects.filter(student=request.user).count()) if AttendanceRecord.objects.filter(student=request.user).exists() else 0,'test_count':Test.objects.filter(status='AVAILABLE',course__in=courses).count(),'fee_records':FeeRecord.objects.filter(student=request.user)})
        template='dashboard_student.html'
    return render(request,template,context)

@login_required
def courses(request):
    r=user_role(request.user); q=request.GET.get('q','').strip(); qs=allowed_courses(request.user)
    if q: qs=qs.filter(Q(title__icontains=q)|Q(subject__name__icontains=q)|Q(description__icontains=q))
    return render(request,'courses/list.html',{'courses':qs.order_by('-created_at'),'q':q,'role':r})

@role_required('ADMIN','TEACHER')
def course_create(request):
    if request.method=='POST':
        form=CourseForm(request.POST,request.FILES)
        if form.is_valid():
            c=form.save(commit=False)
            if user_role(request.user)=='TEACHER': c.teacher=request.user
            else:
                teacher_id=request.POST.get('teacher')
                if teacher_id:
                    c.teacher=get_object_or_404(User,pk=teacher_id,academix_profile__role='TEACHER')
                else: c.teacher=request.user
            c.save(); messages.success(request,'Course created. Add lessons and publish it when ready.'); return redirect('course_detail',pk=c.pk)
    else: form=CourseForm(initial={'academic_year':profile_of(request.user).academic_year})
    teachers=User.objects.filter(academix_profile__role='TEACHER') if user_role(request.user)=='ADMIN' else []
    return render(request,'courses/course_form.html',{'form':form,'page_title':'Create course','teachers':teachers})

@role_required('ADMIN','TEACHER')
def course_edit(request,pk):
    course=get_object_or_404(Course,pk=pk)
    if user_role(request.user)=='TEACHER' and course.teacher_id!=request.user.id: raise PermissionDenied
    if request.method=='POST':
        form=CourseForm(request.POST,request.FILES,instance=course)
        if form.is_valid():
            c=form.save(commit=False)
            if user_role(request.user)=='TEACHER':c.teacher=request.user
            elif request.POST.get('teacher'):c.teacher=get_object_or_404(User,pk=request.POST['teacher'],academix_profile__role='TEACHER')
            c.save();messages.success(request,'Course updated.');return redirect('course_detail',pk=c.pk)
    else:form=CourseForm(instance=course)
    teachers=User.objects.filter(academix_profile__role='TEACHER') if user_role(request.user)=='ADMIN' else []
    return render(request,'courses/course_form.html',{'form':form,'page_title':'Edit course','course':course,'teachers':teachers})

@login_required
def course_detail(request,pk):
    course=permitted_course(request.user,pk); r=user_role(request.user)
    lessons=course.lessons.all()
    if r not in ('ADMIN','TEACHER'): lessons=lessons.filter(status='PUBLISHED')
    progress_ids=set(LessonProgress.objects.filter(student=request.user,completed=True,lesson__course=course).values_list('lesson_id',flat=True)) if r=='STUDENT' else set()
    total=lessons.count(); done=len(progress_ids)
    return render(request,'courses/detail.html',{'course':course,'lessons':lessons,'role':r,'progress_ids':progress_ids,'course_percent':round(done/total*100) if total else 0})

@role_required('ADMIN','TEACHER')
def lesson_create(request,course_pk):
    course=permitted_course(request.user,course_pk)
    if request.method=='POST':
        form=LessonForm(request.POST,request.FILES)
        if form.is_valid():
            lesson=form.save(commit=False); lesson.course=course; lesson.created_by=request.user; lesson.save(); messages.success(request,'Lesson saved. Add notes or publish when ready.'); return redirect('lesson_detail',pk=lesson.pk)
    else: form=LessonForm(initial={'order':course.lessons.count()+1})
    return render(request,'courses/lesson_form.html',{'form':form,'page_title':'Add lesson','course':course})

@role_required('ADMIN','TEACHER')
def lesson_edit(request,pk):
    lesson=get_object_or_404(Lesson.objects.select_related('course'),pk=pk)
    permitted_course(request.user,lesson.course_id)
    if request.method=='POST':
        form=LessonForm(request.POST,request.FILES,instance=lesson)
        if form.is_valid(): form.save(); messages.success(request,'Lesson updated.'); return redirect('lesson_detail',pk=lesson.pk)
    else:form=LessonForm(instance=lesson)
    return render(request,'courses/lesson_form.html',{'form':form,'page_title':'Edit lesson','course':lesson.course,'lesson':lesson})

@role_required('ADMIN','TEACHER')
def material_create(request,lesson_pk):
    lesson=get_object_or_404(Lesson.objects.select_related('course'),pk=lesson_pk); permitted_course(request.user,lesson.course_id)
    if request.method=='POST':
        form=MaterialForm(request.POST,request.FILES)
        if form.is_valid(): m=form.save(commit=False);m.lesson=lesson;m.save();messages.success(request,'Study material added.');return redirect('lesson_detail',pk=lesson.pk)
    else:form=MaterialForm()
    return render(request,'courses/material_form.html',{'form':form,'lesson':lesson})

@login_required
def lesson_detail(request,pk):
    lesson=get_object_or_404(Lesson.objects.select_related('course__teacher','course__subject'),pk=pk); c=permitted_course(request.user,lesson.course_id);r=user_role(request.user)
    if r not in ('ADMIN','TEACHER') and lesson.status!='PUBLISHED':raise PermissionDenied('This lesson is not published yet.')
    if request.method=='POST' and r=='STUDENT':
        complete=request.POST.get('completed')=='yes'
        LessonProgress.objects.update_or_create(lesson=lesson,student=request.user,defaults={'completed':complete})
        messages.success(request,'Lesson progress updated.');return redirect('lesson_detail',pk=pk)
    progress=LessonProgress.objects.filter(lesson=lesson,student=request.user).first() if r=='STUDENT' else None
    return render(request,'courses/lesson.html',{'lesson':lesson,'progress':progress,'role':r})

@login_required
def homework_list(request):
    r=user_role(request.user); courses_qs=allowed_courses(request.user)
    if r=='TEACHER': qs=Homework.objects.filter(created_by=request.user).select_related('course')
    elif r=='ADMIN': qs=Homework.objects.select_related('course','created_by')
    else: qs=Homework.objects.filter(is_published=True,course__in=courses_qs).select_related('course','created_by')
    rows=[]
    parent_children=list(profile_of(request.user).linked_students.all()) if r=='PARENT' else []
    for hw in qs.order_by('-created_at'):
        sub=HomeworkSubmission.objects.filter(homework=hw,student=request.user).first() if r=='STUDENT' else None
        child_statuses=[{'student':child,'submission':HomeworkSubmission.objects.filter(homework=hw,student=child).first()} for child in parent_children] if r=='PARENT' else []
        rows.append({'homework':hw,'submission':sub,'child_statuses':child_statuses,'submission_count':hw.submissions.count(),'pending_count':hw.submissions.filter(marks__isnull=True).count()})
    return render(request,'homework/list.html',{'rows':rows,'role':r})

@role_required('ADMIN','TEACHER')
def homework_create(request):
    if request.method=='POST':
        form=HomeworkForm(request.POST)
        if user_role(request.user)=='TEACHER': form.fields['course'].queryset=Course.objects.filter(teacher=request.user)
        if form.is_valid():
            hw=form.save(commit=False);hw.created_by=request.user;hw.save()
            if hw.is_published:
                child_profiles=UserProfile.objects.filter(role='STUDENT',class_name=hw.course.class_name)
                for child_profile in child_profiles: notify_student_and_parents(child_profile.user,'New homework assigned',f'{hw.title} is due {hw.due_at:%d %b %Y}.','/homework/')
            messages.success(request,'Homework created.');return redirect('homework')
    else:
        form=HomeworkForm()
        if user_role(request.user)=='TEACHER': form.fields['course'].queryset=Course.objects.filter(teacher=request.user)
    return render(request,'homework/homework_form.html',{'form':form})

@role_required('STUDENT')
def homework_submit(request,pk):
    courses_qs=allowed_courses(request.user);hw=get_object_or_404(Homework,is_published=True,pk=pk,course__in=courses_qs)
    submission=HomeworkSubmission.objects.filter(homework=hw,student=request.user).first()
    if request.method=='POST':
        form=SubmissionForm(request.POST,request.FILES,instance=submission)
        if form.is_valid():
            sub=form.save(commit=False);sub.homework=hw;sub.student=request.user;sub.status='SUBMITTED';sub.submitted_at=timezone.now();sub.save()
            notify(hw.created_by,'Homework submitted',f'{request.user.get_full_name() or request.user.username} submitted {hw.title}.','/homework/')
            messages.success(request,'Homework submitted successfully.');return redirect('homework')
    else:form=SubmissionForm(instance=submission)
    return render(request,'homework/submit.html',{'homework':hw,'form':form,'submission':submission})

@role_required('ADMIN','TEACHER')
def homework_review(request,pk):
    hw=get_object_or_404(Homework.objects.select_related('course','created_by'),pk=pk)
    if user_role(request.user)=='TEACHER' and hw.created_by_id!=request.user.id: raise PermissionDenied
    submissions=hw.submissions.select_related('student').order_by('student__username')
    submission_rows=[{'submission': item, 'form': ReviewForm(instance=item)} for item in submissions]
    if request.method=='POST':
        sub=get_object_or_404(submissions,pk=request.POST.get('submission_id'))
        form=ReviewForm(request.POST,instance=sub)
        if form.is_valid():
            reviewed=form.save(commit=False);reviewed.status='REVIEWED';reviewed.save()
            notify_student_and_parents(sub.student,'Homework reviewed',f'Your submission for {hw.title} has been reviewed.','/homework/')
            messages.success(request,'Feedback saved.');return redirect('homework_review',pk=hw.pk)
    return render(request,'homework/review.html',{'homework':hw,'submission_rows':submission_rows})

@login_required
def attendance_page(request):
    r=user_role(request.user);p=profile_of(request.user);today=timezone.localdate();selected_date=request.GET.get('date') or today.isoformat()
    if r=='STUDENT': qs=AttendanceRecord.objects.filter(student=request.user)
    elif r=='PARENT': qs=AttendanceRecord.objects.filter(student__in=p.linked_students.all())
    elif r=='TEACHER':
        allowed_student_ids=teacher_students(request.user).values_list('id',flat=True)
        qs=AttendanceRecord.objects.filter(student_id__in=allowed_student_ids)
    else: qs=AttendanceRecord.objects.all()
    if request.GET.get('date') or r in ('ADMIN','TEACHER'):
        qs=qs.filter(date=selected_date)
    if r in ('ADMIN','TEACHER') and request.method=='POST':
        student=get_object_or_404(student_users(),pk=request.POST.get('student_id'))
        if r=='TEACHER' and not teacher_students(request.user).filter(pk=student.pk).exists(): raise PermissionDenied
        att_date=request.POST.get('date') or str(today); status=request.POST.get('status','PRESENT')
        if status not in ('PRESENT','ABSENT','LATE','LEAVE'): raise PermissionDenied
        rec,_=AttendanceRecord.objects.update_or_create(student=student,date=att_date,defaults={'class_name':profile_of(student).class_name,'status':status,'marked_by':request.user})
        if status=='ABSENT':notify_student_and_parents(student,'Attendance alert',f'{student.get_full_name() or student.username} was marked absent on {att_date}.','/attendance/')
        messages.success(request,f'Attendance saved for {student.get_full_name() or student.username}.');return redirect(f"{reverse('attendance')}?date={att_date}")
    students=student_users()
    if r=='TEACHER': students=teacher_students(request.user)
    if r=='PARENT': children=p.linked_students.all();students=children
    total=qs.count();present=qs.filter(status__in=['PRESENT','LATE']).count()
    return render(request,'attendance/list.html',{'records':qs.select_related('student').order_by('-date')[:100],'students':students,'role':r,'today':today,'selected_date':selected_date,'attendance_pct':round(present*100/total) if total else 0,'present_count':qs.filter(status='PRESENT').count(),'absent_count':qs.filter(status='ABSENT').count(),'leave_count':qs.filter(status='LEAVE').count()})

@login_required
def timetable_page(request):
    r=user_role(request.user);p=profile_of(request.user)
    if request.method=='POST' and r in ('ADMIN','TEACHER'):
        form=TimetableForm(request.POST)
        if form.is_valid():
            entry=form.save(commit=False)
            if r=='TEACHER':
                matching_courses=Course.objects.filter(teacher=request.user, class_name=entry.class_name, subject=entry.subject)
                if entry.division: matching_courses=matching_courses.filter(Q(division=entry.division)|Q(division=''))
                course=matching_courses.first()
                if not course: messages.error(request,'Choose a class and subject assigned to your courses.');return redirect('timetable')
                entry.teacher_name=request.user.get_full_name() or request.user.username
            entry.save();messages.success(request,'Timetable entry saved.');return redirect('timetable')
    else:form=TimetableForm()
    qs=TimetableEntry.objects.all()
    if r=='STUDENT':
        if not p.class_name: qs=qs.filter(class_name='',division='')
        else:
            qs=qs.filter(Q(class_name=p.class_name)|Q(class_name=''))
            if p.division: qs=qs.filter(Q(division=p.division)|Q(division=''))
    elif r=='PARENT':
        child_profiles=UserProfile.objects.filter(user__in=p.linked_students.all())
        q=Q(class_name='',division='')
        for child_profile in child_profiles:
            if child_profile.class_name:
                q |= Q(class_name=child_profile.class_name,division__in=[child_profile.division,''])
        qs=qs.filter(q) if child_profiles.exists() else qs.none()
    elif r=='TEACHER':qs=qs.filter(teacher_name__icontains=request.user.get_full_name() or request.user.username)
    return render(request,'timetable/list.html',{'entries':qs.select_related('subject'),'form':form if r in ('ADMIN','TEACHER') else None,'role':r,'weekdays':['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']})

@login_required
def fee_receipt(request, payment_pk):
    payment=get_object_or_404(PaymentRecord.objects.select_related('fee__student','recorded_by'),pk=payment_pk)
    role=user_role(request.user)
    if role!='ADMIN':
        p=profile_of(request.user)
        allowed=(role=='STUDENT' and payment.fee.student_id==request.user.id) or (role=='PARENT' and p.linked_students.filter(pk=payment.fee.student_id).exists())
        if not allowed: raise PermissionDenied
    return render(request,'fees/receipt.html',{'payment':payment,'role':role})

@login_required
def fees_page(request):
    r=user_role(request.user);p=profile_of(request.user)
    fee_form=FeeForm(); fee_form.fields['student'].queryset=student_users()
    payment_form=PaymentForm(); payment_form.fields['fee'].queryset=FeeRecord.objects.all()
    if request.method=='POST' and r=='ADMIN':
        if request.POST.get('form_type')=='payment':
            payment_form=PaymentForm(request.POST);payment_form.fields['fee'].queryset=FeeRecord.objects.all()
            if payment_form.is_valid():
                payment=payment_form.save(commit=False);payment.recorded_by=request.user;payment.save();notify_student_and_parents(payment.fee.student,'Fee payment recorded',f'Payment of ₹{payment.amount} was recorded for {payment.fee.title}.','/fees/');messages.success(request,'Payment record saved.');return redirect('fees')
        else:
            fee_form=FeeForm(request.POST);fee_form.fields['student'].queryset=student_users()
            if fee_form.is_valid():
                fee=fee_form.save()
                due_label=fee.due_date or 'the due date set by your institution'
                notify_student_and_parents(fee.student,'New fee record',f'{fee.title}: ₹{fee.amount} recorded. Due: {due_label}.','/fees/')
                messages.success(request,'Fee record created and student/parent notified.')
                return redirect('fees')
    qs=FeeRecord.objects.select_related('student').prefetch_related('payments')
    if r=='STUDENT':qs=qs.filter(student=request.user)
    elif r=='PARENT':qs=qs.filter(student__in=p.linked_students.all())
    elif r=='TEACHER':qs=FeeRecord.objects.none()
    rows=[]
    for fee in qs:
        paid=sum((x.amount for x in fee.payments.all()),start=0)
        rows.append({'fee':fee,'paid':paid,'balance':fee.amount-paid})
    return render(request,'fees/list.html',{'rows':rows,'form':fee_form if r=='ADMIN' else None,'payment_form':payment_form if r=='ADMIN' else None,'role':r})

@login_required
def students_page(request):
    r=user_role(request.user)
    if r not in ('ADMIN','TEACHER'):raise PermissionDenied
    qs=student_users()
    if r=='TEACHER':
        classes=Course.objects.filter(teacher=request.user).values_list('class_name',flat=True).distinct()
        qs=qs.filter(academix_profile__class_name__in=classes)
    if request.GET.get('q'):
        q=request.GET['q'];qs=qs.filter(Q(username__icontains=q)|Q(first_name__icontains=q)|Q(last_name__icontains=q)|Q(email__icontains=q))
    return render(request,'students/list.html',{'students':qs,'q':request.GET.get('q',''),'role':r})

@role_required('ADMIN')
def users_page(request):
    if request.method=='POST' and request.POST.get('action')=='update_profile':
        target=get_object_or_404(User,pk=request.POST.get('user_id'))
        target_profile=profile_of(target)
        new_role=request.POST.get('role','STUDENT')
        if new_role not in UserProfile.Role.values: raise PermissionDenied('Unknown role.')
        target_profile.role=new_role;target_profile.class_name=request.POST.get('class_name','').strip();target_profile.division=request.POST.get('division','').strip();target_profile.display_name=target.get_full_name();target_profile.save()
        if new_role!='STUDENT': target_profile.class_name='';target_profile.division='';target_profile.save(update_fields=['class_name','division'])
        messages.success(request,f'Profile updated for {target.username}.');return redirect('users')
    if request.method=='POST' and request.POST.get('action')=='link_parent':
        parent=get_object_or_404(User,pk=request.POST.get('parent_id'),academix_profile__role='PARENT')
        student=get_object_or_404(student_users(),pk=request.POST.get('student_id'))
        parent_profile=profile_of(parent)
        if request.POST.get('link_action')=='unlink': parent_profile.linked_students.remove(student);messages.success(request,'Parent-child link removed.')
        else: parent_profile.linked_students.add(student);messages.success(request,'Parent-child link saved.')
        return redirect('users')
    if request.method=='POST':
        form=UserCreateForm(request.POST)
        if form.is_valid():form.save();messages.success(request,'User account created.');return redirect('users')
    else:form=UserCreateForm()
    users=User.objects.select_related('academix_profile').order_by('-date_joined')
    parents=User.objects.filter(academix_profile__role='PARENT').order_by('first_name','username')
    return render(request,'accounts/users.html',{'form':form,'users':users,'parents':parents,'students_for_link':student_users()})

@login_required
def results_page(request):
    r=user_role(request.user);p=profile_of(request.user)
    submissions=HomeworkSubmission.objects.filter(marks__isnull=False).select_related('homework','student','homework__course')
    attempts=TestAttempt.objects.filter(is_submitted=True).select_related('test','student','test__course')
    if r=='STUDENT':submissions=submissions.filter(student=request.user);attempts=attempts.filter(student=request.user)
    elif r=='PARENT':submissions=submissions.filter(student__in=p.linked_students.all());attempts=attempts.filter(student__in=p.linked_students.all())
    elif r=='TEACHER':submissions=submissions.filter(homework__created_by=request.user);attempts=attempts.filter(test__created_by=request.user)
    student_summaries=submissions.values('student_id','student__first_name','student__last_name','student__username').annotate(graded_count=Count('id'),average_marks=Avg('marks')).order_by('student__first_name')[:100]
    submissions=submissions.order_by('-submitted_at')[:100]; attempts=attempts.order_by('-submitted_at')[:100]
    if request.GET.get('format')=='csv':
        import csv
        from django.http import HttpResponse
        response=HttpResponse(content_type='text/csv');response['Content-Disposition']='attachment; filename="academix-results.csv"'
        writer=csv.writer(response);writer.writerow(['Type','Student','Activity','Course','Marks','Feedback','Submitted'])
        for sub in submissions:writer.writerow(['Homework',sub.student.get_full_name() or sub.student.username,sub.homework.title,sub.homework.course.title,sub.marks,sub.feedback,sub.submitted_at])
        for attempt in attempts:writer.writerow(['Test',attempt.student.get_full_name() or attempt.student.username,attempt.test.title,attempt.test.course.title,attempt.score,'',attempt.submitted_at])
        return response
    return render(request,'results/list.html',{'submissions':submissions,'attempts':attempts,'student_summaries':student_summaries,'role':r})

@login_required
def exams_page(request):
    r=user_role(request.user); courses_qs=allowed_courses(request.user)
    if request.method=='POST' and r in ('ADMIN','TEACHER'):
        form=TestForm(request.POST)
        if r=='TEACHER':form.fields['course'].queryset=Course.objects.filter(teacher=request.user)
        if form.is_valid():t=form.save(commit=False);t.created_by=request.user;t.save();messages.success(request,'Test saved.');return redirect('exams')
    else:form=TestForm()
    if r=='TEACHER':form.fields['course'].queryset=Course.objects.filter(teacher=request.user)
    qs=Test.objects.filter(course__in=courses_qs) if r not in ('ADMIN','TEACHER') else Test.objects.filter(created_by=request.user) if r=='TEACHER' else Test.objects.all()
    return render(request,'exams/list.html',{'tests':qs.select_related('course'),'form':form if r in ('ADMIN','TEACHER') else None,'role':r})

@login_required
def notifications_page(request):
    qs=Notification.objects.filter(recipient=request.user)
    if request.method=='POST':qs.filter(is_read=False).update(is_read=True);messages.success(request,'Notifications marked as read.');return redirect('notifications')
    return render(request,'notifications.html',{'notifications':qs,'role':user_role(request.user)})

@login_required
def announcements_page(request):
    r=user_role(request.user); profile=profile_of(request.user)
    qs=Announcement.objects.all().order_by('-created_at')
    child_classes=set(profile.linked_students.values_list('academix_profile__class_name',flat=True)) if r=='PARENT' else set()
    visible=[]
    for item in qs:
        if item.audience_roles and r not in item.audience_roles:
            continue
        if item.class_name:
            if r=='STUDENT' and profile.class_name!=item.class_name:
                continue
            if r=='PARENT' and item.class_name not in child_classes:
                continue
            if r=='TEACHER' and not Course.objects.filter(teacher=request.user,class_name=item.class_name).exists():
                continue
        visible.append(item)
    return render(request,'announcements/list.html',{'announcements':visible,'role':r})

@login_required
def settings_page(request):
    p=profile_of(request.user)
    if request.method=='POST':
        request.user.first_name=request.POST.get('first_name','').strip();request.user.last_name=request.POST.get('last_name','').strip();request.user.email=request.POST.get('email','').strip();request.user.save()
        p.display_name=request.user.get_full_name();p.phone=request.POST.get('phone','').strip();p.save();messages.success(request,'Profile settings saved.');return redirect('settings')
    return render(request,'accounts/settings.html',{'profile':p})

@login_required
def teachers_list(request):
    if user_role(request.user)!='ADMIN': raise PermissionDenied
    people=User.objects.filter(academix_profile__role='TEACHER').select_related('academix_profile').order_by('first_name','username')
    return render(request,'accounts/people_list.html',{'people':people,'title':'Teachers','role_label':'Teacher'})

@login_required
def parents_list(request):
    if user_role(request.user)!='ADMIN': raise PermissionDenied
    people=User.objects.filter(academix_profile__role='PARENT').select_related('academix_profile').prefetch_related('academix_profile__linked_students').order_by('first_name','username')
    return render(request,'accounts/people_list.html',{'people':people,'title':'Parents','role_label':'Parent'})

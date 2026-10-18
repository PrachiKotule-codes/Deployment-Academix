from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from accounts.models import UserProfile
from academics.models import Subject, Course
from lessons.models import Lesson, StudyMaterial
from homework.models import Homework, HomeworkSubmission
from attendance.models import AttendanceRecord
from timetable.models import TimetableEntry
from fees.models import FeeRecord, PaymentRecord
from exams.models import Test

User = get_user_model()

class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'field-input')
            if isinstance(field.widget, forms.Textarea): field.widget.attrs.setdefault('rows', 3)

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class':'field-input'}))
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class':'field-input'}))
    last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class':'field-input'}))
    role = forms.ChoiceField(choices=[('STUDENT','Student'),('TEACHER','Teacher'),('PARENT','Parent')], widget=forms.Select(attrs={'class':'field-input'}))
    class_name = forms.CharField(max_length=60, required=False, initial='Class 10', widget=forms.TextInput(attrs={'class':'field-input','placeholder':'e.g. Class 10'}), label='Student class (optional)')
    division = forms.CharField(max_length=30, required=False, initial='A', widget=forms.TextInput(attrs={'class':'field-input','placeholder':'e.g. A'}), label='Student division (optional)')
    class Meta:
        model = User
        fields = ('username','first_name','last_name','email','role','class_name','division','password1','password2')
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values(): field.widget.attrs.setdefault('class','field-input')
    def save(self, commit=True):
        user=super().save(commit=False)
        user.email=self.cleaned_data['email']; user.first_name=self.cleaned_data['first_name']; user.last_name=self.cleaned_data.get('last_name','')
        if commit:
            user.save()
            role=self.cleaned_data['role']
            UserProfile.objects.update_or_create(user=user,defaults={'role':role,'display_name':user.get_full_name(),'class_name':self.cleaned_data.get('class_name','') if role=='STUDENT' else '', 'division':self.cleaned_data.get('division','') if role=='STUDENT' else ''})
        return user

class CourseForm(StyledModelForm):
    class Meta:
        model=Course
        fields=('title','subject','description','module_name','class_name','division','academic_year','thumbnail','is_published')
        widgets={'description':forms.Textarea(attrs={'rows':4}), 'is_published':forms.CheckboxInput(attrs={'class':'checkbox-input'})}

class LessonForm(StyledModelForm):
    class Meta:
        model=Lesson
        fields=('title','section_title','description','order','duration_minutes','video_url','video_file','mindmap_url','quick_recap','status')
        widgets={'description':forms.Textarea(attrs={'rows':3}), 'quick_recap':forms.Textarea(attrs={'rows':4}), 'status':forms.Select()}

class MaterialForm(StyledModelForm):
    class Meta:
        model=StudyMaterial
        fields=('title','file','external_url')

class HomeworkForm(StyledModelForm):
    due_at=forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type':'datetime-local'},format='%Y-%m-%dT%H:%M'), input_formats=['%Y-%m-%dT%H:%M'])
    class Meta:
        model=Homework
        fields=('course','title','instructions','due_at','is_published')
        widgets={'instructions':forms.Textarea(attrs={'rows':4}), 'is_published':forms.CheckboxInput(attrs={'class':'checkbox-input'})}

class SubmissionForm(StyledModelForm):
    class Meta:
        model=HomeworkSubmission
        fields=('answer_text','attachment')
        widgets={'answer_text':forms.Textarea(attrs={'rows':5,'placeholder':'Write your answer or notes here...'})}

class ReviewForm(StyledModelForm):
    class Meta:
        model=HomeworkSubmission
        fields=('marks','feedback')
        widgets={'feedback':forms.Textarea(attrs={'rows':4})}

class TimetableForm(StyledModelForm):
    class Meta:
        model=TimetableEntry
        fields=('class_name','division','subject','teacher_name','weekday','start_time','end_time','room','academic_year')
        widgets={'start_time':forms.TimeInput(attrs={'type':'time'}),'end_time':forms.TimeInput(attrs={'type':'time'}),'weekday':forms.Select(choices=[(0,'Monday'),(1,'Tuesday'),(2,'Wednesday'),(3,'Thursday'),(4,'Friday'),(5,'Saturday'),(6,'Sunday')])}

class FeeForm(StyledModelForm):
    class Meta:
        model=FeeRecord
        fields=('student','title','academic_year','amount','due_date')
        widgets={'due_date':forms.DateInput(attrs={'type':'date'})}

class TestForm(StyledModelForm):
    starts_at=forms.DateTimeField(required=False,widget=forms.DateTimeInput(attrs={'type':'datetime-local'},format='%Y-%m-%dT%H:%M'),input_formats=['%Y-%m-%dT%H:%M'])
    ends_at=forms.DateTimeField(required=False,widget=forms.DateTimeInput(attrs={'type':'datetime-local'},format='%Y-%m-%dT%H:%M'),input_formats=['%Y-%m-%dT%H:%M'])
    class Meta:
        model=Test
        fields=('course','title','instructions','duration_minutes','total_marks','starts_at','ends_at','status')
        widgets={'instructions':forms.Textarea(attrs={'rows':3}),'starts_at':forms.DateTimeInput(attrs={'type':'datetime-local'}),'ends_at':forms.DateTimeInput(attrs={'type':'datetime-local'})}

class UserCreateForm(UserCreationForm):
    linked_student=forms.ModelChoiceField(queryset=User.objects.filter(academix_profile__role='STUDENT').order_by('first_name','username'),required=False,widget=forms.Select(attrs={'class':'field-input'}),label='Link parent to student (optional)')
    first_name=forms.CharField(max_length=150,widget=forms.TextInput(attrs={'class':'field-input'}))
    last_name=forms.CharField(max_length=150,required=False,widget=forms.TextInput(attrs={'class':'field-input'}))
    email=forms.EmailField(widget=forms.EmailInput(attrs={'class':'field-input'}))
    role=forms.ChoiceField(choices=UserProfile.Role.choices,widget=forms.Select(attrs={'class':'field-input'}))
    class_name=forms.CharField(max_length=60,required=False,widget=forms.TextInput(attrs={'class':'field-input'}))
    division=forms.CharField(max_length=30,required=False,widget=forms.TextInput(attrs={'class':'field-input'}))
    class Meta:
        model=User
        fields=('username','first_name','last_name','email','role','class_name','division','linked_student','password1','password2')
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values(): field.widget.attrs.setdefault('class','field-input')
    def save(self,commit=True):
        user=super().save(commit=False); user.first_name=self.cleaned_data['first_name']; user.last_name=self.cleaned_data.get('last_name',''); user.email=self.cleaned_data['email']
        if commit:
            user.save(); profile, _ = UserProfile.objects.update_or_create(user=user,defaults={'role':self.cleaned_data['role'],'display_name':user.get_full_name(),'class_name':self.cleaned_data.get('class_name',''),'division':self.cleaned_data.get('division','')})
            if self.cleaned_data.get('linked_student') and profile.role == 'PARENT': profile.linked_students.add(self.cleaned_data['linked_student'])
        return user

class PaymentForm(StyledModelForm):
    class Meta:
        model=PaymentRecord
        fields=('fee','amount','paid_on','reference')
        widgets={'paid_on':forms.DateInput(attrs={'type':'date'})}

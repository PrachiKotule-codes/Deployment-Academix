from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(template_name='registration/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('', views.dashboard, name='dashboard'),
    path('courses/', views.courses, name='courses'),
    path('courses/new/', views.course_create, name='course_create'),
    path('courses/<int:pk>/edit/', views.course_edit, name='course_edit'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_pk>/lessons/new/', views.lesson_create, name='lesson_create'),
    path('lessons/<int:pk>/', views.lesson_detail, name='lesson_detail'),
    path('lessons/<int:pk>/edit/', views.lesson_edit, name='lesson_edit'),
    path('lessons/<int:lesson_pk>/materials/new/', views.material_create, name='material_create'),
    path('homework/', views.homework_list, name='homework'),
    path('homework/new/', views.homework_create, name='homework_create'),
    path('homework/<int:pk>/submit/', views.homework_submit, name='homework_submit'),
    path('homework/<int:pk>/review/', views.homework_review, name='homework_review'),
    path('exams/', views.exams_page, name='exams'),
    path('attendance/', views.attendance_page, name='attendance'),
    path('timetable/', views.timetable_page, name='timetable'),
    path('fees/', views.fees_page, name='fees'),
    path('fees/payment/<int:payment_pk>/receipt/', views.fee_receipt, name='fee_receipt'),
    path('students/', views.students_page, name='students'),
    path('teachers/', views.teachers_list, name='teachers_list'),
    path('parents/', views.parents_list, name='parents_list'),
    path('accounts/', views.users_page, name='users'),
    path('results/', views.results_page, name='results'),
    path('notifications/', views.notifications_page, name='notifications'),
    path('announcements/', views.announcements_page, name='announcements'),
    path('settings/', views.settings_page, name='settings'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

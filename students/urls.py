from django.urls import path
from .views import portal_home
urlpatterns=[path('',portal_home,name='students_home')]

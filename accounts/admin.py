from django.contrib import admin
from .models import UserProfile
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
 list_display=('user','role','display_name','class_name','academic_year')
 list_filter=('role','academic_year','class_name')
 search_fields=('user__username','display_name','user__email')

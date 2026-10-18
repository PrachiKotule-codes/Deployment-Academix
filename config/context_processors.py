from accounts.models import UserProfile
from notifications.models import Notification

def academix(request):
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        return {'role': None, 'profile': None, 'notification_count': 0}
    profile = UserProfile.objects.filter(user=request.user).first()
    role = 'ADMIN' if request.user.is_superuser else (profile.role if profile else ('ADMIN' if request.user.is_staff else 'STUDENT'))
    return {'role': role, 'profile': profile, 'notification_count': Notification.objects.filter(recipient=request.user, is_read=False).count()}

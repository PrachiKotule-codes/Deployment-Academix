from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
def role_required(*roles):
 def dec(view):
  @login_required
  @wraps(view)
  def wrapped(request,*args,**kwargs):
   profile=getattr(request.user,'academix_profile',None)
   if request.user.is_superuser or (profile and profile.role in roles): return view(request,*args,**kwargs)
   raise PermissionDenied
  return wrapped
 return dec

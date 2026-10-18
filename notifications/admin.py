from django.contrib import admin
from .models import *
for model in [x for x in globals().values() if isinstance(x,type) and hasattr(x,'_meta') and getattr(x._meta,'app_label',None)=='notifications']:
    try: admin.site.register(model)
    except admin.sites.AlreadyRegistered: pass

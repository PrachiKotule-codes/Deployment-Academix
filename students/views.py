from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required
def portal_home(request): return render(request,'generic.html',{'title':'Portal','items':[],'kind':'generic','role':'USER'})

from django.http import HttpResponse
from django.shortcuts import redirect

def unauthenticated_user(view_func):
    def wrapper_func (request,*args,**kwargs):
        if request.user.is_authenticated:
            if request.user.roles == 'teacher':
                return redirect ('teachvw')
            else:
                return redirect ('studvw')
        else: 
            return view_func(request,*args,**kwargs)
    return wrapper_func

def authenticated_teacher(view_func):
    def wrapper_func (request,*args,**kwargs):
        if request.user.is_authenticated:
            if request.user.roles == 'teacher':
                return view_func(request,*args,**kwargs)
            else:
                return redirect('studvw')
        else: 
            return redirect('loginpg')
    return wrapper_func

def authenticated_student(view_func):
    def wrapper_func (request,*args,**kwargs):
        if request.user.is_authenticated:
            if request.user.roles == 'teacher':
                return redirect('teachvw')
            else:
                return view_func(request,*args,**kwargs)
        else: 
            return redirect('loginpg')
    return wrapper_func
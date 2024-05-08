from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from .forms import CustomUserCreationForm,LoginForm, AddActivity, teacherUpdateForm, studentUpdateForm,addTeacherForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Teacher, Student, StudentRequest, Activity, Subcategory, Level, Notif, Achievement, CustomUser
from django.contrib.auth.decorators import login_required,permission_required
from django.db import IntegrityError
from .decorators import unauthenticated_user, authenticated_student, authenticated_teacher,authenticated_admin
from django.db.models import Sum, Case,When,Value,CharField
from django.db.models import Q
from django.contrib.staticfiles import finders

class DuplicateRegNoError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

@unauthenticated_user
def homepag(request):
    template= loader.get_template("Home.html")
    return HttpResponse(template.render())

@unauthenticated_user
def registervw(request):
    msg = None
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            msg = 'User Created Successfully'
            regno = form.cleaned_data.get('regno').lower()
            batch = form.cleaned_data.get('batch')
            try:
                teacher = Teacher.objects.get(batch=batch)
                existing_student = Student.objects.filter(regno=regno).first()
                if existing_student:
                    raise DuplicateRegNoError('A student with this registration number already exists.')
                user.save()
                student = StudentRequest.objects.create(name=user.username,user=user,batch=batch,regno=regno,teacher=teacher)
                student.save()
                return redirect('loginpg')  # Redirect to a success page
            except Teacher.DoesNotExist:
                msg= 'the batch teacher has not been assigned'
                form = CustomUserCreationForm(initial={'username': '','regno': '','batch': ''})
            except IntegrityError:
                msg = 'Registration number already exists'
                form = CustomUserCreationForm(initial={'username': '','regno': '','batch': ''})
            except DuplicateRegNoError as e:
                msg = str(e)
                form = CustomUserCreationForm(initial={'username': '','regno': '','batch': ''})
        else:
            msg = 'Form is invalid'
    else:
        form = CustomUserCreationForm(initial={'username': '','regno': ''})
    return render(request, 'Register.html', {'form': form, 'msg':msg})

@unauthenticated_user
def loginvw(request):
    msg= None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                    if user.is_superuser:
                        login(request, user)
                        return redirect('adminvw')
                    elif user.verified == False:
                        msg='Account has not been approved yet'
                    else:
                        login(request, user)
                        if user.roles == 'teacher':
                            return redirect('teachvw')
                        elif user.roles == 'student':
                            return redirect('studvw')
            else:
                msg="Invalid User or password"
        else:
            msg = 'Form is Invalid'
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form, 'msg':msg})

@login_required(login_url='/login')
def logoutvw(request):
    logout(request)
    request.session.flush() 
    messages.success(request, ('Logged out successfully'))
    return redirect('loginpg')

@authenticated_teacher
@login_required(login_url='/login')
def teachvw(request):
    msg=None
    teacher=request.user.teacher
    teachuser=request.user.username
    studreq = [i for i in StudentRequest.objects.all() if i.teacher==teacher]
    students = [i for i in Student.objects.all() if i.teacher == teacher]
    return render(request,'teacherview.html', {'msg':msg, 'students':students,'teacheruser':teachuser,'studreq':studreq})

@authenticated_teacher
@login_required(login_url='/login')
def addstudent(request,id):
    stud_request = StudentRequest.objects.get(id=id)
    student = Student(
        name=stud_request.name,
        regno=stud_request.regno,
        batch=stud_request.batch,
        points=stud_request.points,
        teacher=stud_request.teacher,
        user=stud_request.user
    )
    student.save()
    user= stud_request.user
    user.verified=True
    user.save()
    stud_request.delete()
    return redirect('teachvw')

@authenticated_teacher
@login_required(login_url='/login')
def deletestudent(request,id):
    stud_request = StudentRequest.objects.get(id=id)
    studuser = stud_request.user
    studuser.delete()
    return redirect('teachvw')

@authenticated_teacher
@login_required(login_url='/login')
def approve_activities(request,id):
    act_request= Activity.objects.get(id=id)
    student_activities = Activity.objects.filter(student=act_request.student, level__subcategory=act_request.level.subcategory)
    total_points = student_activities.aggregate(total_points=Sum('points_obtained'))['total_points'] or 0
    newpoints = total_points + act_request.level.points_awarded
    if newpoints>act_request.level.subcategory.max:
        added= newpoints-act_request.level.subcategory.max
    else:
        added=act_request.level.points_awarded
    additional = act_request.achievement.points_awarded
    act_request.additional_obtained=additional
    added=added+additional
    print("added: "+str(added))
    student = act_request.student
    student.points= student.points+added
    student.save()
    print("newtotal: "+str(act_request.student.points+added))
    act_request.approved_status=True
    act_request.points_obtained=added
    act_request.save()
    stud = act_request.student.user
    msghead = "Activity Request Approved"
    msgbody = "Your activity "+str(act_request.name)+" for "+str(act_request.level.subcategory)+ " was approved and was awarded "+str(added)+" points."
    notif = Notif.objects.create(head=msghead,body=msgbody,user=stud)
    notif.save()
    return redirect('activityvw')

@authenticated_teacher
@login_required(login_url='/login')
def delete_activity(request,id):
    act_request = Activity.objects.get(id=id)
    stud = act_request.student.user
    msghead = "Activity Request Rejected"
    msgbody = "Your activity "+str(act_request.name)+" for "+str(act_request.level.subcategory)+ " was Rejected."
    notif = Notif.objects.create(head=msghead,body=msgbody,user=stud)
    notif.save()
    act_request.delete()
    return redirect('activityvw')

@authenticated_teacher
@login_required(login_url='/login')
def teach_cert(request):
    teacher = Teacher.objects.get(user=request.user)
    students = Student.objects.filter(teacher=teacher)
    teachuser= request.user.username
    sort_by = request.GET.get('sort_by')
    if sort_by == 'name':
        students = students.order_by('name')
    elif sort_by == 'regno':
        students = students.order_by('regno')
    elif sort_by == 'points':
        students = students.order_by('-points')
    return render(request, 'teacher_certificates.html', {'students': students ,'teacheruser':teachuser})

@authenticated_teacher
@login_required(login_url='/login')
def student_activities(request, student_id):
    # Retrieve the student's activities
    student = get_object_or_404(Student, id=student_id)
    teacher = Teacher.objects.get(user=request.user)
    teacheruser =request.user.username
    activities = Activity.objects.filter(student=student,approved_status=True)
    sort_by = request.GET.get('sort_by')
    if sort_by == 'name':
        activities = activities.order_by('name')
    elif sort_by == 'date':
        activities = activities.order_by('end_date')
    elif sort_by == 'points':
        activities = activities.order_by('-points_obtained')
    return render(request, 'student_activities.html',{'student': student, 'activities': activities,'teacheruser':teacheruser})

@authenticated_teacher
@login_required(login_url='/login')
def update_teacher(request):
    teacheruser = request.user.username
    user = request.user
    msguser=  None
    msgpass = None
    msgname = None
    if request.method == 'POST':
        form = teacherUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            name = form.cleaned_data.get('name')
            new_password = form.cleaned_data.get('new_password')
            confirm_password =  form.cleaned_data.get('confirm_password')
            
            if username:
                user.username = username
                user.save()
                msguser="Username updated"
            if name is not None and name.strip():
                teacher = Teacher.objects.get(user=request.user)
                teacher.name = name
                teacher.save()
                msgname = 'Name updated'
            if new_password:
                if new_password != confirm_password:
                    msgpass= 'passwords dont match'
                else:
                    msgpass = "Password updated"
                    user.set_password(new_password)
                    user.save()
            return redirect('update_teacher')  # Redirect to profile page or any other page
    else:
        form = teacherUpdateForm(instance=request.user)
    return render(request, 'update_teacher.html', {'form': form, 'teacheruser': teacheruser,'msguser':msguser,'msgpass':msgpass,'msgname':msgname})

@authenticated_student
@login_required(login_url='/login')
def studvw(request):
    studuser = request.user
    student = Student.objects.get(user=studuser)
    activities = Activity.objects.filter(student=student)
    sort_by = request.GET.get('sort_by')
    if sort_by == 'name':
        activities = activities.order_by('name')
    elif sort_by == 'date':
        activities = activities.order_by('end_date')
    elif sort_by == 'points':
        activities = activities.order_by('-points_obtained')

    return render(request,'studentview.html',{'student':student,'certificates':activities,'studuser':studuser})

@authenticated_student
@login_required(login_url='/login')
def upcert(request):
    msg=None
    studuser = request.user
    if request.method == 'POST':
        form= AddActivity(request.POST,request.FILES)
        if form.is_valid():
            print("success")
            activityreq = form.save(commit=False)
            achievementchoice= form.cleaned_data.get('achievementchoice')
            curruser = request.user
            currstudent = Student.objects.get(user=curruser)
            subc = activityreq.level.subcategory
            actlev= activityreq.level
            print(subc.name)
            
            student_activities = Activity.objects.filter(student=currstudent, level__subcategory=subc)

            total_points = student_activities.aggregate(total_points=Sum('points_obtained'))['total_points'] or 0

            print("Total points obtained in the subcategory:", total_points)
            print("Max points allowed :", subc.max)
            if subc.max > total_points:
                activityreq.student= currstudent
                if achievementchoice:
                    print("achievment: " +achievementchoice)
                    achieve = Achievement.objects.filter(prize= achievementchoice,level__in=[actlev])
                    if achieve.exists():
                        activityreq.achievement = achieve.first()
                        print('Achieve:' +str(achieve))
                    else:
                        print("Achievement not found")
                        msg = "Achievement not found"
                        return render(request,'studentcert.html',{'msg':msg, 'form': form,'studuser':studuser})
                activityreq.save()
                msg= "successfully uploaded"
            else:
                msg= "reached limit for this activity"
        else:
            print(form.errors)
            msg='Invalid Entry'
            print("failed")
    else:
        form = AddActivity()
    return render(request,'studentcert.html',{'msg':msg, 'form': form,'studuser':studuser})

def load_sub(request):
    category_id = request.GET.get('category_id')
    subcategories = Subcategory.objects.filter(category_id=category_id)
    return render(request, 'subcategory_choices.html', {'subcategories': subcategories})

def load_levels(request):
    subcategory_id = request.GET.get('subcategory_id')
    levels = Level.objects.filter(subcategory_id=subcategory_id)
    return render(request, 'level_choices.html', {'levels': levels})

@authenticated_student
@login_required(login_url='/login')
def update_student(request):
    studuser = request.user.username
    user = request.user
    msguser=  None
    msgpass = None
    msgreg = None
    msgname = None
    if request.method == 'POST':
        form = studentUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            regno = form.cleaned_data.get('regno').lower()
            name = form.cleaned_data.get('name')
            new_password = form.cleaned_data.get('new_password')
            confirm_password =  form.cleaned_data.get('confirm_password')
            if username:
                user.username = username
                user.save()
                msguser="Username updated"
            if name is not None and name.strip():
                student = Student.objects.get(user=request.user)
                student.name = name
                student.save()
                msgname = "Name updated"
                print("msgname:", msgname)
            if regno is not None and regno.strip():
                print("trying reg")
                existing_student = Student.objects.filter(regno=regno).first()
                if existing_student:
                    msgreg="This register number is already in use."
                else:
                    student = Student.objects.get(user=request.user)
                    student.regno = regno
                    student.save()
                    msgreg = 'Reg no updated'
            if new_password:
                if new_password != confirm_password:
                    msgpass= 'passwords dont match'
                else:
                    msgpass = "Password updated"
                    user.set_password(new_password)
                    user.save() 
    else:
        form = studentUpdateForm(instance=request.user)
    print("msgreg:", msgreg)
    return render(request, 'update_student.html', {'form': form, 'student': studuser,'msguser':msguser,'msgreg':msgreg, 'msgpass':msgpass,'msgname':msgname})

@authenticated_teacher
@login_required(login_url='/login')
def approve_activity(request):
    teachuser = request.user
    students = Student.objects.filter(teacher=Teacher.objects.get(user=request.user))
    # Using Q objects so we can use logical OR
    # See https://docs.djangoproject.com/en/5.0/topics/db/queries/#complex-lookups-with-q-objects
    qobj = Q(student=students[0])

    for i in students[1:]:
        qobj = qobj | Q(student=i)

    activities = Activity.objects.filter(qobj, approved_status=False)
    


    return render(request, 'approve_activities2.html', { 'activities' : activities ,'teachuser':teachuser})


@login_required(login_url='/login')
def view_notif(request):
    user = request.user
    notifs = Notif.objects.filter(user=user)
    return render(request,'view_notif.html',{'user':user,'notifs':notifs})
    # if user.roles == 'student':
    #     return render(request,'view_notif.html',{'user':user,'notifs':notifs})
    # else:
    #     return render(request,'view_notif2.html',{'user':user,'notifs':notifs})

def notif_delete(request,id):
    notification = get_object_or_404(Notif, id=id)
    notification.delete()
    return redirect('view_notif')

@authenticated_admin
@login_required(login_url='/login')
def adminvw(request):
    user=request.user
    teachers = Teacher.objects.all().order_by(
        Case(
            When(batch='9', then=Value(1)),
            When(batch='10', then=Value(2)),
            When(batch='11', then=Value(3)),
            When(batch='12-a', then=Value(4)),
            When(batch='12-b', then=Value(5)),
            default=Value(6),
            output_field=CharField(),
        )
    )
    return render(request,'adminview.html',{'user':user,'teachers':teachers})

@authenticated_admin
@login_required(login_url='/login')
def student_listing(request,id):
    user=request.user
    teacher= Teacher.objects.get(id=id)
    students=Student.objects.filter(teacher=teacher)
    sort_by = request.GET.get('sort_by')
    if sort_by == 'name':
        students = students.order_by('name')
    elif sort_by == 'regno':
        students = students.order_by('regno')
    elif sort_by == 'points':
        students = students.order_by('-points')
    return render(request, 'student_listing.html',{'students': students,'user':user,'teacher':teacher})

@authenticated_admin
@login_required(login_url='/login')
def addtch(request):
    msg = None
    user=request.user
    if request.method == 'POST':
        form = addTeacherForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.roles='teacher'
            msg = 'User Created Successfully'
            name = form.cleaned_data.get('name')
            batch = form.cleaned_data.get('batch')
            existing_teacher= Teacher.objects.filter(batch=batch)
            if existing_teacher:
                msg="A teacher already exists for this batch."
                return render(request, 'addteach.html', {'form': form, 'msg':msg,'user':user})
            user.save()
            newteach = Teacher.objects.create(name=name,batch=batch,user=user)
            newteach.save()
            students=Student.objects.filter(batch=batch)
            for i in students:
                i.teacher= newteach
                i.save()
        else:
            errors = form.errors.as_data()
            msg = "Form is invalid. Reasons:"
            for field, error_list in errors.items():
                for error in error_list:
                    msg += f"{field}: {error}"
    else:
        form = addTeacherForm()
    return render(request, 'addteach.html', {'form': form, 'msg':msg,'user':user})

@authenticated_admin
@login_required(login_url='/login')
def deletetch(request,id):
    teacherobj = Teacher.objects.get(id=id)
    userobj = teacherobj.user
    userobj.delete()
    return redirect('adminvw')
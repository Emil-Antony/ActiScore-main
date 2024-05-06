from django.urls import path
from . import views

urlpatterns = [
    path("", views.homepag, name="homepage"),
    path('register', views.registervw , name='register'),
    path('login',views.loginvw, name='loginpg'),
    path('logout', views.logoutvw, name='logout'),
    path('teacher/My_students',views.teachvw,name="teachvw"),
    path('addstudent/<int:id>',views.addstudent,name='addstudent'),
    path('deletestudent/<int:id>',views.deletestudent,name='deletestudent'),
    path('student/Dashboard/',views.studvw,name="studvw"),
    path('student/Upload',views.upcert,name="uploadcert"),
    path('load_sub/', views.load_sub, name='load_sub'),
    path('load_levels/', views.load_levels, name='load_levels'),
    path('teacher/view_certificates/', views.teach_cert, name='teach_cert'),
    path('view_certificates/<int:student_id>/activities/', views.student_activities, name='student_activities'),
    path('teacher/update_details',views.update_teacher,name='update_teacher'),
    path('student/update_details',views.update_student,name='update_student')
]   
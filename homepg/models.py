from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
import os

class CustomUser(AbstractUser):
    role=(
        ('teacher','Teacher'),
        ('student','Student')
    )
    roles=models.CharField(max_length=10,choices=role,default="student")
    verified=models.BooleanField(default=False)

class Teacher(models.Model):
    batches=(
        ('9','9'),
        ('10','10'),
        ('11','11'),
        ('12-a','12-a'),
        ('12-b','12-b'))
    name = models.CharField(max_length=100)
    batch = models.CharField(choices=batches,default='9',max_length=10,unique=True)
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE,null=True)
    def __str__(self):
        return(self.name)    

class Student(models.Model):
    batches=(
        ('9','9'),
        ('10','10'),
        ('11','11'),
        ('12-a','12-a'),
        ('12-b','12-b'))
    name = models.CharField(max_length=100)
    regno = models.CharField(max_length=10,blank=True,null=False,unique=True,validators=[RegexValidator(regex=r'^(aik|AIK)\d{2}(cs|CS)\d{3}$',message='Enter a valid registration number.')] )
    batch = models.CharField(choices=batches,default='9',max_length=10)
    points = models.IntegerField(default=0)
    teacher = models.ForeignKey(Teacher,default=None,on_delete=models.SET_DEFAULT,null=True,blank=True)
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.regno:
            self.regno = self.regno.lower()  # Convert regno to lowercase before saving
        super().save(*args, **kwargs)


    def __str__(self):
        return(self.name)

class StudentRequest(models.Model):
    batches=(
        ('9','9'),
        ('10','10'),
        ('11','11'),
        ('12-a','12-a'),
        ('12-b','12-b'))
    name = models.CharField(max_length=100)
    regno = models.CharField(max_length=20,blank=True,null=False,unique=True,validators=[RegexValidator(regex=r'^(aik|AIK)\d{2}(cs|CS)\d{3}$',message='Enter a valid registration number.')])
    batch = models.CharField(choices=batches,default='9',max_length=10)
    points = models.IntegerField(default=0)
    teacher = models.ForeignKey(Teacher,default=None,on_delete=models.SET_DEFAULT,null=True,blank=True)
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    
    def save(self, *args, **kwargs):
        if self.regno:
            self.regno = self.regno.lower()  # Convert regno to lowercase before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return(self.name)

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Subcategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    max = models.IntegerField()
    has_levels = models.BooleanField(default=False)
    additional = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
class Level(models.Model):
    levelname = models.CharField(max_length=100,default='')
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    points_awarded = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Level {self.levelname} for {self.subcategory}"

class Achievement(models.Model):
    prize = models.CharField(max_length=20)
    level = models.ManyToManyField(Level,related_name='achievements')
    points_awarded=models.IntegerField(default=0)

    def __str__(self):
        return f"{self.prize} for {', '.join(str(level) for level in self.level.all())}"

class Activity(models.Model):
    name = models.CharField(max_length=100)
    level = models.ForeignKey(Level,default=None,blank=True, on_delete=models.CASCADE)
    start_date = models.DateField(default=None,blank=True)
    end_date = models.DateField(default=None,blank = True)
    approved_status = models.BooleanField(default=False)
    certificate = models.FileField(upload_to='certificates/',default=None,blank=True)
    student = models.ForeignKey(Student,on_delete=models.CASCADE,blank=True,default=None)
    points_obtained = models.IntegerField(default=0)
    additional_obtained = models.IntegerField(default=0)
    achievement = models.ForeignKey(Achievement,default=None,blank=True,null=True, on_delete=models.CASCADE)
    def delete(self, *args, **kwargs):
        # Delete the associated certificate file from the filesystem
        if self.certificate:
            # Get the file path
            certificate_path = self.certificate.path
            # Delete the file if it exists
            if os.path.exists(certificate_path):
                os.remove(certificate_path)
        # Call the superclass delete method to delete the Activity instance
        super().delete(*args, **kwargs)
    def __str__(self):
        return self.name

class Notif(models.Model):
    head = models.CharField(max_length=100)
    body = models.TextField()
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.head
        
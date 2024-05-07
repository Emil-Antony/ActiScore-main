from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import CustomUser, Student, Category, Subcategory, Activity, Level

class CustomUserCreationForm(UserCreationForm):
    username=forms.CharField(
        widget= forms.TextInput(
            attrs={
                "class": "formuser"
            }
        )
    )
    password1=forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "formpass"
            }
        )
    )
    password2=forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "formpass2"
            }
        )
    )
    regno = forms.CharField(max_length=20,validators=[RegexValidator(regex=r'^(aik|AIK)\d{2}(cs|CS)\d{3}$',message='Enter a valid registration number.')])
    batch = forms.ChoiceField(choices=[('9', '9'), ('10', '10'), ('11', '11'), ('12-a', '12-a'),('12-b', '12-b')],initial='')

    class Meta:
        model=CustomUser
        fields=('username','regno','batch','password1','password2',)


class LoginForm(forms.Form):
    username= forms.CharField(
        widget= forms.TextInput(
            attrs={
                "class": "formc"
            }
        )
    )
    password=forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "formc"
            }
        )
    )

class AddActivity(forms.ModelForm):
    # category = forms.ModelChoiceField(queryset=Category.objects.all())
    # subcategory = forms.ModelChoiceField(queryset=Subcategory.objects.none())

    class Meta:
        model = Activity
        fields = ['name','level', 'start_date', 'end_date', 'certificate']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'level': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'certificate': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'application/pdf'})
        }

class teacherUpdateForm(forms.ModelForm):
    new_password = forms.CharField(required=False, widget=forms.PasswordInput)
    confirm_password = forms.CharField(required=False, widget=forms.PasswordInput)
    name=forms.CharField(required=False,initial='')

    class Meta:
        model = User
        fields = ['username', 'name', 'new_password', 'confirm_password']

class studentUpdateForm(forms.ModelForm):
    new_password = forms.CharField(required=False, widget=forms.PasswordInput)
    confirm_password = forms.CharField(required=False, widget=forms.PasswordInput)
    name=forms.CharField(required=False,initial='')
    regno= forms.CharField(required=False,initial='',validators=[RegexValidator(regex=r'^(aik|AIK)\d{2}(cs|CS)\d{3}$',message='Enter a valid registration number.')])

    class Meta:
        model = User
        fields = ['username', 'name', 'regno','new_password', 'confirm_password']
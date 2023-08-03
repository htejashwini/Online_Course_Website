from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from .models import User, Student, Teacher, Content, Course

class UserSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'is_teacher', 'is_student')

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ('email', 'username')

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ('email', 'username')

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'description', 'price']

class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['title', 'description', 'video_url']

class CustomPasswordResetForm(PasswordResetForm):
    class Meta:
        model = User
        fields = ('email')
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    subscribed_courses = models.ManyToManyField('Course', related_name='subscribed_students', blank=True)
    
    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"

    def __str__(self):
        return self.email

class Student(models.Model):
    student_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='students')
    email = models.EmailField(unique=True, default=None)
    username = models.CharField(max_length = 25, default=None)

    def __str__(self):
        return self.student_id.email

class Teacher(models.Model):
    teacher_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='teachers')
    email = models.EmailField(unique=True, default=None)
    username = models.CharField(max_length = 25, default=None)

    def __str__(self):
        return self.teacher_id.email  
    
class Course(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    ratings = models.FloatField(default=0.0)
    total_ratings = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
    
class Content(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    video_url = models.URLField()
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class Payment(models.Model):
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    teacher_id = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    payment_price = models.IntegerField(null=True)
    invoice_number = models.CharField(max_length=100,null=True)

    def __str__(self):
        return f"{self.student_id}{self.course_id}{self.payment_price}{self.date}"
    
class CourseRating(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=0, choices=((1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('course', 'student')
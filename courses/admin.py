from django.contrib import admin
from courses.models import Student, Teacher, User, CourseRating, Content, Course, Payment

admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(User)
admin.site.register(CourseRating)
admin.site.register(Course)
admin.site.register(Content)
admin.site.register(Payment)

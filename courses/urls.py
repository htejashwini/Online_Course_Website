from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetView

urlpatterns = [
    path('', views.index, name = 'index'),
    path('signup/', views.signup, name='signup'),
    path('user_login/', views.user_login, name='user_login'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),

    path('reset_password/', CustomPasswordResetView.as_view(template_name="reset_password.html"), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="reset_password_sent.html") ,name ="password_reset_done" ),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_form.html") ,name="password_reset_confirm"),
    path('reset_password_completed/', auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_done.html"),name ="password_reset_complete" ),

    path('logout/', views.logout, name='logout'),
    # path('verify/otp/', views.verify_otp, name='verify_otp'),
    # path('verify/otp/verify/', views.verify_otp, name='verify_otp_verify'),

    path('create_course/', views.create_course, name='create_course'),
    path('update_course/<int:pk>/', views.update_course, name='update_course'),
    path('delete_course/<int:pk>/', views.delete_course, name='delete_course'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('course_details/<int:pk>/', views.course_details, name='course_details'),

    path('add_content/<int:course_pk>/', views.add_content, name='add_content'),
    path('delete_content/<int:course_pk>/<int:content_pk>/', views.delete_content, name='delete_content'),
    path('edit_content/<int:course_pk>/<int:content_pk>/', views.edit_content, name='edit_content'),

    path('teacher_dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('view_enrolled_students/<int:pk>/', views.view_enrolled_students, name='view_enrolled_students'),

    path('checkout/<int:pk>/', views.checkout, name='checkout'),
    path('payment_completed/', views.payment_completed, name='payment_completed'),
    path('payment_failed/', views.payment_failed, name='payment_failed'),
]



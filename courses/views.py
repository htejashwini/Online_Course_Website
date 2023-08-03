from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout, get_user_model
from .forms import ContentForm, CourseForm, CustomPasswordResetForm, UserSignupForm
from OCS import settings
import random
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from .models import Content, Course, Student, Teacher, Payment, CourseRating
from django.contrib.auth.decorators import login_required
import paypalrestsdk
from django.utils import timezone
from django.contrib.auth.hashers import check_password
import uuid
from datetime import date, datetime
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import views as auth_views
from django.db.models import Avg
from django.core.exceptions import ObjectDoesNotExist
User = get_user_model()

@csrf_exempt
def verify_otp(request):    
    if request.method == "POST":
        registration_data = request.session.get('registration_data')
        is_student = request.session.get('is_student')
        is_teacher = request.session.get('is_teacher')
        otp = request.session.get('signup_otp')
        userotp = request.POST.get('otp')
        email = registration_data['email']

        if userotp == str(otp):
            del request.session['signup_otp']
            del request.session['registration_data'] 

            username = registration_data['email']
            user = User.objects.create_user(
                username=username,
                password='',
                email = email,    
            )
            if is_student:
                user.is_student = True
                user.save()
                Student.objects.create(
                    student_id=user,
                    email=email,
                    username=email,
                )
            elif is_teacher:
                user = User.objects.get(username=email)
                teacher = Teacher.objects.create(
                    teacher_id=user,
                    email=email,
                    username = email,
                )
                user.is_teacher = True
                user.save()
                teacher.save()
            messages.success(request, 'OTP verified successfully. You are can login.')
            return redirect('user_login')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect('verify_otp')
    else:
        email = request.GET.get('email')
        otp = request.GET.get('otp')
        if email and otp:
            return render(request, 'verify_otp.html', {'email': email, 'otp': otp})
        else:
            return HttpResponseBadRequest("Invalid request.")

def send_otp_email(email, otp):
    try:
        subject = 'OTP Verification'
        message = f'Your OTP is: {otp}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)
        print(f"OTP email sent to: {email}")
    except Exception as e:
        print(f"An error occurred while sending the OTP email: {str(e)}")

def signup(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            cleaned_data = form.cleaned_data
            otp = random.randint(1000, 9999)
            request.session['registration_data'] = cleaned_data
            request.session['signup_otp'] = otp
            is_student = form.cleaned_data['is_student']
            is_teacher = form.cleaned_data['is_teacher']

            if is_teacher:
                send_otp_email(email, otp)
                request.session['is_teacher'] = True
                return redirect(reverse('verify_otp') + f'?email={email}&otp={otp}')
            elif is_student:
                send_otp_email(email, otp)
                request.session['is_student'] = True
                return redirect(reverse('verify_otp') + f'?email={email}&otp={otp}')
            else:
                return redirect('user_login')
        else:
            return render(request, 'signup.html', {'form': form})
    else:
        form = UserSignupForm()
    return render(request, 'signup.html', {'form': form})


def logout(request):
    auth_logout(request)
    return redirect('index')


def user_login(request):
    if request.method == 'POST':
        #import pdb; pdb.set_trace()
        username = request.POST.get('email')
        password = request.POST.get('password')
        print(f"Username: {username}, Password: {password}")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
        
        if user is not None:
            user.set_password(password)
            user.save()
            if check_password(password, user.password): 
                auth_login(request, user)
                return redirect('index')
            else:
                error_message = 'Invalid username or password. Please try again.'
        else:
            error_message = 'The user with this email is not registered.'
        
        return render(request, 'user_login.html', {'error_message': error_message})
    password_reset_form = CustomPasswordResetForm()
    return render(request, 'user_login.html')

@login_required
def create_course(request):
    if request.user.is_teacher:
        if request.method == 'POST':
            form = CourseForm(request.POST)
            if form.is_valid():
                course = form.save(commit=False)
                course.teacher = Teacher.objects.get(teacher_id=request.user)
                course.save()

                enrolled_students = Student.objects.filter(payment__course_id=course)

                for student in enrolled_students:
                    send_mail(
                        'Course is updated',
                       f'Dear student,\n\nThe course as been modified "{course.name}".\n\nCheck it out now!\n\nBest regards,\nThe Teacher',
                        'sender@example.com', 
                        [student.email],
                        fail_silently=True,
                    )
                return redirect('teacher_dashboard')
        else:
            form = CourseForm()
    return render(request, 'create_course.html', {'form': form})


def update_course(request, pk):
    course = Course.objects.get(id=pk)
    form = CourseForm(instance=course)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('teacher_dashboard')
    else:
        form = CourseForm(instance=course)
    return render(request, 'update_course.html', {'form': form, 'course': course})


def delete_course(request, pk):
    try:
        obj = Course.objects.get(id=pk)
    except ObjectDoesNotExist:
        messages.error(request, 'Course not found. It may have already been deleted.')
        return redirect('teacher_dashboard')  # Or any other appropriate URL

    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Course deleted successfully.')
        return redirect('teacher_dashboard')

    return render(request, 'delete.html', {'course': obj})

def dashboard(request):
    try:
        student = Student.objects.get(student_id=request.user)
    except ObjectDoesNotExist:
        student = Student.objects.create(student_id=request.user, email=request.user.email, username=request.user.email)

    search_query = request.GET.get('search')
    if search_query:
        courses = Course.objects.filter(name__icontains=search_query)
    else:
        courses = Course.objects.all()

    sort_option = request.GET.get('sort')
    if sort_option == 'price':
        courses = courses.order_by('price')
    elif sort_option == 'ratings':
        courses = courses.order_by('-ratings')
    elif sort_option == 'video_time':
        courses = courses.order_by('total_video_time')

    student = Student.objects.get(student_id=request.user)
    enrolled_courses = student.payment_set.all().values_list('course_id', flat=True)

    for course in courses:
        course.ratings = CourseRating.objects.filter(course=course).aggregate(Avg('rating'))['rating__avg']
        course.total_ratings = CourseRating.objects.filter(course=course).count()

    context = {
        'courses': courses,
        'enrolled_courses': enrolled_courses,
    }

    return render(request, 'dashboard.html', context)

def course_details(request, pk):
    course = get_object_or_404(Course, pk=pk)
    contents = Content.objects.filter(course=course, deleted=False)
    context = {
        'course': course,
        'contents': contents,
    }
    return render(request, 'course_details.html', context)

def add_content(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    form = ContentForm()

    if request.user.is_teacher:
        if request.method == 'POST':
            form = ContentForm(request.POST)
            if form.is_valid():
                content = form.save(commit=False)
                content.course = course
                content.save()

                enrolled_students = Student.objects.filter(payment__course_id=course)

                for student in enrolled_students:
                    send_mail(
                        'New Course Content Added',
                       f'Dear student,\n\nNew content has been added to the course "{course.name}".\n\nCheck it out now!\n\nBest regards,\nThe Teacher',
                        'sender@example.com', 
                        [student.email],
                        fail_silently=True,
                    )

                return redirect('course_details', pk=course.pk)
        
    return render(request, 'content_form.html', {'form': form, 'course': course})

def delete_content(request, course_pk, content_pk):
    course = get_object_or_404(Course, pk=course_pk)
    content = get_object_or_404(Content, pk=content_pk, course=course)

    if request.method == 'POST':
        content.delete()
        messages.success(request, 'Content deleted successfully.')
        return redirect('course_details', pk=course.pk)

    return render(request, 'delete.html', {'course': course, 'content': content})


def edit_content(request, course_pk, content_pk):
    course = get_object_or_404(Course, pk=course_pk)
    content = get_object_or_404(Content, pk=content_pk, course=course)

    if request.user.is_teacher:
        if request.method == 'POST':
            form = ContentForm(request.POST, instance=content)
            if form.is_valid():
                form.save()
                return redirect('course_details', pk=course.pk)
        else:
            form = ContentForm(instance=content)
    return render(request, 'content_form.html', {'form': form, 'course': course, 'content': content})

def view_enrolled_students(request, pk):
    course = get_object_or_404(Course, pk=pk)
    enrolled_students = Payment.objects.filter(course_id=course)

    return render(request, 'enrolled_students.html', {'course': course, 'enrolled_students': enrolled_students})

def teacher_dashboard(request):
    if request.user.is_authenticated and request.user.is_teacher:
        teacher = get_object_or_404(Teacher, teacher_id=request.user)
        courses = Course.objects.filter(teacher=teacher)

        for course in courses:
            course.ratings = CourseRating.objects.filter(course=course).aggregate(Avg('rating'))['rating__avg']
            course.total_ratings = CourseRating.objects.filter(course=course).count()

        return render(request, 'teacher_dashboard.html', {'courses': courses})
    else:
        return redirect('user_login')

def student_dashboard(request):
    if request.user.is_authenticated and request.user.is_student:
        student = Student.objects.get(student_id=request.user)
        enrolled_courses = Course.objects.filter(payment__student_id=student)

        if request.method == 'POST':
            course_id = request.POST.get('course_id')
            rating = int(request.POST.get('rating'))
            if 1 <= rating <= 5:
                course = Course.objects.get(id=course_id)
                course_rating, created = CourseRating.objects.get_or_create(
                    course=course,
                    student=request.user,
                )
                course_rating.rating = rating
                course_rating.save()
                course.total_ratings = CourseRating.objects.filter(course=course).count()
                course.ratings = CourseRating.objects.filter(course=course).aggregate(Avg('rating'))['rating__avg']
                course.save()

        return render(request, 'student_dashboard.html', {'courses': enrolled_courses})
    else:
        return redirect('user_login')
    
def generate_invoice_number(prefix):
    unique_id = uuid.uuid4().hex[:6]
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    invoice_number = '{}-{}-{}'.format(prefix, timestamp, unique_id)
    return invoice_number

@login_required
def checkout(request, pk):
    course = get_object_or_404(Course, pk=pk)
    content = Content.objects.filter(course_id=course)

    host = request.get_host()
    invoice_number = generate_invoice_number('INV')

    # Create a PayPal Payment instance
    paypalrestsdk.configure({
        "mode": "sandbox" if settings.DEBUG else "live",
        "client_id": settings.PAYPAL_CLIENT_ID,
        "client_secret": settings.PAYPAL_CLIENT_SECRET,
    })

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal",
        },
        "redirect_urls": {
            "return_url": "http://{}{}".format(host, reverse('payment_completed')),
            "cancel_url": "http://{}{}".format(host, reverse('payment_failed')),
        },
        "transactions": [{
            "amount": {
                "total": course.price,
                "currency": "USD",
            },
            "description": course.name,
            "invoice_number": invoice_number,
        }]
    })

    # Store course information in session
    request.session['checkout_course_id'] = course.id
    request.session['invoice_number'] = invoice_number
    request.session['checkout_course_price'] = course.price

    # Create the PayPal payment URL and redirect user to PayPal
    if payment.create():
        for link in payment.links:
            if link.method == "REDIRECT":
                redirect_url = str(link.href)
                return redirect(redirect_url)
    else:
        messages.error(request, "Payment creation failed.")
        return redirect('dashboard', pk=pk)

    context = {
        'course': course,
        'content': content,
    }
    return render(request, 'dashboard.html', context)

@login_required
def payment_completed(request):
    if request.user.is_authenticated:
        std_id = request.user.id
    if request.method == "GET":
        try:
            student = Student.objects.get(student_id=std_id)
            course_id = request.session.get('checkout_course_id')
            invoice_number = request.session.get('invoice_number')
            course_price = request.session.get('checkout_course_price')

            course = get_object_or_404(Course, id=course_id)
            payment = Payment.objects.create(
                student_id=student,
                teacher_id=course.teacher,
                course_id=course,
                date=timezone.now(),
                payment_price=course_price,
                invoice_number=invoice_number
            )
            payment.save()

            # Clear the session data
            del request.session['checkout_course_id']
            del request.session['invoice_number']
            del request.session['checkout_course_price']
        except Exception as e:
            print("Exception occurred while creating Payment instance:", str(e))
            course = None
            invoice_number = None

    return render(request, 'payment_completed.html', {'course': course, 'date': date, 'invoice_number': invoice_number})

def payment_failed(request):
    return render(request, 'payment_failed.html')

def index(request):
    return render(request, 'index.html')

class CustomPasswordResetView(auth_views.PasswordResetView):
    form_class = PasswordResetForm

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        # Add your custom filtering logic here
        if not User.objects.filter(email=email).exists():
            messages.error(self.request, 'Email address is not registered.')
            return self.form_invalid(form)
        return super().form_valid(form)
    

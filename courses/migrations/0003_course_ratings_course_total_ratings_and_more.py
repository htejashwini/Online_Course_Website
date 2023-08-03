# Generated by Django 4.2.3 on 2023-07-20 20:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_payment_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='ratings',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='course',
            name='total_ratings',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='subscribed_courses',
            field=models.ManyToManyField(blank=True, related_name='subscribed_students', to='courses.course'),
        ),
        migrations.CreateModel(
            name='CourseRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('course', 'student')},
            },
        ),
    ]
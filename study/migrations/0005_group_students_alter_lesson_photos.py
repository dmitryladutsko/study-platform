# Generated by Django 4.2.5 on 2023-10-10 09:53

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('study', '0004_alter_lesson_photos'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='students',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='photos',
            field=models.ManyToManyField(blank=True, to='study.lessonphoto'),
        ),
    ]

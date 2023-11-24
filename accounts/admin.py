from django.contrib import admin

from .models import Profile, Application


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "type"]


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ["email", "first_name", "last_name", "middle_name", "group_id"]


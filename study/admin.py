from django.contrib import admin

from .models import Group, Subject, Lesson, LessonPhoto, Test, Question, Answer, Try


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "owner"]


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ["name", "group"]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["name", "subject"]


@admin.register(LessonPhoto)
class LessonPhotoAdmin(admin.ModelAdmin):
    list_display = ["name", "owner"]


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ["name", "owner"]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["type", "text", "test"]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ["text", "correct", "question"]


@admin.register(Try)
class TryAdmin(admin.ModelAdmin):
    list_display = ["score", "user", "test"]


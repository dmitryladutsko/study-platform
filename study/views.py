from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView

from accounts.forms import UserEditForm, UserCreateForm
from accounts.models import Application
from .decorators.is_admin import admin_only
from .decorators.is_not_student import not_student
from .decorators.is_teacher import teacher_only
from .forms import AdminProfileEditForm, GroupForm, SubjectForm, LessonForm, \
    AdminTestForm, QuestionForm, AnswerForm, LessonPhotoForm
from .models import Group, Subject, Lesson, LessonPhoto, Test, Question, Answer, Try


class IndexView(LoginRequiredMixin, View):
    menu = {
        "admin": {
            "Пользователи": {
                "Учителя": reverse_lazy("teachers"),
                "Ученики": reverse_lazy("students"),
            },
            "Заявки": reverse_lazy("applications"),
            "Группы": reverse_lazy("groups"),
            "Предметы": reverse_lazy("subjects"),
            "Уроки": reverse_lazy("lessons"),
            "Тесты": reverse_lazy("tests"),
        },
        "teacher": {
            "Моя группа": reverse_lazy("my-group"),
            "Предметы": reverse_lazy("my-subjects"),
            "Уроки": reverse_lazy("my-lessons"),
            "Фото": reverse_lazy("my-photos"),
            "Тесты": reverse_lazy("my-tests"),
        }
    }

    def get(self, request, *args, **kwargs):

        user = request.user
        if user.profile.type == 1:
            return render(request, "study/index.html", {"menu": self.menu["admin"]})
        if user.profile.type == 2:
            return render(request, "study/index.html", {"menu": self.menu["teacher"]})
        if user.profile.type == 3:
            return render(
                request,
                "study/index.html",
                {
                    "menu": {subject.name: reverse_lazy("student-subject", kwargs={"pk": subject.pk})
                             for subject in Subject.objects.filter(group=user.group_set.first())}
                }
            )


@method_decorator(admin_only, name="dispatch")
class TeachersListView(LoginRequiredMixin, ListView):
    model = User
    context_object_name = "objects"
    template_name = "study/teachers.html"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(profile__type=2)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


@method_decorator(admin_only, name="dispatch")
class TeacherEditView(LoginRequiredMixin, View):

    def post(self, request, pk, *args, **kwargs):
        teacher = get_object_or_404(User, pk=pk)
        user_form = UserEditForm(instance=teacher, data=request.POST)
        profile_form = AdminProfileEditForm(instance=teacher.profile, data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.username = user.email
            user.save()

            group = profile_form.cleaned_data.get("group")
            profile = profile_form.save()

            if group.owner and group.owner != user:
                messages.error(request, f"У группы {group.name} уже есть учитель!")
                return redirect(reverse("teacher", kwargs={"pk": pk}))

            group.owner = profile.user
            group.save()

            messages.success(request, "Пользователь успешно изменен!")

        return redirect(reverse("teacher", kwargs={"pk": pk}))

    def get(self, request, pk, *args, **kwargs):
        teacher = get_object_or_404(User, pk=pk)
        user_form = UserEditForm(instance=teacher)
        profile_form = AdminProfileEditForm(instance=teacher.profile)

        teacher_group = teacher.study_groups.first()
        groups = Group.objects.all()

        return render(request, "study/teacher-edit.html", {
            "user_form": user_form,
            "profile_form": profile_form,
            "teacher_group": teacher_group,
            "groups": groups,
            "teacher": teacher,
        })


@method_decorator(admin_only, name="dispatch")
class TeacherCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user_form = UserCreateForm(request.POST)
        profile_form = AdminProfileEditForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():

            new_user = user_form.save(commit=False)
            new_user_password = user_form.cleaned_data.get("password")
            new_user.set_password(new_user_password)
            new_user.username = new_user.email
            new_user.save()

            profile = new_user.profile
            profile.middle_name = profile_form.cleaned_data.get("middle_name")
            profile.type = 2
            profile.save()

            group = profile_form.cleaned_data.get("group")
            if group:
                group.owner = new_user
                group.save()

            try:
                send_mail(
                    "Данные для входа",
                    f"Логин - ваша почта: {new_user.email}\nПароль: {new_user_password}",
                    settings.EMAIL_HOST_USER,
                    [new_user.email])
            except Exception as err:
                print(err)
                messages.error(request, "Не получилось отправить письмо на почту")

            messages.success(request, "Пользователь успешно создан!")
            return redirect(reverse("teachers"))

        return redirect(reverse("teacher-add"))

    def get(self, request, *args, **kwargs):
        user_form = UserCreateForm()
        profile_form = AdminProfileEditForm()
        groups = Group.objects.all()
        return render(request, "study/teacher-add.html", {
            "user_form": user_form,
            "profile_form": profile_form,
            "groups": groups,
        })


@admin_only
def delete_teacher(request, pk):

    teacher = get_object_or_404(User, pk=pk)
    username = teacher.username
    teacher.delete()
    messages.success(request, f"Учитель {username} удален!")

    return redirect(reverse("teachers"))


@method_decorator(admin_only, name="dispatch")
class StudentsListView(LoginRequiredMixin, ListView):
    model = User
    context_object_name = "objects"
    template_name = "study/students.html"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(profile__type=3)


@method_decorator(admin_only, name="dispatch")
class StudentEditView(LoginRequiredMixin, View):

    def post(self, request, pk, *args, **kwargs):
        student = get_object_or_404(User, pk=pk)
        user_form = UserEditForm(instance=student, data=request.POST)
        profile_form = AdminProfileEditForm(instance=student.profile, data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.username = user.email
            user.save()

            group = profile_form.cleaned_data.get("group")
            user_group = user.group_set.first()
            profile_form.save()

            if group:
                if not(user in group.students.all()):
                    if user_group:
                        user_group.students.remove(user)
                    group.students.add(user)
            else:
                if user_group:
                    user_group.students.remove(user)

            messages.success(request, "Пользователь успешно изменен!")

        return redirect(reverse("student", kwargs={"pk": pk}))

    def get(self, request, pk, *args, **kwargs):
        student = get_object_or_404(User, pk=pk)
        user_form = UserEditForm(instance=student)
        profile_form = AdminProfileEditForm(instance=student.profile)

        student_group = student.group_set.first()
        groups = Group.objects.all()

        return render(request, "study/student-edit.html", {
            "user_form": user_form,
            "profile_form": profile_form,
            "student_group": student_group,
            "groups": groups,
            "student": student,
        })


@method_decorator(admin_only, name="dispatch")
class StudentCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user_form = UserCreateForm(request.POST)
        profile_form = AdminProfileEditForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():

            new_user = user_form.save(commit=False)
            new_user_password = user_form.cleaned_data.get("password")
            new_user.set_password(new_user_password)
            new_user.username = new_user.email
            new_user.save()

            profile = new_user.profile
            profile.middle_name = profile_form.cleaned_data.get("middle_name")
            profile.type = 3
            profile.save()

            group = profile_form.cleaned_data.get("group")
            if group:
                group.students.add(new_user)

            try:
                send_mail(
                    "Данные для входа",
                    f"Логин - ваша почта: {new_user.email}\nПароль: {new_user_password}",
                    settings.EMAIL_HOST_USER,
                    [new_user.email])
            except Exception as err:
                print(err)
                messages.error(request, "Не получилось отправить письмо на почту")

            messages.success(request, "Пользователь успешно создан!")
            return redirect(reverse("students"))

        return redirect(reverse("student-add"))

    def get(self, request, *args, **kwargs):
        user_form = UserCreateForm()
        profile_form = AdminProfileEditForm()
        groups = Group.objects.all()
        return render(request, "study/student-add.html", {
            "user_form": user_form,
            "profile_form": profile_form,
            "groups": groups,
        })


@admin_only
def delete_student(request, pk):

    student = get_object_or_404(User, pk=pk)
    username = student.username
    student.delete()
    messages.success(request, f"Ученик {username} удален!")

    return redirect(reverse("students"))


@method_decorator(admin_only, name="dispatch")
class ApplicationsListView(LoginRequiredMixin, ListView):
    model = Application
    context_object_name = "objects"
    template_name = "study/applications.html"


@method_decorator(admin_only, name="dispatch")
class ApplicationView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        application = get_object_or_404(Application, pk=pk)
        user_form = UserCreateForm(initial={
            "first_name": application.first_name,
            "last_name": application.last_name,
            "email": application.email
        })
        profile_form = AdminProfileEditForm(initial={
            "middle_name": application.middle_name,
            "group": application.group_id
        })
        groups = Group.objects.all()

        if not(Group.objects.filter(id=application.group_id).first()):
            messages.error(request, "Пользователь указал несуществующую группу!")

        return render(request, "study/application.html", {
            "user_form": user_form,
            "profile_form": profile_form,
            "groups": groups,
            "application": application
        })


@admin_only
def delete_application(request, pk):

    application = get_object_or_404(Application, pk=pk)
    email = application.email
    application.delete()
    messages.success(request, f"Заявка от {email} удален!")

    return redirect(reverse("applications"))


@method_decorator(admin_only, name="dispatch")
class GroupsListView(LoginRequiredMixin, ListView):
    model = Group
    context_object_name = "objects"
    template_name = "study/group/list.html"


@method_decorator(admin_only, name="dispatch")
class GroupEditView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        group = get_object_or_404(Group, pk=pk)
        form = GroupForm(instance=group, data=request.POST)
        if form.is_valid():
            new_owner = form.cleaned_data.get("owner")

            if new_owner == group.owner:
                form.save()
            elif new_owner:
                if not (new_owner.study_groups.first()):
                    group = form.save(commit=False)
                    group.owner = new_owner
                    group.save()
                else:
                    form.save()
                    messages.error(
                        request,
                        f"Учитель {new_owner} уже является владельцем группы {new_owner.study_groups.first()}"
                    )
            else:
                group = form.save(commit=False)
                group.owner = None
                group.save()

            messages.success(request, "Группа успешно изменена!")
        return redirect(reverse("group", kwargs={"pk": pk}))

    def get(self, request, pk, *args, **kwargs):
        group = get_object_or_404(Group, pk=pk)
        form = GroupForm(instance=group)
        teachers = User.objects.filter(profile__type=2)

        return render(request, "study/group/edit.html", {"form": form, "group": group, "teachers": teachers})


@method_decorator(admin_only, name="dispatch")
class GroupCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = GroupForm(request.POST)
        if form.is_valid():
            owner = form.cleaned_data.get("owner")
            if owner:
                if owner.study_groups.first():
                    messages.error(request, f"Учитель {owner} уже владеет группой {owner.study_groups.first()}!")
                    return redirect(reverse("group-add"))
                new_group = form.save(commit=False)
                new_group.owner = owner
                new_group.save()
            else:
                form.save()

            messages.success(request, "Группа успешно создана!")

        return redirect(reverse("groups"))

    def get(self, request, *args, **kwargs):
        form = GroupForm()
        teachers = User.objects.filter(profile__type=2)
        return render(request, "study/group/add.html", {"form": form, "teachers": teachers})


@admin_only
def delete_group(request, pk):

    group = get_object_or_404(Group, pk=pk)
    name = group.name
    group.delete()
    messages.success(request, f"Группа {name} удалена!")

    return redirect(reverse("groups"))


@method_decorator(admin_only, name="dispatch")
class SubjectsListView(LoginRequiredMixin, ListView):
    model = Subject
    context_object_name = "objects"
    template_name = "study/subjects/list.html"


@method_decorator(admin_only, name="dispatch")
class SubjectEditView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        subject = get_object_or_404(Subject, pk=pk)
        form = SubjectForm(instance=subject, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Предмет успешно изменен")

        return redirect(reverse("subject", kwargs={"pk": pk}))

    def get(self, request, pk, *args, **kwargs):
        subject = get_object_or_404(Subject, pk=pk)
        form = SubjectForm(instance=subject)
        groups = Group.objects.all()
        return render(request, "study/subjects/edit.html", {"form": form, "subject": subject, "groups": groups})


@method_decorator(admin_only, name="dispatch")
class SubjectCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = SubjectForm(data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Предмет успешно создан")

        return redirect(reverse("subjects"))

    def get(self, request, *args, **kwargs):
        form = SubjectForm()
        groups = Group.objects.all()
        return render(request, "study/subjects/add.html", {"form": form, "groups": groups})


@not_student
def delete_subject(request, pk):

    subject = get_object_or_404(Subject, pk=pk)
    name = subject.name
    subject.delete()
    messages.success(request, f"Предмет {name} удален!")

    return redirect(reverse("subjects"))


@method_decorator(admin_only, name="dispatch")
class LessonsListView(LoginRequiredMixin, ListView):
    model = Lesson
    context_object_name = "objects"
    template_name = "study/lesson/list.html"


@method_decorator(admin_only, name="dispatch")
class LessonEditView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        lesson = get_object_or_404(Lesson, pk=pk)
        form = LessonForm(instance=lesson, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Урок изменен!")
        return redirect(reverse("lesson", kwargs={"pk": pk}))

    def get(self, request, pk, *args, **kwargs):
        lesson = get_object_or_404(Lesson, pk=pk)
        form = LessonForm(instance=lesson)
        subjects = Subject.objects.all()
        tests = Test.objects.all()
        photos = LessonPhoto.objects.filter(owner=lesson.subject.group.owner)

        return render(request, "study/lesson/edit.html", {
            "form": form,
            "lesson": lesson,
            "subjects": subjects,
            "tests": tests,
            "photos": photos
        })


@method_decorator(admin_only, name="dispatch")
class LessonCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = LessonForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Урок создан!")
        return redirect(reverse("lessons"))

    def get(self, request, *args, **kwargs):

        form = LessonForm()
        subjects = Subject.objects.all()
        tests = Test.objects.all()
        photos = LessonPhoto.objects.all()

        return render(request, "study/lesson/add.html", {
            "form": form,
            "subjects": subjects,
            "tests": tests,
            "photos": photos
        })


@not_student
def delete_lesson(request, pk):

    lesson = get_object_or_404(Lesson, pk=pk)
    name = lesson.name
    lesson.delete()
    messages.success(request, f"Урок {name} удален!")

    return redirect(reverse("lessons"))


@method_decorator(not_student, name="dispatch")
class TestsListView(LoginRequiredMixin, ListView):
    model = Test
    context_object_name = "objects"
    template_name = "study/test/list.html"


@method_decorator(not_student, name="dispatch")
class TestEditView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        test = get_object_or_404(Test, pk=pk)
        form = AdminTestForm(instance=test, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Тест изменен!")
        return redirect(reverse("test", kwargs={"pk": pk}))

    def get(self, request, pk, *args, **kwargs):
        test = get_object_or_404(Test, pk=pk)
        form = AdminTestForm(instance=test)
        teachers = User.objects.filter(profile__type=2)

        return render(request, "study/test/edit.html", {
            "form": form,
            "test": test,
            "teachers": teachers,
        })


@method_decorator(not_student, name="dispatch")
class TestCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = AdminTestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Тест создан!")
        elif request.user.profile.type == 2:
            name = request.POST.get("name")
            Test.objects.create(owner=request.user, name=name)
            messages.success(request, "Тест создан!")
            return redirect(reverse("my-tests"))

        return redirect(reverse("tests"))

    def get(self, request, *args, **kwargs):
        form = AdminTestForm()
        teachers = User.objects.filter(profile__type=2)

        return render(request, "study/test/add.html", {
            "form": form,
            "teachers": teachers,
        })


@not_student
def delete_test(request, pk):

    test = get_object_or_404(Test, pk=pk)
    name = test.name
    test.delete()
    messages.success(request, f"Тест {name} удален!")
    if request.user.profile.type == 1:
        return redirect(reverse("tests"))
    return redirect(reverse("my-tests"))


@method_decorator(not_student, name="dispatch")
class TestQuestionCreateView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        form = QuestionForm(request.POST)
        if form.is_valid():
            new_question = form.save(commit=False)
            new_question.test = get_object_or_404(Test, pk=pk)
            new_question.save()
            messages.success(request, "Вопрос создан!")

        return redirect(reverse("test", kwargs={"pk": pk}))

    def get(self, request, *args, **kwargs):
        form = QuestionForm()
        return render(request, "study/test/question-add.html", {
            "form": form,
            "types": Question.Type.choices
        })


@not_student
def delete_question(request, test_pk, question_pk):

    question = get_object_or_404(Question, pk=question_pk)
    name = question.text
    question.delete()
    messages.success(request, f"Вопрос {name} удален!")

    return redirect(reverse("test", kwargs={"pk": test_pk}))


@method_decorator(not_student, name="dispatch")
class TestQuestionEditView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        question = get_object_or_404(Question, pk=kwargs["question_pk"])
        form = QuestionForm(instance=question, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Вопрос изменен!")

        return redirect(reverse("test-question", kwargs=kwargs))

    def get(self, request, *args, **kwargs):
        question = get_object_or_404(Question, pk=kwargs["question_pk"])
        form = QuestionForm(instance=question)
        answer_form = AnswerForm()
        return render(request, "study/test/question.html", {
            "form": form,
            "answer_form": answer_form,
            "question": question,
        })


@not_student
def add_answer_variant(request, pk):
    if request.method == "POST":
        question = get_object_or_404(Question, pk=pk)
        form = AnswerForm(request.POST)
        if form.is_valid():
            new_answer = form.save(commit=False)
            new_answer.question = question
            new_answer.save()
            messages.success(request, "Добавлен вариант ответа")

        return redirect(reverse("test-question", kwargs={"question_pk": pk, "test_pk": question.test.pk}))
    else:
        return redirect(reverse("tests"))


@not_student
def add_correct_text_answer(request, pk):
    if request.method == "POST":
        question = get_object_or_404(Question, pk=pk)
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = question.answers.first()
            if answer:
                answer.text = form.cleaned_data.get("text")
                answer.save()
                messages.success(request, "Правильный ответ изменен")
            else:
                new_answer = form.save(commit=False)
                new_answer.question = question
                new_answer.save()
                messages.success(request, "Правильный ответ добавлен")

        return redirect(reverse("test-question", kwargs={"question_pk": pk, "test_pk": question.test.pk}))
    else:
        return redirect(reverse("tests"))


@not_student
def delete_answer(request, pk):

    answer = get_object_or_404(Answer, pk=pk)
    name = answer.text
    answer.delete()
    messages.success(request, f"Ответ {name} удален!")

    return HttpResponse("Answer delete successfully!")


@method_decorator(teacher_only, name="dispatch")
class MyGroupListView(LoginRequiredMixin, ListView):
    model = User
    context_object_name = "objects"
    template_name = "study/teacher/my_group.html"

    def get_queryset(self):
        group = self.request.user.study_groups.first()
        if group:
            students = group.students.all()
            return students
        return []


@method_decorator(teacher_only, name="dispatch")
class MyGroupCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = GroupForm(request.POST)
        if form.is_valid():
            new_group = form.save(commit=False)
            new_group.owner = request.user
            new_group.save()
            messages.success(request, "Ваша группа создана!")
            return redirect(reverse("my-group"))

        return redirect(reverse("my-group-create"))

    def get(self, request, *args, **kwargs):
        form = GroupForm()
        return render(request, "study/teacher/create-group.html", {"form": form})


def exclude_student(request, pk):
    student = get_object_or_404(User, pk=pk)
    group = request.user.study_groups.first()
    group.students.remove(student)
    messages.success(request, "Ученик был исключен")
    return redirect(reverse("my-group"))


@method_decorator(teacher_only, name="dispatch")
class MySubjectsListView(LoginRequiredMixin, ListView):
    model = Subject
    context_object_name = "objects"
    template_name = "study/teacher/my_subjects.html"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(group__owner=self.request.user)


@method_decorator(teacher_only, name="dispatch")
class MySubjectCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        group = request.user.study_groups.first()
        subject_name = request.POST.get("name")
        if not group:
            messages.error(request, "У вас нет своей группы!")
            return redirect(reverse("index"))

        Subject.objects.create(name=subject_name, group=group)
        messages.success(request, "Предмет создан!")
        return redirect(reverse("my-subjects"))

    def get(self, request, *args, **kwargs):
        form = SubjectForm()
        return render(request, "study/teacher/create-subject.html", {"form": form})


@method_decorator(teacher_only, name="dispatch")
class MySubjectEditView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        subject = get_object_or_404(Subject, pk=kwargs["pk"])
        form = SubjectForm(instance=subject, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Предмет изменен!")

        return redirect(reverse("my-subject", kwargs=kwargs))

    def get(self, request, *args, **kwargs):
        subject = get_object_or_404(Subject, pk=kwargs["pk"])
        form = SubjectForm(instance=subject)
        return render(request, "study/teacher/edit-subject.html", {"form": form, "subject": subject})


@method_decorator(teacher_only, name="dispatch")
class MyLessonsListView(LoginRequiredMixin, ListView):
    model = Lesson
    context_object_name = "objects"
    template_name = "study/teacher/my_lessons.html"

    def get_queryset(self):
        qs = super().get_queryset().filter(subject__group__owner=self.request.user)
        objects = {}
        for lesson in qs:
            subject = lesson.subject
            if subject in objects:
                objects[subject].append(lesson)
            else:
                objects[subject] = [lesson]
        return objects


@method_decorator(teacher_only, name="dispatch")
class MyLessonCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = LessonForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Урок создан")

        return redirect(reverse("my-lessons"))

    def get(self, request, *args, **kwargs):
        user = request.user
        form = LessonForm()
        tests = user.tests.all()
        photos = user.lesson_photos.all()
        subjects = user.study_groups.first().subjects.all()
        return render(request, "study/teacher/create-lesson.html", {
            "form": form,
            "tests": tests,
            "photos": photos,
            "subjects": subjects,
        })


@method_decorator(teacher_only, name="dispatch")
class MyLessonEditView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        lesson = get_object_or_404(Lesson, pk=kwargs["pk"])
        form = LessonForm(instance=lesson, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Урок изменен")

        return redirect(reverse("my-lesson", kwargs=kwargs))

    def get(self, request, *args, **kwargs):
        lesson = get_object_or_404(Lesson, pk=kwargs["pk"])
        user = request.user
        form = LessonForm(instance=lesson)
        tests = user.tests.all()
        photos = user.lesson_photos.all()
        subjects = user.study_groups.first().subjects.all()
        return render(request, "study/teacher/edit-lesson.html", {
            "form": form,
            "tests": tests,
            "photos": photos,
            "subjects": subjects,
            "lesson": lesson,
        })


@method_decorator(teacher_only, name="dispatch")
class MyPhotosView(LoginRequiredMixin, ListView):
    model = LessonPhoto
    context_object_name = "objects"
    template_name = "study/teacher/my_photos.html"

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


@method_decorator(teacher_only, name="dispatch")
class MyPhotoCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = LessonPhotoForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            new_photo = form.save(commit=False)
            new_photo.owner = request.user
            new_photo.save()
            messages.success(request, "Фото создано")

        return redirect(reverse("my-photos"))

    def get(self, request, *args, **kwargs):
        form = LessonPhotoForm()
        return render(request, "study/teacher/create-photo.html", {
            "form": form,
        })


@method_decorator(teacher_only, name="dispatch")
class MyPhotoEditView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        photo = get_object_or_404(LessonPhoto, pk=kwargs["pk"])
        form = LessonPhotoForm(instance=photo, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Фото изменено")

        return redirect(reverse("my-photo", kwargs=kwargs))

    def get(self, request, *args, **kwargs):
        photo = get_object_or_404(LessonPhoto, pk=kwargs["pk"])
        form = LessonPhotoForm(instance=photo)
        return render(request, "study/teacher/edit-photo.html", {
            "form": form,
            "photo": photo
        })


def delete_photo(request, pk):
    photo = get_object_or_404(LessonPhoto, pk=pk)
    name = photo.name
    photo.delete()
    messages.success(request, f"Фото {name} удалено")
    return HttpResponse("Ok")


class MyTestsListView(TestsListView):
    model = Test
    context_object_name = "objects"
    template_name = "study/test/list.html"

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class StudentSubjectView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        user = self.request.user
        subject = get_object_or_404(Subject, pk=kwargs["pk"])

        if not user.group_set.first():
            return HttpResponse("No permission")
        if user.group_set.first().pk != subject.group.pk:
            return HttpResponse("No permission")

        return render(request, "study/student/subject.html", {
            "subject": subject,
            "lessons": subject.lessons.all()
        })


class StudentLessonView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        user = self.request.user
        lesson = get_object_or_404(Lesson, pk=kwargs["pk"])

        if not user.group_set.first():
            return HttpResponse("No permission")
        if user.group_set.first().pk != lesson.subject.group.pk:
            return HttpResponse("No permission")

        return render(request, "study/student/lesson.html", {
            "lesson": lesson,
        })


class StudentTestView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = self.request.user
        test = get_object_or_404(Test, pk=kwargs["pk"])

        if not user.group_set.first():
            return HttpResponse("No permission")
        if user.group_set.first().owner != test.owner:
            return HttpResponse("No permission")

        score = test.calculate_score(request.POST)
        Try.objects.create(user=user, test=test, score=score)
        messages.success(request, f"Ваш балл составил {score}")

        return redirect(reverse("student-lesson", kwargs={"pk": test.lessons.first().pk}))

    def get(self, request, *args, **kwargs):
        user = self.request.user
        test = get_object_or_404(Test, pk=kwargs["pk"])

        if not user.group_set.first():
            return HttpResponse("No permission")
        if user.group_set.first().owner != test.owner:
            return HttpResponse("No permission")

        return render(request, "study/student/test.html", {
            "test": test,
        })
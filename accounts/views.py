from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import LoginForm, ApplicationForm, UserEditForm, ProfileEditForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db.utils import IntegrityError


class LoginView(View):
    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request, username=cd["username"], password=cd["password"]
            )
            if user is None:
                messages.error(request, "Неверный логин или пароль!")
                return render(request, "accounts/login.html", {"form": form})

            if not user.is_active:
                messages.error(request, "Аккаунт заблокирован!")
                return render(request, "accounts/login.html", {"form": form})

            login(request, user)
            return redirect(reverse("index"))

        return render(request, "accounts/login.html", {"form": form})

    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, "accounts/login.html", {"form": form})


class ApplicationView(View):
    def post(self, request, *args, **kwargs):
        form = ApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "accounts/application-sent-successfully.html")

        messages.error(request, "Неверно введены данные!")
        return render(request, "accounts/application.html", {"form": form})

    def get(self, request, *args, **kwargs):
        form = ApplicationForm()
        return render(request, "accounts/application.html", {"form": form})


class ProfileView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        user = request.user
        user_form = UserEditForm(instance=user, data=request.POST)
        profile_form = ProfileEditForm(instance=user.profile, data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            try:
                user = user_form.save(commit=False)
                user.username = user.email
                user.save()
            except IntegrityError:
                messages.error(request, "Такой email уже существует")
                return redirect(reverse("profile"))

            profile_form.save()
            messages.success(request, "Профиль успешно изменен")
            return redirect(reverse("profile"))

        messages.success(request, "Форма заполнена некорректно")
        return redirect(reverse("profile"))

    def get(self, request, *args, **kwargs):
        user = request.user
        user_form = UserEditForm(instance=user)
        profile_form = ProfileEditForm(instance=user.profile)
        return render(request, "accounts/profile.html", {"user_form": user_form, "profile_form": profile_form})

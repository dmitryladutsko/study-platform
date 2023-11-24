from django import forms
from django.contrib.auth.models import User
from .models import Application, Profile


class LoginForm(forms.Form):
    username = forms.CharField(label="Логин")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form__input'


class ApplicationForm(forms.ModelForm):

    class Meta:
        model = Application
        fields = ("email", "first_name", "last_name", "middle_name", "group_id")
        labels = {"email": "Email", "first_name": "Имя", "last_name": "Фамилия", "middle_name": "Отчество", "group_id": "Группа"}

    def __init__(self, *args, **kwargs):
        super(ApplicationForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form__input'


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        labels = {"first_name": "Имя", "last_name": "Фамилия", "email": "Email"}

    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form__input'


class UserCreateForm(UserEditForm):

    password = forms.CharField(max_length=64, label="Пароль")


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("middle_name",)
        labels = {"middle_name": "Отчество"}

    def __init__(self, *args, **kwargs):
        super(ProfileEditForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form__input'
